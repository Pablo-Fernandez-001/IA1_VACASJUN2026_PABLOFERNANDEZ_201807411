import json
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .config import get_settings
from .database import Base, engine, get_db
from .models import DiagnosisHistory
from .schemas import DiagnoseRequest, DiagnosisRecord
from .services.prolog_client import PrologClient
from .services.telegram_client import TelegramClient
from .services.formatters import build_telegram_text

settings = get_settings()
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Doctor Byte API Gateway",
    description="API principal que orquesta diagnóstico experto, historial y Telegram.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health():
    prolog_status = "unknown"
    try:
        prolog_status = (await PrologClient().health()).get("status", "ok")
    except Exception as exc:
        prolog_status = f"error: {exc}"
    return {"status": "ok", "service": "api-gateway", "prolog_service": prolog_status}

@app.get("/api/symptoms")
async def get_symptoms():
    try:
        return {"symptoms": await PrologClient().symptoms()}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"No se pudo obtener catálogo desde Prolog: {exc}")

@app.post("/api/diagnose", response_model=DiagnosisRecord)
async def diagnose(payload: DiagnoseRequest, db: Session = Depends(get_db)):
    try:
        result = await PrologClient().diagnose(payload.symptoms)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Error consultando motor Prolog: {exc}")

    diagnostics = result.get("diagnostics", [])
    top_diagnosis = diagnostics[0].get("name", "Sin diagnóstico concluyente") if diagnostics else "Sin diagnóstico concluyente"
    telegram_sent = "no"

    if payload.notify_telegram:
        try:
            text = build_telegram_text(payload.user_name, payload.symptoms, result)
            response = await TelegramClient().send_message(text=text, chat_id=payload.telegram_chat_id)
            telegram_sent = "yes" if response.get("sent") else "no_configurado"
        except Exception:
            telegram_sent = "error"

    record = DiagnosisHistory(
        user_name=payload.user_name,
        selected_symptoms=json.dumps(payload.symptoms, ensure_ascii=False),
        result_json=json.dumps(result, ensure_ascii=False),
        top_diagnosis=top_diagnosis,
        telegram_sent=telegram_sent,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return DiagnosisRecord(
        id=record.id,
        user_name=record.user_name,
        selected_symptoms=json.loads(record.selected_symptoms),
        result=json.loads(record.result_json),
        top_diagnosis=record.top_diagnosis,
        telegram_sent=record.telegram_sent,
        created_at=record.created_at,
    )

@app.get("/api/history", response_model=list[DiagnosisRecord])
def get_history(db: Session = Depends(get_db)):
    rows = db.query(DiagnosisHistory).order_by(DiagnosisHistory.created_at.desc()).limit(100).all()
    return [
        DiagnosisRecord(
            id=row.id,
            user_name=row.user_name,
            selected_symptoms=json.loads(row.selected_symptoms),
            result=json.loads(row.result_json),
            top_diagnosis=row.top_diagnosis,
            telegram_sent=row.telegram_sent,
            created_at=row.created_at,
        )
        for row in rows
    ]

@app.get("/api/history/{record_id}", response_model=DiagnosisRecord)
def get_history_item(record_id: int, db: Session = Depends(get_db)):
    row = db.get(DiagnosisHistory, record_id)
    if not row:
        raise HTTPException(status_code=404, detail="Diagnóstico no encontrado")
    return DiagnosisRecord(
        id=row.id,
        user_name=row.user_name,
        selected_symptoms=json.loads(row.selected_symptoms),
        result=json.loads(row.result_json),
        top_diagnosis=row.top_diagnosis,
        telegram_sent=row.telegram_sent,
        created_at=row.created_at,
    )

@app.delete("/api/history/{record_id}")
def delete_history_item(record_id: int, db: Session = Depends(get_db)):
    row = db.get(DiagnosisHistory, record_id)
    if not row:
        raise HTTPException(status_code=404, detail="Diagnóstico no encontrado")
    db.delete(row)
    db.commit()
    return {"deleted": True, "id": record_id}

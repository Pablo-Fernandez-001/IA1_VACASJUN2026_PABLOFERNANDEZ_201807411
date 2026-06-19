import json

import httpx
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .config import get_settings
from .database import Base, SessionLocal, engine, get_db
from .models import DiagnosisHistory, SystemConfig
from .schemas import DiagnoseRequest, DiagnosisRecord, SystemConfigPayload
from .services.formatters import build_telegram_text
from .services.prolog_client import PrologClient
from .services.telegram_client import TelegramClient

settings = get_settings()
Base.metadata.create_all(bind=engine)


def ensure_system_config(db: Session) -> SystemConfig:
    config = db.get(SystemConfig, 1)
    if config is None:
        config = SystemConfig(id=1)
        db.add(config)
        db.commit()
        db.refresh(config)
    return config


with SessionLocal() as startup_db:
    ensure_system_config(startup_db)


app = FastAPI(
    title="Doctor Byte API Gateway",
    description="Orquesta el motor Prolog, historial SQLite, configuracion y Telegram.",
    version="2.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def proxy_error(action: str, exc: Exception) -> HTTPException:
    if isinstance(exc, httpx.HTTPStatusError):
        try:
            detail = exc.response.json().get("detail", exc.response.text)
        except ValueError:
            detail = exc.response.text
        return HTTPException(status_code=exc.response.status_code, detail=detail)
    return HTTPException(status_code=502, detail=f"{action}: {exc}")


@app.get("/api/health", tags=["system"])
async def health():
    try:
        prolog = await PrologClient().health()
    except Exception as exc:
        return {"status": "degraded", "service": "api-gateway", "prolog_service": str(exc)}
    return {"status": "ok", "service": "api-gateway", "prolog_service": prolog}


@app.get("/api/knowledge", tags=["knowledge"])
async def get_knowledge():
    try:
        return await PrologClient().knowledge()
    except Exception as exc:
        raise proxy_error("No se pudo leer el conocimiento Prolog", exc)


@app.get("/api/symptoms", tags=["symptoms"])
async def get_symptoms():
    try:
        return {"symptoms": await PrologClient().symptoms()}
    except Exception as exc:
        raise proxy_error("No se pudo obtener el catalogo", exc)


@app.post("/api/symptoms", tags=["symptoms"])
async def create_symptom(payload: dict):
    try:
        return await PrologClient().create_symptom(payload)
    except Exception as exc:
        raise proxy_error("No se pudo crear el sintoma", exc)


@app.put("/api/symptoms/{item_id}", tags=["symptoms"])
async def update_symptom(item_id: str, payload: dict):
    try:
        return await PrologClient().update_symptom(item_id, payload)
    except Exception as exc:
        raise proxy_error("No se pudo actualizar el sintoma", exc)


@app.delete("/api/symptoms/{item_id}", tags=["symptoms"])
async def delete_symptom(item_id: str):
    try:
        return await PrologClient().delete_symptom(item_id)
    except Exception as exc:
        raise proxy_error("No se pudo eliminar el sintoma", exc)


@app.get("/api/failures", tags=["failures"])
async def get_failures():
    try:
        return {"failures": await PrologClient().failures()}
    except Exception as exc:
        raise proxy_error("No se pudieron obtener las fallas", exc)


@app.post("/api/failures", tags=["failures"])
async def create_failure(payload: dict):
    try:
        return await PrologClient().create_failure(payload)
    except Exception as exc:
        raise proxy_error("No se pudo crear la falla", exc)


@app.put("/api/failures/{item_id}", tags=["failures"])
async def update_failure(item_id: str, payload: dict):
    try:
        return await PrologClient().update_failure(item_id, payload)
    except Exception as exc:
        raise proxy_error("No se pudo actualizar la falla", exc)


@app.delete("/api/failures/{item_id}", tags=["failures"])
async def delete_failure(item_id: str):
    try:
        return await PrologClient().delete_failure(item_id)
    except Exception as exc:
        raise proxy_error("No se pudo eliminar la falla", exc)


@app.get("/api/recommendations", tags=["recommendations"])
async def get_recommendations():
    try:
        return {"recommendations": await PrologClient().recommendations()}
    except Exception as exc:
        raise proxy_error("No se pudieron obtener las recomendaciones", exc)


@app.post("/api/recommendations", tags=["recommendations"])
async def create_recommendation(payload: dict):
    try:
        return await PrologClient().create_recommendation(payload)
    except Exception as exc:
        raise proxy_error("No se pudo crear la recomendacion", exc)


@app.put("/api/recommendations/{item_id}", tags=["recommendations"])
async def update_recommendation(item_id: str, payload: dict):
    try:
        return await PrologClient().update_recommendation(item_id, payload)
    except Exception as exc:
        raise proxy_error("No se pudo actualizar la recomendacion", exc)


@app.delete("/api/recommendations/{item_id}", tags=["recommendations"])
async def delete_recommendation(item_id: str):
    try:
        return await PrologClient().delete_recommendation(item_id)
    except Exception as exc:
        raise proxy_error("No se pudo eliminar la recomendacion", exc)


@app.get("/api/diagnosis-rules", tags=["rules"])
async def get_diagnosis_rules():
    try:
        return {"diagnosis_rules": await PrologClient().diagnosis_rules()}
    except Exception as exc:
        raise proxy_error("No se pudieron obtener las reglas", exc)


@app.post("/api/diagnosis-rules", tags=["rules"])
async def create_diagnosis_rule(payload: dict):
    try:
        return await PrologClient().create_diagnosis_rule(payload)
    except Exception as exc:
        raise proxy_error("No se pudo crear la regla", exc)


@app.put("/api/diagnosis-rules/{item_id}", tags=["rules"])
async def update_diagnosis_rule(item_id: str, payload: dict):
    try:
        return await PrologClient().update_diagnosis_rule(item_id, payload)
    except Exception as exc:
        raise proxy_error("No se pudo actualizar la regla", exc)


@app.delete("/api/diagnosis-rules/{item_id}", tags=["rules"])
async def delete_diagnosis_rule(item_id: str):
    try:
        return await PrologClient().delete_diagnosis_rule(item_id)
    except Exception as exc:
        raise proxy_error("No se pudo eliminar la regla", exc)


@app.get("/api/config", tags=["configuration"])
def get_config(db: Session = Depends(get_db)):
    return ensure_system_config(db)


@app.put("/api/config", tags=["configuration"])
def update_config(payload: SystemConfigPayload, db: Session = Depends(get_db)):
    config = ensure_system_config(db)
    for key, value in payload.model_dump().items():
        setattr(config, key, value)
    db.commit()
    db.refresh(config)
    return config


@app.post("/api/diagnose", response_model=DiagnosisRecord, tags=["diagnosis"])
async def diagnose(payload: DiagnoseRequest, db: Session = Depends(get_db)):
    try:
        available = {item["id"] for item in await PrologClient().symptoms()}
        unknown = sorted(set(payload.symptoms) - available)
        if unknown:
            raise HTTPException(status_code=422, detail={"unknown_symptoms": unknown})
        result = await PrologClient().diagnose(payload.symptoms)
    except HTTPException:
        raise
    except Exception as exc:
        raise proxy_error("Error consultando el motor Prolog", exc)

    diagnostics = result.get("diagnostics", [])
    top = diagnostics[0] if diagnostics else None
    top_diagnosis = top.get("name", "Sin diagnostico concluyente") if top else "Sin diagnostico concluyente"
    telegram_sent = "no"
    config = ensure_system_config(db)

    if payload.notify_telegram:
        if not config.bot_active:
            telegram_sent = "bot_inactivo"
        else:
            try:
                chat_id = payload.telegram_chat_id or config.bot_id or settings.telegram_default_chat_id or None
                text = build_telegram_text(payload.user_name, payload.symptoms, result)
                response = await TelegramClient().send_message(
                    text=text,
                    chat_id=chat_id,
                )
                telegram_sent = "yes" if response.get("sent") else "no_configurado"
            except Exception:
                telegram_sent = "error"

    record = DiagnosisHistory(
        user_name=payload.user_name.strip() or "Usuario",
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


@app.get("/api/history", response_model=list[DiagnosisRecord], tags=["history"])
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


@app.get("/api/history/{record_id}", response_model=DiagnosisRecord, tags=["history"])
def get_history_item(record_id: int, db: Session = Depends(get_db)):
    row = db.get(DiagnosisHistory, record_id)
    if not row:
        raise HTTPException(status_code=404, detail="Diagnostico no encontrado")
    return DiagnosisRecord(
        id=row.id,
        user_name=row.user_name,
        selected_symptoms=json.loads(row.selected_symptoms),
        result=json.loads(row.result_json),
        top_diagnosis=row.top_diagnosis,
        telegram_sent=row.telegram_sent,
        created_at=row.created_at,
    )


@app.delete("/api/history/{record_id}", tags=["history"])
def delete_history_item(record_id: int, db: Session = Depends(get_db)):
    row = db.get(DiagnosisHistory, record_id)
    if not row:
        raise HTTPException(status_code=404, detail="Diagnostico no encontrado")
    db.delete(row)
    db.commit()
    return {"deleted": True, "id": record_id}

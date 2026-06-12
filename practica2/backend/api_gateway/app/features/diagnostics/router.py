import json
import re
import unicodedata
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.core.security import get_current_admin
from app.db.models import Diagnosis, DiagnosticRule, QueryLog, RuleSymptom, Symptom
from app.db.session import get_db
from app.services.prolog_client import run_diagnosis

router = APIRouter(prefix="/api/diagnostics", tags=["diagnostics"])

class SymptomIn(BaseModel):
    code: str
    name: str
    description: str = ""
    category: str = "General"
    severity: float = 1.0
    is_active: bool = True

class DiagnosisIn(BaseModel):
    code: str
    name: str
    category: str = "General"
    message: str
    solution_route: list[str] = Field(default_factory=list)
    base_probability: float = 100.0
    is_active: bool = True

class RuleIn(BaseModel):
    name: str
    diagnosis_id: int
    weight: float = 100.0
    explanation: str = ""
    is_active: bool = True
    symptom_ids: list[int] = Field(default_factory=list)

class DiagnoseRequest(BaseModel):
    symptom_codes: list[str]
    telegram_user: str = "panel"

class CustomSymptomIn(BaseModel):
    name: str
    telegram_user: str = "telegram"
    selected_codes: list[str] = Field(default_factory=list)

def build_custom_code(name: str, db: Session) -> str:
    normalized = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    base = re.sub(r"[^a-zA-Z0-9]+", "_", normalized.lower()).strip("_") or "otro_sintoma"
    base = f"custom_{base[:70]}".strip("_")
    candidate = base
    counter = 2
    while db.query(Symptom).filter_by(code=candidate).first():
        candidate = f"{base[:78]}_{counter}"
        counter += 1
    return candidate

@router.get("/symptoms")
def list_symptoms(db: Session = Depends(get_db)):
    return db.query(Symptom).order_by(Symptom.name).all()

@router.post("/custom-symptoms")
def create_custom_symptom(payload: CustomSymptomIn, db: Session = Depends(get_db)):
    clean_name = " ".join(payload.name.strip().split())
    if len(clean_name) < 3:
        raise HTTPException(400, "El sintoma debe tener al menos 3 caracteres")
    if len(clean_name) > 150:
        clean_name = clean_name[:150]

    obj = db.query(Symptom).filter(func.lower(Symptom.name) == clean_name.lower()).first()
    created = False
    if not obj:
        obj = Symptom(
            code=build_custom_code(clean_name, db),
            name=clean_name,
            description="Sintoma agregado desde Telegram con el boton Otro.",
            category="Personalizado",
            severity=1.0,
            is_active=True,
        )
        db.add(obj)
        db.flush()
        created = True

    selected_codes = list(dict.fromkeys([*payload.selected_codes, obj.code]))
    action = "agregado" if created else "ya existia"
    db.add(QueryLog(
        telegram_user=payload.telegram_user,
        query_text=clean_name,
        response_text=f"Sintoma personalizado {action}: {obj.code}",
        matched_type="custom_symptom",
        category="Personalizado",
    ))
    db.commit()
    db.refresh(obj)
    return {
        "id": obj.id,
        "code": obj.code,
        "name": obj.name,
        "category": obj.category,
        "created": created,
        "selected_codes": selected_codes,
    }

@router.post("/symptoms", dependencies=[Depends(get_current_admin)])
def create_symptom(payload: SymptomIn, db: Session = Depends(get_db)):
    obj = Symptom(**payload.model_dump())
    db.add(obj); db.commit(); db.refresh(obj); return obj

@router.put("/symptoms/{symptom_id}", dependencies=[Depends(get_current_admin)])
def update_symptom(symptom_id: int, payload: SymptomIn, db: Session = Depends(get_db)):
    obj = db.get(Symptom, symptom_id)
    if not obj: raise HTTPException(404, "Síntoma no encontrado")
    for k,v in payload.model_dump().items(): setattr(obj,k,v)
    db.commit(); db.refresh(obj); return obj

@router.delete("/symptoms/{symptom_id}", dependencies=[Depends(get_current_admin)])
def delete_symptom(symptom_id: int, db: Session = Depends(get_db)):
    obj = db.get(Symptom, symptom_id)
    if not obj: raise HTTPException(404, "Síntoma no encontrado")
    db.delete(obj); db.commit(); return {"ok": True}

@router.get("/diagnoses")
def list_diagnoses(db: Session = Depends(get_db)):
    items = db.query(Diagnosis).order_by(Diagnosis.name).all()
    return [{**{c.name: getattr(d, c.name) for c in d.__table__.columns}, "solution_route": json.loads(d.solution_route or "[]")} for d in items]

@router.post("/diagnoses", dependencies=[Depends(get_current_admin)])
def create_diagnosis(payload: DiagnosisIn, db: Session = Depends(get_db)):
    data = payload.model_dump(); data["solution_route"] = json.dumps(data["solution_route"], ensure_ascii=False)
    obj = Diagnosis(**data)
    db.add(obj); db.commit(); db.refresh(obj); return obj

@router.put("/diagnoses/{diagnosis_id}", dependencies=[Depends(get_current_admin)])
def update_diagnosis(diagnosis_id: int, payload: DiagnosisIn, db: Session = Depends(get_db)):
    obj = db.get(Diagnosis, diagnosis_id)
    if not obj: raise HTTPException(404, "Diagnóstico no encontrado")
    data = payload.model_dump(); data["solution_route"] = json.dumps(data["solution_route"], ensure_ascii=False)
    for k,v in data.items(): setattr(obj,k,v)
    db.commit(); db.refresh(obj); return obj

@router.delete("/diagnoses/{diagnosis_id}", dependencies=[Depends(get_current_admin)])
def delete_diagnosis(diagnosis_id: int, db: Session = Depends(get_db)):
    obj = db.get(Diagnosis, diagnosis_id)
    if not obj: raise HTTPException(404, "Diagnóstico no encontrado")
    db.delete(obj); db.commit(); return {"ok": True}

@router.get("/rules")
def list_rules(db: Session = Depends(get_db)):
    rules = db.query(DiagnosticRule).order_by(DiagnosticRule.id).all()
    result=[]
    for r in rules:
        result.append({"id": r.id, "name": r.name, "diagnosis_id": r.diagnosis_id, "weight": r.weight, "explanation": r.explanation, "is_active": r.is_active, "symptom_ids": [rs.symptom_id for rs in r.symptoms]})
    return result

@router.post("/rules", dependencies=[Depends(get_current_admin)])
def create_rule(payload: RuleIn, db: Session = Depends(get_db)):
    data = payload.model_dump(); symptom_ids = data.pop("symptom_ids")
    obj = DiagnosticRule(**data); db.add(obj); db.flush()
    for sid in symptom_ids: db.add(RuleSymptom(rule_id=obj.id, symptom_id=sid))
    db.commit(); db.refresh(obj); return obj

@router.put("/rules/{rule_id}", dependencies=[Depends(get_current_admin)])
def update_rule(rule_id: int, payload: RuleIn, db: Session = Depends(get_db)):
    obj = db.get(DiagnosticRule, rule_id)
    if not obj: raise HTTPException(404, "Regla no encontrada")
    data = payload.model_dump(); symptom_ids = data.pop("symptom_ids")
    for k,v in data.items(): setattr(obj,k,v)
    db.query(RuleSymptom).filter_by(rule_id=rule_id).delete()
    for sid in symptom_ids: db.add(RuleSymptom(rule_id=rule_id, symptom_id=sid))
    db.commit(); db.refresh(obj); return obj

@router.delete("/rules/{rule_id}", dependencies=[Depends(get_current_admin)])
def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    obj = db.get(DiagnosticRule, rule_id)
    if not obj: raise HTTPException(404, "Regla no encontrada")
    db.delete(obj); db.commit(); return {"ok": True}

@router.post("/diagnose")
def diagnose(payload: DiagnoseRequest, db: Session = Depends(get_db)):
    symptoms = db.query(Symptom).filter(Symptom.is_active == True).all()
    diagnoses = db.query(Diagnosis).filter(Diagnosis.is_active == True).all()
    rules = db.query(DiagnosticRule).filter(DiagnosticRule.is_active == True).all()
    symptom_map = {s.id: s for s in symptoms}
    diagnosis_map = {d.id: d for d in diagnoses}
    prolog_payload = {
        "selected_symptoms": payload.symptom_codes,
        "diagnoses": [{"id": d.code, "name": d.name, "category": d.category, "message": d.message, "solution_route": json.loads(d.solution_route or "[]"), "base_probability": d.base_probability} for d in diagnoses],
        "rules": []
    }
    for r in rules:
        diag = diagnosis_map.get(r.diagnosis_id)
        if not diag: continue
        prolog_payload["rules"].append({
            "id": f"rule_{r.id}", "name": r.name, "diagnosis_id": diag.code,
            "weight": r.weight, "explanation": r.explanation,
            "symptoms": [symptom_map[rs.symptom_id].code for rs in r.symptoms if rs.symptom_id in symptom_map]
        })
    try:
        result = run_diagnosis(prolog_payload)
    except Exception as exc:
        raise HTTPException(502, f"No se pudo consultar Prolog: {exc}")
    response_text = "; ".join([f"{d['name']} {d['probability']}%" for d in result.get("diagnostics", [])]) or "Sin diagnóstico posible"
    db.add(QueryLog(telegram_user=payload.telegram_user, query_text=",".join(payload.symptom_codes), response_text=response_text, matched_type="diagnosis", category="diagnóstico"))
    db.commit()
    return result

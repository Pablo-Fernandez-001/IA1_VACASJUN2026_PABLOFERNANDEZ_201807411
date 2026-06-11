import json
import shutil
import subprocess
from pathlib import Path
from threading import Lock

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parents[1]
KB_PATH = BASE_DIR / "knowledge_base" / "doctor_byte.pl"
DATA_PATH = BASE_DIR / "knowledge_base" / "doctor_byte_data.json"
DATA_LOCK = Lock()

app = FastAPI(
    title="Doctor Byte Prolog Service",
    description="Microservicio que encapsula SWI-Prolog y expone diagnostico experto por REST.",
    version="1.1.0",
)


class DiagnoseRequest(BaseModel):
    symptoms: list[str] = Field(min_length=1)


class SymptomPayload(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    category: str = Field(min_length=1)
    weight: int = Field(ge=1, le=5)


class DiagnosisRulePayload(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    message: str = ""
    category: str = Field(min_length=1)
    severity: str = "media"
    enabled: bool = True
    min_score: int = Field(default=0, ge=0, le=100)
    required_symptoms: list[str] = Field(default_factory=list)
    support_symptoms: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    solution_steps: list[str] = Field(default_factory=list)


def read_knowledge() -> dict:
    with DATA_LOCK:
        with DATA_PATH.open("r", encoding="utf-8") as file:
            return json.load(file)


def write_knowledge(data: dict) -> dict:
    with DATA_LOCK:
        with DATA_PATH.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
            file.write("\n")
    return data


def replace_symptom_reference(rules: list[dict], old_id: str, new_id: str) -> None:
    for rule in rules:
        for field in ("required_symptoms", "support_symptoms"):
            rule[field] = [new_id if symptom == old_id else symptom for symptom in rule.get(field, [])]


def remove_symptom_reference(rules: list[dict], symptom_id: str) -> None:
    for rule in rules:
        for field in ("required_symptoms", "support_symptoms"):
            rule[field] = [symptom for symptom in rule.get(field, []) if symptom != symptom_id]


def run_prolog(payload: dict) -> dict:
    if not shutil.which("swipl"):
        raise HTTPException(status_code=500, detail="SWI-Prolog no esta instalado o no esta en PATH")

    payload = {**payload, "knowledge_path": str(DATA_PATH)}
    try:
        completed = subprocess.run(
            ["swipl", "-q", "-s", str(KB_PATH), "-g", "doctor_byte_cli"],
            input=json.dumps(payload, ensure_ascii=False),
            text=True,
            encoding="utf-8",
            capture_output=True,
            timeout=10,
            check=False,
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Prolog tardo demasiado en responder")

    if completed.returncode != 0:
        raise HTTPException(status_code=500, detail={"stderr": completed.stderr, "stdout": completed.stdout})
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail=f"Respuesta Prolog no es JSON valido: {exc}; stdout={completed.stdout}")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "prolog-service",
        "swipl_available": bool(shutil.which("swipl")),
        "knowledge_path": str(DATA_PATH),
    }


@app.get("/knowledge")
def get_knowledge():
    return read_knowledge()


@app.put("/knowledge")
def replace_knowledge(payload: dict):
    if "symptoms" not in payload or "diagnosis_rules" not in payload:
        raise HTTPException(status_code=400, detail="La base debe incluir symptoms y diagnosis_rules")
    return write_knowledge(payload)


@app.get("/symptoms")
def symptoms():
    return run_prolog({"mode": "symptoms"})


@app.post("/symptoms")
def create_symptom(payload: SymptomPayload):
    data = read_knowledge()
    if any(symptom["id"] == payload.id for symptom in data["symptoms"]):
        raise HTTPException(status_code=409, detail="Ya existe un sintoma con ese id")
    data["symptoms"].append(payload.model_dump())
    return write_knowledge(data)["symptoms"][-1]


@app.put("/symptoms/{symptom_id}")
def update_symptom(symptom_id: str, payload: SymptomPayload):
    data = read_knowledge()
    symptoms = data["symptoms"]
    index = next((i for i, symptom in enumerate(symptoms) if symptom["id"] == symptom_id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Sintoma no encontrado")
    if payload.id != symptom_id and any(symptom["id"] == payload.id for symptom in symptoms):
        raise HTTPException(status_code=409, detail="Ya existe un sintoma con el nuevo id")
    symptoms[index] = payload.model_dump()
    if payload.id != symptom_id:
        replace_symptom_reference(data["diagnosis_rules"], symptom_id, payload.id)
    write_knowledge(data)
    return symptoms[index]


@app.delete("/symptoms/{symptom_id}")
def delete_symptom(symptom_id: str):
    data = read_knowledge()
    original_count = len(data["symptoms"])
    data["symptoms"] = [symptom for symptom in data["symptoms"] if symptom["id"] != symptom_id]
    if len(data["symptoms"]) == original_count:
        raise HTTPException(status_code=404, detail="Sintoma no encontrado")
    remove_symptom_reference(data["diagnosis_rules"], symptom_id)
    write_knowledge(data)
    return {"deleted": True, "id": symptom_id}


@app.get("/diagnosis-rules")
def diagnosis_rules():
    return run_prolog({"mode": "rules"})


@app.post("/diagnosis-rules")
def create_diagnosis_rule(payload: DiagnosisRulePayload):
    data = read_knowledge()
    if any(rule["id"] == payload.id for rule in data["diagnosis_rules"]):
        raise HTTPException(status_code=409, detail="Ya existe una regla con ese id")
    data["diagnosis_rules"].append(payload.model_dump())
    return write_knowledge(data)["diagnosis_rules"][-1]


@app.put("/diagnosis-rules/{rule_id}")
def update_diagnosis_rule(rule_id: str, payload: DiagnosisRulePayload):
    data = read_knowledge()
    rules = data["diagnosis_rules"]
    index = next((i for i, rule in enumerate(rules) if rule["id"] == rule_id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Regla no encontrada")
    if payload.id != rule_id and any(rule["id"] == payload.id for rule in rules):
        raise HTTPException(status_code=409, detail="Ya existe una regla con el nuevo id")
    rules[index] = payload.model_dump()
    write_knowledge(data)
    return rules[index]


@app.delete("/diagnosis-rules/{rule_id}")
def delete_diagnosis_rule(rule_id: str):
    data = read_knowledge()
    original_count = len(data["diagnosis_rules"])
    data["diagnosis_rules"] = [rule for rule in data["diagnosis_rules"] if rule["id"] != rule_id]
    if len(data["diagnosis_rules"]) == original_count:
        raise HTTPException(status_code=404, detail="Regla no encontrada")
    write_knowledge(data)
    return {"deleted": True, "id": rule_id}


@app.post("/diagnose")
def diagnose(payload: DiagnoseRequest):
    return run_prolog({"mode": "diagnose", "symptoms": payload.symptoms})

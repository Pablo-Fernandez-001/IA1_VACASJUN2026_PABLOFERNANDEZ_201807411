import json
import re
import subprocess
import tempfile
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "prolog" / "expert_engine.pl"

app = FastAPI(title="SmartBot Prolog Service", version="1.0.0")

class DiagnosisIn(BaseModel):
    id: str
    name: str
    category: str
    message: str
    solution_route: list[str] = Field(default_factory=list)
    base_probability: float = 100.0

class RuleIn(BaseModel):
    id: str
    name: str
    diagnosis_id: str
    weight: float = 100.0
    explanation: str = ""
    symptoms: list[str] = Field(default_factory=list)

class PrologRequest(BaseModel):
    selected_symptoms: list[str]
    diagnoses: list[DiagnosisIn]
    rules: list[RuleIn]

def atom(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_]", "_", value.strip().lower())
    if not cleaned:
        cleaned = "vacio"
    if cleaned[0].isdigit():
        cleaned = "a_" + cleaned
    return cleaned

def q(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)

def prolog_list(items):
    return "[" + ",".join(q(str(x)) for x in items) + "]"

def build_program(payload: PrologRequest) -> str:
    lines = [f":- consult('{ENGINE.as_posix()}')."]
    for s in payload.selected_symptoms:
        lines.append(f"selected({atom(s)}).")
    for d in payload.diagnoses:
        lines.append(f"diagnosis({atom(d.id)}, {q(d.name)}, {q(d.category)}, {q(d.message)}, {prolog_list(d.solution_route)}, {float(d.base_probability)}).")
    for r in payload.rules:
        lines.append(f"rule({atom(r.id)}, {atom(r.diagnosis_id)}, {q(r.name)}, {float(r.weight)}, {q(r.explanation)}).")
        for s in r.symptoms:
            lines.append(f"required_symptom({atom(r.id)}, {atom(s)}).")
    lines.append(":- initialization(main, main).")
    return "\n".join(lines)

@app.get("/health")
def health():
    return {"status": "ok", "service": "prolog-service", "engine": str(ENGINE)}

@app.post("/api/prolog/diagnose")
def diagnose(payload: PrologRequest):
    program = build_program(payload)
    with tempfile.NamedTemporaryFile("w", suffix=".pl", delete=False, encoding="utf-8") as tmp:
        tmp.write(program)
        tmp_path = tmp.name
    try:
        proc = subprocess.run(["swipl", "-q", "-s", tmp_path], capture_output=True, text=True, timeout=15)
    except FileNotFoundError:
        raise HTTPException(500, "SWI-Prolog no está instalado o no existe el comando swipl")
    except subprocess.TimeoutExpired:
        raise HTTPException(500, "La consulta Prolog excedió el tiempo máximo")
    finally:
        Path(tmp_path).unlink(missing_ok=True)
    if proc.returncode != 0:
        raise HTTPException(500, {"error": proc.stderr, "program": program})
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        raise HTTPException(500, {"error": "Prolog no devolvió JSON válido", "stdout": proc.stdout, "stderr": proc.stderr})
    diagnostics = sorted(data.get("diagnostics", []), key=lambda d: d.get("probability", 0), reverse=True)
    return {"diagnostics": diagnostics, "count": len(diagnostics)}

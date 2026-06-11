import json
import shutil
import subprocess
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parents[1]
KB_PATH = BASE_DIR / "knowledge_base" / "doctor_byte.pl"

app = FastAPI(
    title="Doctor Byte Prolog Service",
    description="Microservicio que encapsula SWI-Prolog y expone diagnóstico experto por REST.",
    version="1.0.0",
)

class DiagnoseRequest(BaseModel):
    symptoms: list[str] = Field(min_length=1)


def run_prolog(payload: dict) -> dict:
    if not shutil.which("swipl"):
        raise HTTPException(status_code=500, detail="SWI-Prolog no está instalado o no está en PATH")
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
        raise HTTPException(status_code=504, detail="Prolog tardó demasiado en responder")

    if completed.returncode != 0:
        raise HTTPException(status_code=500, detail={"stderr": completed.stderr, "stdout": completed.stdout})
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail=f"Respuesta Prolog no es JSON válido: {exc}; stdout={completed.stdout}")

@app.get("/health")
def health():
    return {"status": "ok", "service": "prolog-service", "swipl_available": bool(shutil.which("swipl"))}

@app.get("/symptoms")
def symptoms():
    return run_prolog({"mode": "symptoms"})

@app.post("/diagnose")
def diagnose(payload: DiagnoseRequest):
    return run_prolog({"mode": "diagnose", "symptoms": payload.symptoms})

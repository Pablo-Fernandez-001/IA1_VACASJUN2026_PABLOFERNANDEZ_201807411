import json
import shutil
import subprocess
from pathlib import Path
from threading import Lock
from typing import Callable

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parents[1]
ENGINE_PATH = BASE_DIR / "knowledge_base" / "doctor_byte.pl"
KNOWLEDGE_PATH = BASE_DIR / "knowledge_base" / "doctor_byte_knowledge.pl"
PROLOG_LOCK = Lock()

app = FastAPI(
    title="Doctor Byte Prolog Service",
    description="CRUD e inferencia sobre hechos y reglas persistidos en SWI-Prolog.",
    version="2.0.0",
)


class DiagnoseRequest(BaseModel):
    symptoms: list[str] = Field(min_length=1)


class SymptomPayload(BaseModel):
    id: str = Field(min_length=1, pattern=r"^[a-z][a-z0-9_]*$")
    name: str = Field(min_length=2)
    category: str = Field(min_length=2)
    weight: int = Field(ge=1, le=5)


class FailurePayload(BaseModel):
    id: str = Field(min_length=1, pattern=r"^[a-z][a-z0-9_]*$")
    name: str = Field(min_length=2)
    category: str = Field(min_length=2)
    severity: str = Field(pattern=r"^(baja|media|alta|critica)$")
    message: str = Field(min_length=2)
    solution_steps: list[str] = Field(default_factory=list)


class RecommendationPayload(BaseModel):
    id: str = Field(min_length=1, pattern=r"^[a-z][a-z0-9_]*$")
    failure_id: str = Field(min_length=1)
    text: str = Field(min_length=2)
    order: int = Field(default=1, ge=1, le=100)


class DiagnosisRulePayload(BaseModel):
    id: str = Field(min_length=1, pattern=r"^[a-z][a-z0-9_]*$")
    failure_id: str = Field(min_length=1)
    required_symptoms: list[str] = Field(default_factory=list)
    support_symptoms: list[str] = Field(default_factory=list)
    min_score: int = Field(default=20, ge=0, le=100)
    enabled: bool = True


def run_prolog(payload: dict) -> dict:
    if not shutil.which("swipl"):
        raise HTTPException(status_code=503, detail="SWI-Prolog no esta instalado o no esta en PATH")

    command_payload = {**payload, "knowledge_path": str(KNOWLEDGE_PATH)}
    try:
        with PROLOG_LOCK:
            completed = subprocess.run(
                ["swipl", "-q", "-s", str(ENGINE_PATH), "-g", "doctor_byte_cli"],
                input=json.dumps(command_payload, ensure_ascii=False),
                text=True,
                encoding="utf-8",
                capture_output=True,
                timeout=15,
                check=False,
            )
    except subprocess.TimeoutExpired as exc:
        raise HTTPException(status_code=504, detail="Prolog tardo demasiado en responder") from exc

    if completed.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail={"message": "SWI-Prolog finalizo con error", "stderr": completed.stderr[-2000:]},
        )
    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail=f"Respuesta Prolog invalida: {completed.stdout[-1000:]}") from exc
    if result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])
    return result


def entity_crud(mode: str, entity: BaseModel | None = None, target_id: str | None = None) -> dict:
    payload: dict = {"mode": mode}
    if entity is not None:
        payload["entity"] = entity.model_dump()
    if target_id is not None:
        payload["target_id"] = target_id
    return run_prolog(payload)


def register_crud(
    path: str,
    list_mode: str,
    response_key: str,
    model: type[BaseModel],
    mode_name: str,
) -> None:
    async def list_items():
        return run_prolog({"mode": list_mode})

    async def create_item(payload: model):
        return entity_crud(f"create_{mode_name}", payload)

    async def update_item(item_id: str, payload: model):
        return entity_crud(f"update_{mode_name}", payload, item_id)

    async def delete_item(item_id: str):
        return entity_crud(f"delete_{mode_name}", target_id=item_id)

    list_items.__name__ = f"list_{response_key}"
    create_item.__name__ = f"create_{mode_name}"
    update_item.__name__ = f"update_{mode_name}"
    delete_item.__name__ = f"delete_{mode_name}"
    app.add_api_route(path, list_items, methods=["GET"], tags=[response_key])
    app.add_api_route(path, create_item, methods=["POST"], tags=[response_key])
    app.add_api_route(f"{path}/{{item_id}}", update_item, methods=["PUT"], tags=[response_key])
    app.add_api_route(f"{path}/{{item_id}}", delete_item, methods=["DELETE"], tags=[response_key])


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "prolog-service",
        "swipl_available": bool(shutil.which("swipl")),
        "knowledge_path": str(KNOWLEDGE_PATH),
        "knowledge_format": "Prolog facts",
    }


@app.get("/knowledge")
def get_knowledge():
    return run_prolog({"mode": "knowledge"})


@app.post("/diagnose")
def diagnose(payload: DiagnoseRequest):
    return run_prolog({"mode": "diagnose", "symptoms": payload.symptoms})


register_crud("/symptoms", "symptoms", "symptoms", SymptomPayload, "symptom")
register_crud("/failures", "failures", "failures", FailurePayload, "failure")
register_crud(
    "/recommendations",
    "recommendations",
    "recommendations",
    RecommendationPayload,
    "recommendation",
)
register_crud("/diagnosis-rules", "rules", "diagnosis_rules", DiagnosisRulePayload, "rule")

import json
import shutil
import subprocess
from pathlib import Path
from threading import Lock

from fastapi import HTTPException

from app.core.config import settings

PROLOG_LOCK = Lock()


def warehouse_path() -> Path:
    configured = Path(settings.prolog_path)
    if configured.is_absolute():
        return configured
    project_root = Path(__file__).resolve().parents[3]
    return (project_root / configured).resolve()


def next_action(state: dict, robot_id: str = "r1") -> dict:
    if not shutil.which("swipl"):
        raise HTTPException(status_code=503, detail="SWI-Prolog no esta instalado o no esta en PATH")
    payload = {
        "robot_id": robot_id,
        "map": state["map"],
        "robots": state["robots"],
        "packages": state["packages"],
        "zones": state["zones"],
        "obstacles": state["obstacles"],
    }
    try:
        with PROLOG_LOCK:
            completed = subprocess.run(
                ["swipl", "-q", "-s", str(warehouse_path()), "-g", "warehouse_cli"],
                input=json.dumps(payload),
                text=True,
                encoding="utf-8",
                capture_output=True,
                timeout=8,
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
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail=f"Respuesta Prolog invalida: {completed.stdout}") from exc

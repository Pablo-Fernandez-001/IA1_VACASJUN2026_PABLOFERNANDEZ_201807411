import json
from collections import Counter
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.entities import Simulation, SimulationCheckpoint, SimulationScenario, SimulationStep
from app.schemas.scenario import ScenarioApply, ScenarioCreate, ScenarioUpdate
from app.services import scenario_service, simulation_service
from app.services.report_service import build_analytics_pdf

router = APIRouter(prefix="/api", tags=["simulation"])


class SimulationSpeedUpdate(BaseModel):
    speed: str


@router.get("/simulation/state")
def state():
    return simulation_service.current_state()


@router.put("/simulation/configuration")
def configure(payload: ScenarioApply):
    return simulation_service.activate_configuration(
        payload.configuration.model_dump(),
        scenario_name="Escenario sin guardar",
        dirty=True,
    )


@router.post("/simulation/start")
def start(db: Session = Depends(get_db)):
    return simulation_service.start(db)


@router.post("/simulation/pause")
def pause(db: Session = Depends(get_db)):
    return simulation_service.pause(db)


@router.post("/simulation/reset")
def reset(db: Session = Depends(get_db)):
    return simulation_service.reset(db)


@router.post("/simulation/step")
def step(db: Session = Depends(get_db)):
    return simulation_service.step(db)


@router.post("/simulation/auto")
def auto(max_steps: int = 25, db: Session = Depends(get_db)):
    return simulation_service.auto(db, max_steps)


@router.put("/simulation/speed")
def update_speed(payload: SimulationSpeedUpdate):
    return simulation_service.set_speed(payload.speed)


@router.get("/robots")
def robots():
    return simulation_service.current_state()["robots"]


@router.get("/packages")
def packages():
    return simulation_service.current_state()["packages"]


@router.get("/obstacles")
def obstacles():
    return simulation_service.current_state()["obstacles"]


@router.get("/zones")
def zones():
    return simulation_service.current_state()["zones"]


@router.get("/metrics")
def metrics():
    return simulation_service.metrics()


@router.get("/scenarios")
def scenarios(db: Session = Depends(get_db)):
    return scenario_service.list_scenarios(db)


@router.get("/scenarios/{scenario_id}")
def scenario(scenario_id: int, db: Session = Depends(get_db)):
    return scenario_service.scenario_to_dict(scenario_service.get_scenario(db, scenario_id))


@router.post("/scenarios", status_code=status.HTTP_201_CREATED)
def create_scenario(payload: ScenarioCreate, db: Session = Depends(get_db)):
    created = scenario_service.create_scenario(db, payload.name, payload.configuration)
    return scenario_service.scenario_to_dict(created)


@router.put("/scenarios/{scenario_id}")
def update_scenario(scenario_id: int, payload: ScenarioUpdate, db: Session = Depends(get_db)):
    updated = scenario_service.update_scenario(db, scenario_id, payload.name, payload.configuration)
    return scenario_service.scenario_to_dict(updated)


@router.delete("/scenarios/{scenario_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scenario(scenario_id: int, db: Session = Depends(get_db)):
    current = simulation_service.current_state()
    was_active = current["scenario"]["id"] == scenario_id
    if was_active and current["simulation_id"] is not None:
        raise HTTPException(status_code=409, detail="Reinicia la simulacion antes de eliminar su escenario")
    scenario_service.delete_scenario(db, scenario_id)
    if was_active:
        default = scenario_service.ensure_default_scenario(db)
        data = scenario_service.scenario_to_dict(default)
        simulation_service.activate_configuration(
            data["configuration"],
            scenario_id=default.id,
            scenario_name=default.name,
            is_default=True,
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/scenarios/{scenario_id}/activate")
def activate_scenario(scenario_id: int, db: Session = Depends(get_db)):
    selected = scenario_service.get_scenario(db, scenario_id)
    data = scenario_service.scenario_to_dict(selected)
    return simulation_service.activate_configuration(
        data["configuration"],
        scenario_id=selected.id,
        scenario_name=selected.name,
        is_default=selected.is_default,
    )


@router.get("/scenarios/{scenario_id}/changes")
def scenario_changes(scenario_id: int, db: Session = Depends(get_db)):
    return scenario_service.scenario_changes(db, scenario_id)


@router.get("/history")
def history(db: Session = Depends(get_db)):
    simulations = db.query(Simulation).order_by(Simulation.started_at.desc()).limit(100).all()
    ids = [item.id for item in simulations]
    links = {
        item.simulation_id: item
        for item in db.query(SimulationScenario).filter(SimulationScenario.simulation_id.in_(ids)).all()
    } if ids else {}
    return [
        {
            "id": item.id,
            "scenario": links[item.id].scenario_name if item.id in links else "Escenario anterior",
            "started_at": item.started_at,
            "finished_at": item.finished_at,
            "status": item.status,
            "total_steps": item.total_steps,
            "deliveries": item.deliveries,
            "moves": item.moves,
            "efficiency": item.efficiency,
            "has_report": item.total_steps > 0,
            "duration_seconds": round(
                ((item.finished_at or datetime.utcnow()) - item.started_at).total_seconds(),
                2,
            ),
        }
        for item in simulations
    ]


def _load_json(value: str | None, fallback=None):
    try:
        return json.loads(value or "{}")
    except (TypeError, json.JSONDecodeError):
        return {} if fallback is None else fallback


def _speed_from_snapshot(snapshot: dict) -> dict | None:
    speed = snapshot.get("speed") if isinstance(snapshot, dict) else None
    if not isinstance(speed, dict):
        return None
    current = simulation_service.default_speed()
    current.update({key: speed[key] for key in ("key", "label", "interval_ms", "multiplier") if key in speed})
    return current


def _remember_speed(speed_trace: list[dict], speed: dict | None, created_at) -> None:
    if not speed:
        return
    if speed_trace:
        previous = speed_trace[-1]["speed"]
        if previous.get("key") == speed.get("key") and previous.get("interval_ms") == speed.get("interval_ms"):
            return
    speed_trace.append({"speed": speed, "created_at": created_at})


def _history_detail_payload(simulation_id: int, db: Session) -> dict:
    simulation = db.get(Simulation, simulation_id)
    if not simulation:
        raise HTTPException(status_code=404, detail="Proceso no encontrado")
    link = (
        db.query(SimulationScenario)
        .filter(SimulationScenario.simulation_id == simulation_id)
        .first()
    )
    steps = (
        db.query(SimulationStep)
        .filter(SimulationStep.simulation_id == simulation_id)
        .order_by(SimulationStep.step_number)
        .all()
    )
    checkpoints = (
        db.query(SimulationCheckpoint)
        .filter(SimulationCheckpoint.simulation_id == simulation_id)
        .order_by(SimulationCheckpoint.created_at)
        .all()
    )
    action_counts = Counter(step.action for step in steps)
    duration_seconds = round(((simulation.finished_at or datetime.utcnow()) - simulation.started_at).total_seconds(), 2)
    initial_configuration = _load_json(link.initial_snapshot) if link else None
    deliveries = simulation.deliveries
    speed_trace: list[dict] = []
    checkpoint_payloads = []
    for checkpoint in checkpoints:
        snapshot = _load_json(checkpoint.snapshot)
        _remember_speed(speed_trace, _speed_from_snapshot(snapshot), checkpoint.created_at)
        checkpoint_payloads.append(
            {
                "event": checkpoint.event,
                "snapshot": snapshot,
                "created_at": checkpoint.created_at,
            }
        )
    step_payloads = []
    for step in steps:
        snapshot = _load_json(step.snapshot)
        _remember_speed(speed_trace, _speed_from_snapshot(snapshot), step.created_at)
        robot = (snapshot.get("robots") or [{}])[0] if isinstance(snapshot, dict) else {}
        route = snapshot.get("last_route") if isinstance(snapshot, dict) else []
        step_payloads.append(
            {
                "step_number": step.step_number,
                "action": step.action,
                "reason": step.reason,
                "created_at": step.created_at,
                "robot": {
                    "id": robot.get("id"),
                    "x": robot.get("x"),
                    "y": robot.get("y"),
                    "carrying": robot.get("carrying"),
                    "status": robot.get("status"),
                },
                "target": snapshot.get("last_target") if isinstance(snapshot, dict) else None,
                "route": route if isinstance(route, list) else [],
                "route_length": len(route) if isinstance(route, list) else 0,
                "speed": _speed_from_snapshot(snapshot),
            }
        )
    active_speed = speed_trace[-1]["speed"] if speed_trace else simulation_service.default_speed()
    return {
        "simulation": {
            "id": simulation.id,
            "scenario": link.scenario_name if link else "Escenario anterior",
            "initial_configuration": initial_configuration,
            "status": simulation.status,
            "started_at": simulation.started_at,
            "finished_at": simulation.finished_at,
            "total_steps": simulation.total_steps,
            "deliveries": simulation.deliveries,
            "moves": simulation.moves,
            "efficiency": simulation.efficiency,
            "duration_seconds": duration_seconds,
            "speed": active_speed,
        },
        "steps": step_payloads,
        "checkpoints": checkpoint_payloads,
        "analytics": {
            "action_counts": dict(action_counts),
            "waits": action_counts.get("esperar", 0),
            "pickups": action_counts.get("recoger_paquete", 0),
            "deliveries": action_counts.get("entregar_paquete", 0),
            "average_steps_per_delivery": round(simulation.total_steps / deliveries, 2) if deliveries else 0,
            "duration_seconds": duration_seconds,
            "initial_packages": len(initial_configuration.get("packages", [])) if initial_configuration else None,
            "initial_obstacles": len(initial_configuration.get("obstacles", [])) if initial_configuration else None,
            "checkpoint_count": len(checkpoints),
            "speed": active_speed,
            "speed_trace": speed_trace,
        },
    }


def _build_markdown_report(data: dict) -> str:
    simulation = data["simulation"]
    analytics = data["analytics"]
    configuration = simulation.get("initial_configuration") or {}
    speed_trace = analytics.get("speed_trace") or [{"speed": simulation.get("speed"), "created_at": simulation.get("started_at")}]
    speed_lines = "\n".join(
        f'- {_speed_text(item.get("speed"))} desde {_format_dt(item.get("created_at"))}'
        for item in speed_trace
    )
    action_lines = "\n".join(
        f"- {action}: {count}"
        for action, count in sorted(analytics["action_counts"].items(), key=lambda item: item[0])
    ) or "- Sin acciones registradas"
    package_lines = "\n".join(
        f'- {package.get("id", "?").upper()}: ({package.get("x")}, {package.get("y")}) -> {package.get("zone")}'
        for package in configuration.get("packages", [])
    ) or "- Sin paquetes iniciales"
    zone_lines = "\n".join(
        f'- {zone.get("id", "?")}: ({zone.get("x")}, {zone.get("y")})'
        for zone in configuration.get("zones", [])
    ) or "- Sin zonas registradas"
    step_lines = "\n".join(
        "\n".join(
            [
                f'### Paso {step["step_number"]}',
                f'- Hora: {_format_dt(step["created_at"])}',
                f'- Accion: {step["action"]}',
                f'- Robot: ({step["robot"].get("x")}, {step["robot"].get("y")}) · carga: {step["robot"].get("carrying")}',
                f'- Objetivo: {step["target"] if step["target"] else "-"}',
                f'- Ruta Prolog ({step["route_length"]} nodos): {_route_text(step["route"])}',
                f'- Velocidad: {_speed_text(step.get("speed") or simulation.get("speed"))}',
                f'- Explicacion: {step["reason"] or "-"}',
            ]
        )
        for step in data["steps"]
    )
    return "\n".join(
        [
            f'# Reporte de corrida #{simulation["id"]}',
            "",
            "## Resumen",
            "",
            f'- Escenario: {simulation["scenario"]}',
            f'- Estado: {simulation["status"]}',
            f'- Inicio: {_format_dt(simulation["started_at"])}',
            f'- Fin: {_format_dt(simulation["finished_at"])}',
            f'- Duracion: {simulation["duration_seconds"]} s',
            f'- Pasos registrados: {simulation["total_steps"]}',
            f'- Movimientos: {simulation["moves"]}',
            f'- Entregas: {simulation["deliveries"]}',
            f'- Eficiencia: {simulation["efficiency"]}%',
            f'- Checkpoints automaticos: {analytics["checkpoint_count"]}',
            "",
            "## Velocidad de recorrido",
            "",
            speed_lines,
            "",
            "## Distribucion de acciones",
            "",
            action_lines,
            "",
            "## Configuracion inicial",
            "",
            f'- Mapa: {configuration.get("map", {}).get("width", "-")} x {configuration.get("map", {}).get("height", "-")}',
            f'- Estanterias: {len(configuration.get("obstacles", []))}',
            "",
            "### Paquetes",
            "",
            package_lines,
            "",
            "### Zonas",
            "",
            zone_lines,
            "",
            "## Recorrido paso a paso",
            "",
            step_lines or "Sin recorrido registrado.",
            "",
        ]
    )


@router.get("/history/{simulation_id}")
def history_detail(simulation_id: int, db: Session = Depends(get_db)):
    return _history_detail_payload(simulation_id, db)


@router.get("/history/{simulation_id}/report")
def history_report(simulation_id: int, db: Session = Depends(get_db)):
    data = _history_detail_payload(simulation_id, db)
    if not data["steps"]:
        raise HTTPException(status_code=409, detail="Este proceso aun no tiene recorrido para reportar")
    content = build_analytics_pdf(data)
    return Response(
        content=content,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="reporte_proceso_{simulation_id}.pdf"'},
    )

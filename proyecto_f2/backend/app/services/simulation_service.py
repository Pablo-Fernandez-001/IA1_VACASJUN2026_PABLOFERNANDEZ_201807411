import json
from copy import deepcopy
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.entities import (
    MetricRecord,
    PackageRecord,
    RobotRecord,
    Simulation,
    SimulationCheckpoint,
    SimulationScenario,
    SimulationStep,
)
from app.services.prolog_service import next_action
from app.services.scenario_service import DEFAULT_CONFIGURATION, create_auto_scenario, normalize_configuration


ACTIVE_CONFIGURATION = normalize_configuration(DEFAULT_CONFIGURATION)
ACTIVE_SCENARIO = {"id": None, "name": "Bodega clasica", "is_default": True, "dirty": False}


def _runtime_from_configuration(configuration: dict) -> dict:
    clean = normalize_configuration(configuration)
    return {
        "map": deepcopy(clean["map"]),
        "running": False,
        "phase": "ready",
        "simulation_id": None,
        "started_at": None,
        "steps": 0,
        "moves": 0,
        "deliveries": 0,
        "robots": deepcopy(clean["robots"]),
        "packages": deepcopy(clean["packages"]),
        "zones": deepcopy(clean["zones"]),
        "obstacles": deepcopy(clean["obstacles"]),
        "last_action": None,
        "last_reason": "Escenario listo para iniciar.",
        "last_source": None,
        "last_route": [],
        "last_target": None,
    }


STATE = _runtime_from_configuration(ACTIVE_CONFIGURATION)


def reset_state() -> dict:
    global STATE
    STATE = _runtime_from_configuration(ACTIVE_CONFIGURATION)
    return current_state()


def current_state() -> dict:
    snapshot = deepcopy(STATE)
    snapshot["scenario"] = deepcopy(ACTIVE_SCENARIO)
    return snapshot


def activate_configuration(
    configuration: dict,
    scenario_id: int | None = None,
    scenario_name: str = "Escenario temporal",
    is_default: bool = False,
    dirty: bool = False,
) -> dict:
    global ACTIVE_CONFIGURATION, ACTIVE_SCENARIO
    if STATE.get("simulation_id") is not None:
        raise HTTPException(status_code=409, detail="Reinicia la simulacion antes de cambiar el escenario")
    ACTIVE_CONFIGURATION = normalize_configuration(configuration)
    ACTIVE_SCENARIO = {
        "id": scenario_id,
        "name": scenario_name,
        "is_default": is_default,
        "dirty": dirty,
    }
    return reset_state()


def _active_robot() -> dict:
    return STATE["robots"][0]


def _package(package_id: str) -> dict | None:
    return next((package for package in STATE["packages"] if package["id"] == package_id), None)


def _zone(zone_id: str) -> dict:
    return next(zone for zone in STATE["zones"] if zone["id"] == zone_id)


def _valid_position(x: int, y: int) -> bool:
    if x < 1 or y < 1 or x > STATE["map"]["width"] or y > STATE["map"]["height"]:
        return False
    return not any(obstacle["x"] == x and obstacle["y"] == y for obstacle in STATE["obstacles"])


def _sync_carried_package(robot: dict) -> None:
    if robot["carrying"] != "none":
        package = _package(robot["carrying"])
        if package:
            package["x"] = robot["x"]
            package["y"] = robot["y"]


def _apply_action(action: str) -> None:
    robot = _active_robot()
    delta = {
        "mover_arriba": (0, -1),
        "mover_abajo": (0, 1),
        "mover_izquierda": (-1, 0),
        "mover_derecha": (1, 0),
    }
    if action in delta:
        dx, dy = delta[action]
        nx, ny = robot["x"] + dx, robot["y"] + dy
        if _valid_position(nx, ny):
            robot["x"], robot["y"] = nx, ny
            STATE["moves"] += 1
            _sync_carried_package(robot)
        return
    if action == "recoger_paquete" and robot["carrying"] == "none":
        package = next(
            (
                item
                for item in STATE["packages"]
                if item["status"] == "pendiente" and item["x"] == robot["x"] and item["y"] == robot["y"]
            ),
            None,
        )
        if package:
            package["status"] = "en_robot"
            robot["carrying"] = package["id"]
            robot["status"] = "transportando"
            _sync_carried_package(robot)
        return
    if action == "entregar_paquete" and robot["carrying"] != "none":
        package = _package(robot["carrying"])
        if package:
            zone = _zone(package["zone"])
            if robot["x"] == zone["x"] and robot["y"] == zone["y"]:
                package["status"] = "entregado"
                robot["carrying"] = "none"
                robot["status"] = "libre"
                STATE["deliveries"] += 1


def _metrics() -> dict:
    pending = sum(1 for package in STATE["packages"] if package["status"] != "entregado")
    elapsed = 0.0
    if STATE["started_at"]:
        elapsed = (datetime.utcnow() - datetime.fromisoformat(STATE["started_at"])).total_seconds()
    efficiency = round((STATE["deliveries"] / STATE["moves"]) * 100, 2) if STATE["moves"] else 0
    return {
        "deliveries": STATE["deliveries"],
        "moves": STATE["moves"],
        "pending_packages": pending,
        "efficiency": efficiency,
        "elapsed_seconds": round(elapsed, 2),
    }


def _record_snapshot(db: Session, action: str, reason: str) -> None:
    simulation_id = STATE["simulation_id"]
    if not simulation_id:
        return
    db.add(
        SimulationStep(
            simulation_id=simulation_id,
            step_number=STATE["steps"],
            robot_id=_active_robot()["id"],
            action=action,
            reason=reason,
            snapshot=json.dumps(current_state()),
        )
    )
    robot = _active_robot()
    db.add(
        RobotRecord(
            simulation_id=simulation_id,
            robot_code=robot["id"],
            x=robot["x"],
            y=robot["y"],
            carrying=robot["carrying"],
            status=robot["status"],
        )
    )
    for package in STATE["packages"]:
        db.add(
            PackageRecord(
                simulation_id=simulation_id,
                package_code=package["id"],
                x=package["x"],
                y=package["y"],
                zone=package["zone"],
                status=package["status"],
            )
        )
    metrics = _metrics()
    db.add(MetricRecord(simulation_id=simulation_id, **metrics))
    simulation = db.get(Simulation, simulation_id)
    if simulation:
        simulation.total_steps = STATE["steps"]
        simulation.deliveries = metrics["deliveries"]
        simulation.moves = metrics["moves"]
        simulation.efficiency = metrics["efficiency"]
        if metrics["pending_packages"] == 0:
            simulation.status = "completed"
            simulation.finished_at = datetime.utcnow()
            STATE["running"] = False
            STATE["phase"] = "completed"
            _checkpoint(db, "completed")
    db.commit()


def _checkpoint(db: Session, event: str) -> None:
    if not STATE.get("simulation_id"):
        return
    db.add(
        SimulationCheckpoint(
            simulation_id=STATE["simulation_id"],
            event=event,
            snapshot=json.dumps(current_state()),
        )
    )


def _close_previous_simulation(db: Session, status: str) -> None:
    if not STATE.get("simulation_id"):
        return
    simulation = db.get(Simulation, STATE["simulation_id"])
    if simulation and simulation.status not in {"completed", "reset"}:
        simulation.status = status
        simulation.finished_at = datetime.utcnow()
        db.commit()


def start(db: Session) -> dict:
    global ACTIVE_SCENARIO
    if STATE.get("simulation_id"):
        _checkpoint(db, "restarted")
    _close_previous_simulation(db, "restarted")
    if ACTIVE_SCENARIO["id"] is None or ACTIVE_SCENARIO.get("dirty"):
        autosaved = create_auto_scenario(db, ACTIVE_CONFIGURATION)
        ACTIVE_SCENARIO = {
            "id": autosaved.id,
            "name": autosaved.name,
            "is_default": False,
            "dirty": False,
            "autosaved": True,
        }
    reset_state()
    simulation = Simulation(status="running")
    db.add(simulation)
    db.flush()
    db.add(
        SimulationScenario(
            simulation_id=simulation.id,
            scenario_id=ACTIVE_SCENARIO["id"],
            scenario_name=ACTIVE_SCENARIO["name"],
            initial_snapshot=json.dumps(ACTIVE_CONFIGURATION),
        )
    )
    db.commit()
    db.refresh(simulation)
    STATE["running"] = True
    STATE["phase"] = "running"
    STATE["simulation_id"] = simulation.id
    STATE["started_at"] = simulation.started_at.isoformat()
    STATE["last_reason"] = "Simulacion iniciada; Prolog esta listo para decidir."
    _checkpoint(db, "started")
    if not STATE["packages"]:
        simulation.status = "completed"
        simulation.finished_at = datetime.utcnow()
        STATE["running"] = False
        STATE["phase"] = "completed"
        STATE["last_reason"] = "El escenario no contiene paquetes pendientes."
        _checkpoint(db, "completed")
    db.commit()
    return current_state()


def pause(db: Session) -> dict:
    STATE["running"] = False
    STATE["phase"] = "paused" if STATE["simulation_id"] else "ready"
    if STATE["simulation_id"]:
        simulation = db.get(Simulation, STATE["simulation_id"])
        if simulation and simulation.status == "running":
            simulation.status = "paused"
            _checkpoint(db, "paused")
            db.commit()
    return current_state()


def reset(db: Session) -> dict:
    _checkpoint(db, "reset")
    _close_previous_simulation(db, "reset")
    return reset_state()


def step(db: Session) -> dict:
    if not STATE["simulation_id"]:
        start(db)
    simulation = db.get(Simulation, STATE["simulation_id"])
    if simulation and simulation.status == "paused":
        simulation.status = "running"
        _checkpoint(db, "resumed")
        db.commit()
    STATE["running"] = True
    STATE["phase"] = "running"
    decision = next_action(current_state(), _active_robot()["id"])
    action = decision["action"]
    reason = decision.get("reason", "")
    _apply_action(action)
    STATE["steps"] += 1
    STATE["last_action"] = action
    STATE["last_reason"] = reason
    STATE["last_source"] = decision.get("source")
    STATE["last_route"] = decision.get("route", [])
    STATE["last_target"] = decision.get("target")
    _record_snapshot(db, action, reason)
    return current_state()


def auto(db: Session, max_steps: int = 25) -> dict:
    for _ in range(max(1, min(max_steps, 500))):
        if _metrics()["pending_packages"] == 0:
            break
        step(db)
        if STATE["last_action"] == "esperar":
            break
    return current_state()


def metrics() -> dict:
    result = _metrics()
    result["phase"] = STATE["phase"]
    result["scenario"] = ACTIVE_SCENARIO["name"]
    return result

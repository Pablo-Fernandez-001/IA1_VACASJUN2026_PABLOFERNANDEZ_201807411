import json
from copy import deepcopy
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.entities import MetricRecord, PackageRecord, RobotRecord, Simulation, SimulationStep
from app.services.prolog_service import next_action


INITIAL_STATE = {
    "map": {"width": 10, "height": 10},
    "running": False,
    "simulation_id": None,
    "started_at": None,
    "steps": 0,
    "moves": 0,
    "deliveries": 0,
    "robots": [{"id": "r1", "x": 1, "y": 1, "status": "libre", "carrying": "none"}],
    "packages": [
        {"id": "p1", "x": 1, "y": 3, "zone": "zona_a", "status": "pendiente"},
        {"id": "p2", "x": 4, "y": 2, "zone": "zona_b", "status": "pendiente"},
        {"id": "p3", "x": 6, "y": 8, "zone": "zona_a", "status": "pendiente"},
        {"id": "p4", "x": 9, "y": 1, "zone": "zona_b", "status": "pendiente"},
        {"id": "p5", "x": 3, "y": 9, "zone": "zona_a", "status": "pendiente"},
    ],
    "zones": [{"id": "zona_a", "x": 10, "y": 10}, {"id": "zona_b", "x": 1, "y": 10}],
    "obstacles": [
        {"x": 3, "y": 1},
        {"x": 3, "y": 2},
        {"x": 3, "y": 3},
        {"x": 5, "y": 5},
        {"x": 6, "y": 5},
        {"x": 7, "y": 5},
        {"x": 2, "y": 7},
        {"x": 8, "y": 3},
    ],
    "last_action": None,
    "last_reason": "",
}

STATE = deepcopy(INITIAL_STATE)


def reset_state() -> dict:
    global STATE
    STATE = deepcopy(INITIAL_STATE)
    return STATE


def current_state() -> dict:
    return deepcopy(STATE)


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
    db.commit()


def start(db: Session) -> dict:
    reset_state()
    simulation = Simulation(status="running")
    db.add(simulation)
    db.commit()
    db.refresh(simulation)
    STATE["running"] = True
    STATE["simulation_id"] = simulation.id
    STATE["started_at"] = simulation.started_at.isoformat()
    return current_state()


def pause(db: Session) -> dict:
    STATE["running"] = False
    if STATE["simulation_id"]:
        simulation = db.get(Simulation, STATE["simulation_id"])
        if simulation and simulation.status == "running":
            simulation.status = "paused"
            db.commit()
    return current_state()


def reset(db: Session) -> dict:
    if STATE["simulation_id"]:
        simulation = db.get(Simulation, STATE["simulation_id"])
        if simulation and simulation.status == "running":
            simulation.status = "reset"
            simulation.finished_at = datetime.utcnow()
            db.commit()
    return reset_state()


def step(db: Session) -> dict:
    if not STATE["simulation_id"]:
        start(db)
    STATE["running"] = True
    decision = next_action(current_state(), _active_robot()["id"])
    action = decision["action"]
    reason = decision.get("reason", "")
    _apply_action(action)
    STATE["steps"] += 1
    STATE["last_action"] = action
    STATE["last_reason"] = reason
    _record_snapshot(db, action, reason)
    return current_state()


def auto(db: Session, max_steps: int = 25) -> dict:
    STATE["running"] = True
    for _ in range(max_steps):
        if _metrics()["pending_packages"] == 0:
            break
        step(db)
    return current_state()


def metrics() -> dict:
    return _metrics()

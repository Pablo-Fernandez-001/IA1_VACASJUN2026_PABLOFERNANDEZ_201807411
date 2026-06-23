import json
from copy import deepcopy

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.entities import Scenario, ScenarioChange, SimulationScenario


DEFAULT_CONFIGURATION = {
    "map": {"width": 10, "height": 10},
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
}


def normalize_configuration(configuration: dict) -> dict:
    normalized = deepcopy(configuration)
    for robot in normalized["robots"]:
        robot["status"] = "libre"
        robot["carrying"] = "none"
    for package in normalized["packages"]:
        package["status"] = "pendiente"
    return normalized


def _configuration(value: dict | object) -> dict:
    if hasattr(value, "model_dump"):
        return value.model_dump()
    return deepcopy(value)


def scenario_to_dict(scenario: Scenario) -> dict:
    return {
        "id": scenario.id,
        "name": scenario.name,
        "is_default": scenario.is_default,
        "width": scenario.width,
        "height": scenario.height,
        "configuration": json.loads(scenario.configuration),
        "created_at": scenario.created_at,
        "updated_at": scenario.updated_at,
    }


def ensure_default_scenario(db: Session) -> Scenario:
    scenario = db.query(Scenario).filter(Scenario.is_default.is_(True)).first()
    if scenario:
        return scenario
    configuration = normalize_configuration(DEFAULT_CONFIGURATION)
    scenario = Scenario(
        name="Bodega clasica",
        is_default=True,
        width=configuration["map"]["width"],
        height=configuration["map"]["height"],
        configuration=json.dumps(configuration),
    )
    db.add(scenario)
    db.flush()
    db.add(ScenarioChange(scenario_id=scenario.id, action="created", details='{"source":"system"}'))
    db.commit()
    db.refresh(scenario)
    return scenario


def list_scenarios(db: Session) -> list[dict]:
    ensure_default_scenario(db)
    scenarios = db.query(Scenario).order_by(Scenario.is_default.desc(), Scenario.name).all()
    return [scenario_to_dict(item) for item in scenarios]


def get_scenario(db: Session, scenario_id: int) -> Scenario:
    scenario = db.get(Scenario, scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Escenario no encontrado")
    return scenario


def _ensure_unique_name(db: Session, name: str, exclude_id: int | None = None) -> None:
    query = db.query(Scenario).filter(func.lower(Scenario.name) == name.strip().lower())
    if exclude_id is not None:
        query = query.filter(Scenario.id != exclude_id)
    if query.first():
        raise HTTPException(status_code=409, detail="Ya existe un escenario con ese nombre")


def create_scenario(db: Session, name: str, configuration: dict | object) -> Scenario:
    clean_name = name.strip()
    _ensure_unique_name(db, clean_name)
    clean_configuration = normalize_configuration(_configuration(configuration))
    scenario = Scenario(
        name=clean_name,
        is_default=False,
        width=clean_configuration["map"]["width"],
        height=clean_configuration["map"]["height"],
        configuration=json.dumps(clean_configuration),
    )
    db.add(scenario)
    db.flush()
    db.add(
        ScenarioChange(
            scenario_id=scenario.id,
            action="created",
            details=json.dumps({"packages": len(clean_configuration["packages"])}),
        )
    )
    db.commit()
    db.refresh(scenario)
    return scenario


def update_scenario(db: Session, scenario_id: int, name: str, configuration: dict | object) -> Scenario:
    scenario = get_scenario(db, scenario_id)
    if scenario.is_default:
        raise HTTPException(status_code=409, detail="El escenario base es inmutable; guardalo con otro nombre")
    clean_name = name.strip()
    _ensure_unique_name(db, clean_name, exclude_id=scenario.id)
    clean_configuration = normalize_configuration(_configuration(configuration))
    scenario.name = clean_name
    scenario.width = clean_configuration["map"]["width"]
    scenario.height = clean_configuration["map"]["height"]
    scenario.configuration = json.dumps(clean_configuration)
    db.add(
        ScenarioChange(
            scenario_id=scenario.id,
            action="updated",
            details=json.dumps({"packages": len(clean_configuration["packages"])}),
        )
    )
    db.commit()
    db.refresh(scenario)
    return scenario


def delete_scenario(db: Session, scenario_id: int) -> None:
    scenario = get_scenario(db, scenario_id)
    if scenario.is_default:
        raise HTTPException(status_code=409, detail="El escenario base no se puede eliminar")
    db.query(SimulationScenario).filter(SimulationScenario.scenario_id == scenario_id).update(
        {SimulationScenario.scenario_id: None},
        synchronize_session=False,
    )
    db.query(ScenarioChange).filter(ScenarioChange.scenario_id == scenario_id).delete()
    db.delete(scenario)
    db.commit()


def scenario_changes(db: Session, scenario_id: int) -> list[dict]:
    get_scenario(db, scenario_id)
    changes = (
        db.query(ScenarioChange)
        .filter(ScenarioChange.scenario_id == scenario_id)
        .order_by(ScenarioChange.created_at.desc())
        .all()
    )
    return [
        {
            "id": change.id,
            "action": change.action,
            "details": json.loads(change.details),
            "created_at": change.created_at,
        }
        for change in changes
    ]

import json

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.entities import Simulation, SimulationScenario, SimulationStep
from app.schemas.scenario import ScenarioApply, ScenarioCreate, ScenarioUpdate
from app.services import scenario_service, simulation_service

router = APIRouter(prefix="/api", tags=["simulation"])


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
    was_active = simulation_service.current_state()["scenario"]["id"] == scenario_id
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
        }
        for item in simulations
    ]


@router.get("/history/{simulation_id}")
def history_detail(simulation_id: int, db: Session = Depends(get_db)):
    simulation = db.get(Simulation, simulation_id)
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
    return {
        "simulation": {
            "id": simulation.id,
            "scenario": link.scenario_name if link else "Escenario anterior",
            "initial_configuration": json.loads(link.initial_snapshot) if link else None,
            "status": simulation.status,
            "started_at": simulation.started_at,
            "finished_at": simulation.finished_at,
            "total_steps": simulation.total_steps,
            "deliveries": simulation.deliveries,
            "moves": simulation.moves,
            "efficiency": simulation.efficiency,
        }
        if simulation
        else None,
        "steps": [
            {
                "step_number": step.step_number,
                "action": step.action,
                "reason": step.reason,
                "created_at": step.created_at,
            }
            for step in steps
        ],
    }

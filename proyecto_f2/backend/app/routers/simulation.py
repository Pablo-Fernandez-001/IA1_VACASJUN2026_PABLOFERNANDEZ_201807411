from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.entities import Simulation, SimulationStep
from app.services import simulation_service

router = APIRouter(prefix="/api", tags=["simulation"])


@router.get("/simulation/state")
def state():
    return simulation_service.current_state()


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


@router.get("/history")
def history(db: Session = Depends(get_db)):
    simulations = db.query(Simulation).order_by(Simulation.started_at.desc()).limit(100).all()
    return [
        {
            "id": item.id,
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
    steps = db.query(SimulationStep).filter(SimulationStep.simulation_id == simulation_id).order_by(SimulationStep.step_number).all()
    return {
        "simulation": {
            "id": simulation.id,
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
            {"step_number": step.step_number, "action": step.action, "reason": step.reason, "created_at": step.created_at}
            for step in steps
        ],
    }

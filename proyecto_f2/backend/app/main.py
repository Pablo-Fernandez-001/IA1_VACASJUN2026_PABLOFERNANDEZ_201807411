from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database.init_db import init_db
from app.database.session import SessionLocal
from app.routers import simulation
from app.services import scenario_service, simulation_service


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    with SessionLocal() as db:
        default = scenario_service.ensure_default_scenario(db)
        data = scenario_service.scenario_to_dict(default)
        simulation_service.activate_configuration(
            data["configuration"],
            scenario_id=default.id,
            scenario_name=default.name,
            is_default=True,
        )
    yield


app = FastAPI(
    title="Smart Warehouse API",
    description="Simulacion de bodega inteligente con decisiones originadas en SWI-Prolog.",
    version="2.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", tags=["system"])
def health():
    return {"status": "ok", "service": "smart-warehouse-api"}


app.include_router(simulation.router)

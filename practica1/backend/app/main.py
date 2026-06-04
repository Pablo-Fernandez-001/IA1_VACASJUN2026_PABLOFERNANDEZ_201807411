from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.cities_feature.router import router as cities_router
from app.routes_feature.router import router as routes_router
from app.connections_feature.router import router as connections_router


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend Python orientado por funcionalidades que consulta SWI-Prolog.",
    version=settings.VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cities_router)
app.include_router(routes_router)
app.include_router(connections_router)


@app.get("/")
def root():
    return {
        "mensaje": "API funcionando correctamente",
        "arquitectura": "Feature-Based Layered Architecture",
        "motor_logico": "SWI-Prolog",
        "backend": "FastAPI"
    }
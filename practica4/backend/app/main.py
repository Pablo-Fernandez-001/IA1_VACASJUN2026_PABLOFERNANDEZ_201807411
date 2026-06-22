from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.maze_routes import router as maze_router
from app.core.config import APP_TITLE, APP_VERSION, CORS_ORIGINS
from app.models.schemas import HealthResponse


app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description="API REST para resolver y comparar laberintos con BFS y DFS manuales.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(maze_router)


@app.exception_handler(RequestValidationError)
async def readable_validation_error(
    _request: Request, error: RequestValidationError
) -> JSONResponse:
    """Conserva el codigo 422 y agrega un mensaje sencillo para clientes web."""

    first = error.errors()[0] if error.errors() else {}
    location = ".".join(str(part) for part in first.get("loc", [])[1:])
    detail = first.get("msg", "Solicitud invalida.")
    message = f"Dato invalido en '{location}': {detail}" if location else detail
    return JSONResponse(
        status_code=422,
        content={"detail": message, "errors": error.errors()},
    )


@app.get("/api/health", response_model=HealthResponse, tags=["Sistema"])
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="RoboMaze API", version=APP_VERSION)


@app.get("/", include_in_schema=False)
def root() -> dict[str, str]:
    return {
        "message": "RoboMaze API en funcionamiento.",
        "documentation": "/docs",
        "health": "/api/health",
    }

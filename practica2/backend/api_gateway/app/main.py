from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.features.answers.router import router as answers_router
from app.features.auth.router import router as auth_router
from app.features.categories.router import router as categories_router
from app.features.questions.router import router as questions_router
from app.features.search.router import router as search_router
from app.features.settings.router import router as settings_router
from app.features.stats.router import router as stats_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    with SessionLocal() as db:
        init_db(db)
    yield


app = FastAPI(
    title="SmartBot Practica 2 API",
    description="API REST Python para FAQ persistidas exclusivamente en SQLite.",
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
    return {"status": "ok", "service": "smartbot-api", "storage": "SQLite"}


app.include_router(auth_router)
app.include_router(categories_router)
app.include_router(questions_router)
app.include_router(answers_router)
app.include_router(search_router)
app.include_router(settings_router)
app.include_router(stats_router)

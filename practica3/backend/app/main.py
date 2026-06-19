from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database.init_db import init_db
from app.database.session import SessionLocal
from app.routers import auth, dashboard, invoices, logs, providers, reports


@asynccontextmanager
async def lifespan(_: FastAPI):
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.report_dir).mkdir(parents=True, exist_ok=True)
    with SessionLocal() as db:
        init_db(db)
    yield


app = FastAPI(
    title="SmartInvoice API",
    description="Procesamiento local de facturas con Computer Vision, OCR, RPA, reportes y correo.",
    version="1.0.0",
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
    return {"status": "ok", "service": "smartinvoice-api"}


app.include_router(auth.router)
app.include_router(providers.router)
app.include_router(invoices.router)
app.include_router(logs.router)
app.include_router(reports.router)
app.include_router(dashboard.router)

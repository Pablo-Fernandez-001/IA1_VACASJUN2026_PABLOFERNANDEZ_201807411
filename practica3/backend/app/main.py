from contextlib import asynccontextmanager
import os
from pathlib import Path
import shutil

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.init_db import init_db
from app.database.session import SessionLocal, get_db
from app.routers import auth, dashboard, invoices, logs, providers, reports, rpa


@asynccontextmanager
async def lifespan(_: FastAPI):
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.report_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.ocr_evidence_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.rpa_evidence_dir).mkdir(parents=True, exist_ok=True)
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
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {
        "status": "ok",
        "service": "smartinvoice-api",
        "database": "connected",
        "tesseract_available": bool(shutil.which("tesseract")),
        "rpa_engine": "playwright",
        "public_url": settings.public_url or None,
    }


app.include_router(auth.router)
app.include_router(providers.router)
app.include_router(invoices.router)
app.include_router(logs.router)
app.include_router(reports.router)
app.include_router(rpa.router)
app.include_router(dashboard.router)

frontend_dir = Path(os.getenv("FRONTEND_DIR", "./frontend"))
if frontend_dir.is_dir():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")

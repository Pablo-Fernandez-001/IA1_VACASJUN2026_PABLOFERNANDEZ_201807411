from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.init_db import init_db
from app.features.auth.router import router as auth_router
from app.features.categories.router import router as categories_router
from app.features.faqs.router import router as faqs_router
from app.features.settings.router import router as settings_router
from app.features.stats.router import router as stats_router
from app.features.diagnostics.router import router as diagnostics_router

app = FastAPI(title="SmartBot API Gateway", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def startup():
    db = next(get_db())
    try:
        init_db(db)
    finally:
        db.close()

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "api-gateway"}

app.include_router(auth_router)
app.include_router(categories_router)
app.include_router(faqs_router)
app.include_router(settings_router)
app.include_router(stats_router)
app.include_router(diagnostics_router)

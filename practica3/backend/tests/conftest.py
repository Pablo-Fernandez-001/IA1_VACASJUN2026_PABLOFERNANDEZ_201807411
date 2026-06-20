import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = BACKEND_DIR.parent
sys.path.insert(0, str(BACKEND_DIR))
os.environ["DATABASE_URL"] = f"sqlite:///{(PROJECT_DIR / 'test_smartinvoice.db').as_posix()}"
os.environ["UPLOAD_DIR"] = str(PROJECT_DIR / "test_uploads")
os.environ["REPORT_DIR"] = str(PROJECT_DIR / "test_reports")
os.environ["EVIDENCE_DIR"] = str(PROJECT_DIR / "test_evidencias")

from app.database.init_db import init_db  # noqa: E402
from app.database.session import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        init_db(db)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def auth_headers(client):
    response = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}

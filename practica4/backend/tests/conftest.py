import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.main import app  # noqa: E402


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def simple_maze():
    return {
        "rows": 5,
        "cols": 5,
        "start": {"row": 0, "col": 0},
        "goal": {"row": 4, "col": 4},
        "obstacles": [
            {"row": 1, "col": 1},
            {"row": 1, "col": 2},
            {"row": 2, "col": 2},
        ],
    }

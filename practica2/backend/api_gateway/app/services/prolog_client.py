import requests
from app.core.config import settings

def run_diagnosis(payload: dict) -> dict:
    url = settings.prolog_service_url.rstrip("/") + "/api/prolog/diagnose"
    response = requests.post(url, json=payload, timeout=20)
    response.raise_for_status()
    return response.json()

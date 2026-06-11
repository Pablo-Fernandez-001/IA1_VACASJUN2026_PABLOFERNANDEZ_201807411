import httpx
from ..config import get_settings

class PrologClient:
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.prolog_service_url.rstrip("/")

    async def health(self) -> dict:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()

    async def symptoms(self) -> list[dict]:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(f"{self.base_url}/symptoms")
            response.raise_for_status()
            return response.json()["symptoms"]

    async def diagnose(self, symptoms: list[str]) -> dict:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(f"{self.base_url}/diagnose", json={"symptoms": symptoms})
            response.raise_for_status()
            return response.json()

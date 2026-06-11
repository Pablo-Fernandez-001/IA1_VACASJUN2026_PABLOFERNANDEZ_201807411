import httpx

from ..config import get_settings


class PrologClient:
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.prolog_service_url.rstrip("/")

    async def _request(self, method: str, path: str, **kwargs) -> dict | list:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.request(method, f"{self.base_url}{path}", **kwargs)
            response.raise_for_status()
            return response.json()

    async def health(self) -> dict:
        return await self._request("GET", "/health")

    async def knowledge(self) -> dict:
        return await self._request("GET", "/knowledge")

    async def symptoms(self) -> list[dict]:
        return (await self._request("GET", "/symptoms"))["symptoms"]

    async def create_symptom(self, payload: dict) -> dict:
        return await self._request("POST", "/symptoms", json=payload)

    async def update_symptom(self, symptom_id: str, payload: dict) -> dict:
        return await self._request("PUT", f"/symptoms/{symptom_id}", json=payload)

    async def delete_symptom(self, symptom_id: str) -> dict:
        return await self._request("DELETE", f"/symptoms/{symptom_id}")

    async def diagnosis_rules(self) -> list[dict]:
        return (await self._request("GET", "/diagnosis-rules"))["diagnosis_rules"]

    async def create_diagnosis_rule(self, payload: dict) -> dict:
        return await self._request("POST", "/diagnosis-rules", json=payload)

    async def update_diagnosis_rule(self, rule_id: str, payload: dict) -> dict:
        return await self._request("PUT", f"/diagnosis-rules/{rule_id}", json=payload)

    async def delete_diagnosis_rule(self, rule_id: str) -> dict:
        return await self._request("DELETE", f"/diagnosis-rules/{rule_id}")

    async def diagnose(self, symptoms: list[str]) -> dict:
        return await self._request("POST", "/diagnose", json={"symptoms": symptoms})

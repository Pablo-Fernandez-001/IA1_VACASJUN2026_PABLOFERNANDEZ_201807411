import httpx
from ..config import get_settings

class TelegramClient:
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.telegram_service_url.rstrip("/")

    async def send_message(self, text: str, chat_id: str | None = None) -> dict:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                f"{self.base_url}/notify",
                json={"text": text, "chat_id": chat_id},
            )
            response.raise_for_status()
            return response.json()

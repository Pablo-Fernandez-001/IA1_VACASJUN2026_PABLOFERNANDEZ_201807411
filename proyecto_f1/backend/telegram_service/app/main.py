import httpx
from fastapi import FastAPI
from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

SERVICE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ENV = (SERVICE_DIR / ".." / ".." / ".env").resolve()

class Settings(BaseSettings):
    telegram_bot_token: str = ""
    telegram_default_chat_id: str = ""
    model_config = SettingsConfigDict(env_file=(PROJECT_ENV, ".env"), extra="ignore")

settings = Settings()
app = FastAPI(title="Doctor Byte Telegram Service", version="1.0.0")

class NotifyRequest(BaseModel):
    text: str
    chat_id: str | None = None

@app.get("/health")
def health():
    return {"status": "ok", "service": "telegram-service", "configured": bool(settings.telegram_bot_token)}

@app.post("/notify")
async def notify(payload: NotifyRequest):
    if not settings.telegram_bot_token:
        return {"sent": False, "reason": "TELEGRAM_BOT_TOKEN no configurado"}
    chat_id = payload.chat_id or settings.telegram_default_chat_id
    if not chat_id:
        return {"sent": False, "reason": "chat_id no configurado"}

    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(url, json={"chat_id": chat_id, "text": payload.text})
    if response.status_code >= 400:
        return {"sent": False, "reason": response.text}
    return {"sent": True, "telegram_response": response.json()}

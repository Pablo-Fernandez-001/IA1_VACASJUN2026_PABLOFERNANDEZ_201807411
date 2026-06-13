import asyncio
from contextlib import asynccontextmanager, suppress
from pathlib import Path

import httpx
from fastapi import FastAPI
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

SERVICE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ENV = (SERVICE_DIR / ".." / ".." / ".env").resolve()


class Settings(BaseSettings):
    telegram_bot_token: str = ""
    telegram_default_chat_id: str = ""
    api_gateway_url: str = "http://localhost:8000"
    telegram_poll_seconds: float = 2.0
    model_config = SettingsConfigDict(env_file=(PROJECT_ENV, ".env"), extra="ignore")


settings = Settings()


class NotifyRequest(BaseModel):
    text: str
    chat_id: str | None = None


async def telegram_request(method: str, payload: dict | None = None, params: dict | None = None) -> dict:
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/{method}"
    async with httpx.AsyncClient(timeout=35) as client:
        response = await client.request("POST", url, json=payload, params=params)
        response.raise_for_status()
        return response.json()


async def send_message(chat_id: str | int, text: str) -> dict:
    return await telegram_request("sendMessage", {"chat_id": chat_id, "text": text})


async def gateway_get(path: str) -> dict:
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(f"{settings.api_gateway_url.rstrip('/')}{path}")
        response.raise_for_status()
        return response.json()


async def gateway_post(path: str, payload: dict) -> dict:
    async with httpx.AsyncClient(timeout=25) as client:
        response = await client.post(f"{settings.api_gateway_url.rstrip('/')}{path}", json=payload)
        response.raise_for_status()
        return response.json()


async def process_message(message: dict) -> None:
    chat = message.get("chat", {})
    sender = message.get("from", {})
    chat_id = chat.get("id")
    text = message.get("text", "").strip()
    if not chat_id or not text:
        return

    try:
        config = await gateway_get("/api/config")
        if not config.get("bot_active", True):
            await send_message(chat_id, "Doctor Byte se encuentra temporalmente inactivo.")
            return

        if text.startswith("/start") or text.startswith("/ayuda"):
            await send_message(
                chat_id,
                f"{config['welcome_message']}\n\n"
                "Comandos:\n/sintomas - ver IDs disponibles\n"
                "/diagnosticar id1,id2 - ejecutar la consulta Prolog",
            )
            return

        if text.startswith("/sintomas"):
            data = await gateway_get("/api/symptoms")
            lines = [f"{item['id']}: {item['name']}" for item in data.get("symptoms", [])]
            await send_message(chat_id, "Sintomas disponibles:\n" + "\n".join(lines))
            return

        if text.startswith("/diagnosticar"):
            raw = text.split(" ", 1)[1] if " " in text else ""
            symptoms = [item.strip() for item in raw.split(",") if item.strip()]
            if not symptoms:
                await send_message(chat_id, "Uso: /diagnosticar pantalla_negra,ventiladores_giran")
                return
            user = sender.get("username") or str(sender.get("id", "telegram"))
            record = await gateway_post(
                "/api/diagnose",
                {
                    "symptoms": symptoms,
                    "user_name": user,
                    "notify_telegram": False,
                    "telegram_chat_id": None,
                },
            )
            diagnostics = record.get("result", {}).get("diagnostics", [])
            if not diagnostics:
                await send_message(chat_id, config["no_diagnosis_message"])
                return
            top = diagnostics[0]
            recommendations = "\n".join(f"- {item}" for item in top.get("recommendations", []))
            await send_message(
                chat_id,
                f"{config['diagnosis_message']}\n\n"
                f"Diagnostico: {top['name']}\nProbabilidad: {top['probability']}%\n"
                f"Recomendaciones:\n{recommendations}",
            )
            return

        await send_message(chat_id, "No reconozco ese mensaje. Usa /ayuda para ver los comandos.")
    except httpx.HTTPStatusError as exc:
        await send_message(chat_id, f"No pude procesar la consulta: {exc.response.text[:300]}")
    except Exception as exc:
        await send_message(chat_id, f"No pude comunicarme con el backend: {exc}")


async def polling_loop() -> None:
    if not settings.telegram_bot_token:
        return
    offset = 0
    while True:
        try:
            updates = await telegram_request(
                "getUpdates",
                params={"timeout": 25, "offset": offset, "allowed_updates": '["message"]'},
            )
            for update in updates.get("result", []):
                offset = update["update_id"] + 1
                if "message" in update:
                    await process_message(update["message"])
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            print(f"Telegram polling error: {exc}", flush=True)
            await asyncio.sleep(5)
        await asyncio.sleep(settings.telegram_poll_seconds)


@asynccontextmanager
async def lifespan(_: FastAPI):
    task = asyncio.create_task(polling_loop())
    yield
    task.cancel()
    with suppress(asyncio.CancelledError):
        await task


app = FastAPI(title="Doctor Byte Telegram Service", version="2.0.0", lifespan=lifespan)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "telegram-service",
        "configured": bool(settings.telegram_bot_token),
        "receives_messages": True,
        "backend": settings.api_gateway_url,
    }


@app.post("/notify")
async def notify(payload: NotifyRequest):
    if not settings.telegram_bot_token:
        return {"sent": False, "reason": "TELEGRAM_BOT_TOKEN no configurado"}
    chat_id = payload.chat_id or settings.telegram_default_chat_id
    if not chat_id:
        return {"sent": False, "reason": "chat_id no configurado"}
    try:
        response = await send_message(chat_id, payload.text)
    except httpx.HTTPStatusError as exc:
        return {"sent": False, "reason": exc.response.text}
    return {"sent": True, "telegram_response": response}

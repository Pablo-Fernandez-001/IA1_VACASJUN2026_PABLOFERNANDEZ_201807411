import requests
from app.core.config import settings


def send_telegram_message(chat_id: str, text: str) -> dict:
    if not settings.telegram_bot_token:
        return {"sent": False, "reason": "TELEGRAM_BOT_TOKEN no configurado"}
    if not chat_id:
        return {"sent": False, "reason": "telegram_chat_id no configurado"}

    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    response = requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=20)
    if response.status_code >= 400:
        return {"sent": False, "reason": response.text}
    return {"sent": True, "telegram_response": response.json()}

import os
import time

import requests

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
API_BASE = os.getenv("API_BASE_URL", "http://localhost:8100").rstrip("/")
POLL_SECONDS = float(os.getenv("TELEGRAM_POLL_SECONDS", "2"))


def telegram(method: str, **payload):
    response = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/{method}",
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def send(chat_id: int, text: str):
    return telegram("sendMessage", chat_id=chat_id, text=text)


def api_get(path: str, **params):
    response = requests.get(f"{API_BASE}{path}", params=params, timeout=20)
    response.raise_for_status()
    return response.json()


def handle_message(message: dict):
    chat_id = message.get("chat", {}).get("id")
    sender = message.get("from", {})
    text = message.get("text", "").strip()
    if not chat_id or not text:
        return

    if text.startswith("/start") or text.startswith("/ayuda"):
        send(
            chat_id,
            "Hola, soy SmartBot. Escribe una pregunta y consultare la base de datos.\n\n"
            "Comandos:\n/categorias - ver temas disponibles\n/ayuda - mostrar esta ayuda",
        )
        return

    if text.startswith("/categorias"):
        categories = api_get("/api/categories")
        send(chat_id, "Categorias disponibles:\n" + "\n".join(f"- {item['name']}" for item in categories))
        return

    user = sender.get("username") or str(sender.get("id", "telegram"))
    result = api_get("/api/search", q=text, telegram_user=user)
    answer = result.get("answer", "No encontre una respuesta registrada.")
    if result.get("found") and result.get("category"):
        answer = f"{answer}\n\nCategoria: {result['category']}"
    send(chat_id, answer)


def main():
    if not TOKEN:
        print("TELEGRAM_BOT_TOKEN vacio. El contenedor queda en espera sin afectar la API.", flush=True)
        while True:
            time.sleep(60)

    offset = 0
    print("SmartBot Telegram iniciado", flush=True)
    while True:
        try:
            response = requests.get(
                f"https://api.telegram.org/bot{TOKEN}/getUpdates",
                params={"timeout": 25, "offset": offset, "allowed_updates": '["message"]'},
                timeout=35,
            )
            response.raise_for_status()
            for update in response.json().get("result", []):
                offset = update["update_id"] + 1
                if "message" in update:
                    handle_message(update["message"])
        except Exception as exc:
            print(f"Error del bot: {exc}", flush=True)
            time.sleep(5)
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()

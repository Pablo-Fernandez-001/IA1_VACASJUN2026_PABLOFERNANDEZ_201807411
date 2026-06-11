import os
import time
import requests

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")
POLL_SECONDS = float(os.getenv("TELEGRAM_POLL_SECONDS", "2"))

def tg(method, **params):
    return requests.post(f"https://api.telegram.org/bot{TOKEN}/{method}", json=params, timeout=20).json()

def send(chat_id, text):
    return tg("sendMessage", chat_id=chat_id, text=text, parse_mode="HTML")

def format_diagnostics(data):
    diagnostics = data.get("diagnostics", [])
    if not diagnostics:
        return "No encontré diagnósticos posibles con esos síntomas."
    chunks = ["<b>Diagnósticos posibles:</b>"]
    for d in diagnostics[:5]:
        route = " → ".join(d.get("solution_route", []))
        chunks.append(f"\n<b>{d['name']}</b> ({d['probability']}%)\nCategoría: {d['category']}\nNivel: {d['problem_level']}\nRuta: {route}")
    return "\n".join(chunks)

def handle_message(message):
    chat_id = message["chat"]["id"]
    user = message.get("from", {}).get("username") or str(message.get("from", {}).get("id", "telegram"))
    text = message.get("text", "").strip()
    if text.startswith("/start"):
        send(chat_id, "Hola, soy SmartBot. Escribe una pregunta o usa /diagnostico sintoma1,sintoma2")
        return
    if text.startswith("/diagnostico"):
        raw = text.replace("/diagnostico", "", 1).strip()
        symptom_codes = [x.strip() for x in raw.split(",") if x.strip()]
        r = requests.post(f"{API_BASE}/api/diagnostics/diagnose", json={"symptom_codes": symptom_codes, "telegram_user": user}, timeout=20)
        send(chat_id, format_diagnostics(r.json()))
        return
    r = requests.get(f"{API_BASE}/api/faqs/search", params={"q": text, "telegram_user": user}, timeout=20)
    data = r.json()
    send(chat_id, data.get("answer", "No encontré respuesta."))

def main():
    if not TOKEN:
        print("TELEGRAM_BOT_TOKEN vacío. El servicio queda inactivo pero no rompe el compose.")
        while True: time.sleep(60)
    offset = None
    print("SmartBot Telegram iniciado")
    while True:
        try:
            params = {"timeout": 20}
            if offset: params["offset"] = offset
            updates = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates", params=params, timeout=30).json()
            for upd in updates.get("result", []):
                offset = upd["update_id"] + 1
                if "message" in upd:
                    handle_message(upd["message"])
        except Exception as exc:
            print("Error bot:", exc)
            time.sleep(5)
        time.sleep(POLL_SECONDS)

if __name__ == "__main__":
    main()

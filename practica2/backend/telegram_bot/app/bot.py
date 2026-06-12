import os
import time
from html import escape
import requests

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
API_BASE = os.getenv("API_BASE_URL", "http://localhost:8100").rstrip("/")
POLL_SECONDS = float(os.getenv("TELEGRAM_POLL_SECONDS", "2"))

SESSIONS = {}


def session_for(chat_id):
    return SESSIONS.setdefault(str(chat_id), {"selected": set(), "awaiting_other": False})


def tg(method, **params):
    response = requests.post(f"https://api.telegram.org/bot{TOKEN}/{method}", json=params, timeout=20)
    return response.json()


def send(chat_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    return tg("sendMessage", **payload)


def edit(chat_id, message_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    return tg("editMessageText", **payload)


def answer_callback(callback_id, text=""):
    return tg("answerCallbackQuery", callback_query_id=callback_id, text=text, show_alert=False)


def get_symptoms():
    response = requests.get(f"{API_BASE}/api/diagnostics/symptoms", timeout=20)
    response.raise_for_status()
    return response.json()


def symptom_by_id(symptoms, symptom_id):
    for symptom in symptoms:
        if int(symptom["id"]) == int(symptom_id):
            return symptom
    return None


def clipped(text, limit=42):
    return text if len(text) <= limit else text[: limit - 3] + "..."


def h(text):
    return escape(str(text), quote=False)


def menu_text(selected):
    if selected:
        return (
            "<b>SmartBot IA1</b>\n"
            "Selecciona o quita sintomas con los botones.\n\n"
            f"Sintomas seleccionados: <b>{len(selected)}</b>\n"
            "Cuando termines, presiona <b>Diagnosticar</b>."
        )
    return (
        "<b>SmartBot IA1</b>\n"
        "Elige uno o varios sintomas con los botones.\n\n"
        "Tambien puedes usar <b>Otro sintoma</b> si no aparece en la lista."
    )


def build_menu(symptoms, selected):
    rows = []
    for symptom in symptoms:
        mark = "[x]" if symptom["code"] in selected else "[ ]"
        label = f"{mark} {clipped(symptom['name'])}"
        rows.append([{"text": label, "callback_data": f"sym:{symptom['id']}"}])

    rows.append([
        {"text": "Diagnosticar", "callback_data": "diag"},
        {"text": "Otro sintoma", "callback_data": "other"},
    ])
    rows.append([
        {"text": "Seleccionar todos", "callback_data": "all"},
        {"text": "Quitar todos", "callback_data": "none"},
    ])
    rows.append([{"text": "Limpiar/Reiniciar chat", "callback_data": "reset"}])
    return {"inline_keyboard": rows}


def send_menu(chat_id):
    state = session_for(chat_id)
    symptoms = get_symptoms()
    return send(chat_id, menu_text(state["selected"]), build_menu(symptoms, state["selected"]))


def refresh_menu(chat_id, message_id):
    state = session_for(chat_id)
    symptoms = get_symptoms()
    return edit(chat_id, message_id, menu_text(state["selected"]), build_menu(symptoms, state["selected"]))


def format_diagnostics(data, selected_codes):
    diagnostics = data.get("diagnostics", [])
    if not diagnostics:
        selected = ", ".join(selected_codes) or "ninguno"
        return (
            "No encontre diagnosticos posibles con esos sintomas.\n\n"
            f"Sintomas evaluados: {selected}\n"
            "Puedes agregar otro sintoma o reiniciar la seleccion."
        )

    chunks = ["<b>Diagnosticos posibles:</b>"]
    for item in diagnostics[:5]:
        route = " -> ".join(h(step) for step in item.get("solution_route", [])) or "Sin ruta registrada"
        missing = ", ".join(h(symptom) for symptom in item.get("missing_symptoms", [])) or "ninguno"
        chunks.append(
            f"\n<b>{h(item['name'])}</b> ({item['probability']}%)"
            f"\nCategoria: {h(item['category'])}"
            f"\nNivel: {h(item['problem_level'])}"
            f"\nCoincidencias: {item['matched']}/{item['total_required']}"
            f"\nFaltantes: {missing}"
            f"\nRuta: {route}"
        )
    return "\n".join(chunks)


def run_diagnosis(chat_id, user):
    state = session_for(chat_id)
    selected = list(state["selected"])
    if not selected:
        send(chat_id, "Selecciona al menos un sintoma antes de diagnosticar.")
        send_menu(chat_id)
        return

    response = requests.post(
        f"{API_BASE}/api/diagnostics/diagnose",
        json={"symptom_codes": selected, "telegram_user": user},
        timeout=20,
    )
    response.raise_for_status()
    send(chat_id, format_diagnostics(response.json(), selected))


def add_custom_symptom(chat_id, user, text):
    state = session_for(chat_id)
    response = requests.post(
        f"{API_BASE}/api/diagnostics/custom-symptoms",
        json={"name": text, "telegram_user": user, "selected_codes": list(state["selected"])},
        timeout=20,
    )
    response.raise_for_status()
    data = response.json()
    state["selected"] = set(data.get("selected_codes", []))
    state["awaiting_other"] = False
    status = "agregado" if data.get("created") else "ya existia"
    send(chat_id, f"Sintoma {status}: <b>{h(data['name'])}</b>\nQuedo seleccionado para el diagnostico.")
    send_menu(chat_id)


def handle_callback(callback):
    callback_id = callback["id"]
    data = callback.get("data", "")
    message = callback.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    message_id = message.get("message_id")
    user = callback.get("from", {}).get("username") or str(callback.get("from", {}).get("id", "telegram"))
    if not chat_id:
        answer_callback(callback_id)
        return

    state = session_for(chat_id)
    try:
        if data.startswith("sym:"):
            symptoms = get_symptoms()
            symptom = symptom_by_id(symptoms, data.split(":", 1)[1])
            if not symptom:
                answer_callback(callback_id, "Sintoma no encontrado")
                return
            code = symptom["code"]
            if code in state["selected"]:
                state["selected"].remove(code)
                answer_callback(callback_id, "Sintoma quitado")
            else:
                state["selected"].add(code)
                answer_callback(callback_id, "Sintoma seleccionado")
            refresh_menu(chat_id, message_id)
            return

        if data == "all":
            state["selected"] = {symptom["code"] for symptom in get_symptoms()}
            state["awaiting_other"] = False
            answer_callback(callback_id, "Todos seleccionados")
            refresh_menu(chat_id, message_id)
            return

        if data == "none":
            state["selected"].clear()
            state["awaiting_other"] = False
            answer_callback(callback_id, "Seleccion limpia")
            refresh_menu(chat_id, message_id)
            return

        if data == "reset":
            state["selected"].clear()
            state["awaiting_other"] = False
            answer_callback(callback_id, "Chat reiniciado")
            edit(chat_id, message_id, "Chat reiniciado. Empezamos de nuevo.")
            send_menu(chat_id)
            return

        if data == "other":
            state["awaiting_other"] = True
            answer_callback(callback_id, "Escribe el sintoma")
            send(chat_id, "Escribe el sintoma nuevo en un mensaje. Lo guardare y quedara seleccionado.")
            return

        if data == "diag":
            answer_callback(callback_id, "Diagnosticando")
            run_diagnosis(chat_id, user)
            return
    except Exception as exc:
        answer_callback(callback_id, "Ocurrio un error")
        send(chat_id, f"No pude procesar la accion: {exc}")


def handle_message(message):
    chat_id = message["chat"]["id"]
    user = message.get("from", {}).get("username") or str(message.get("from", {}).get("id", "telegram"))
    text = message.get("text", "").strip()
    state = session_for(chat_id)

    if text.startswith("/start") or text.lower() in {"reiniciar", "limpiar", "/reiniciar", "/limpiar"}:
        state["selected"].clear()
        state["awaiting_other"] = False
        send_menu(chat_id)
        return

    if state.get("awaiting_other"):
        add_custom_symptom(chat_id, user, text)
        return

    if text.startswith("/diagnostico"):
        raw = text.replace("/diagnostico", "", 1).strip()
        if not raw:
            send_menu(chat_id)
            return
        state["selected"] = {item.strip() for item in raw.split(",") if item.strip()}
        run_diagnosis(chat_id, user)
        return

    response = requests.get(f"{API_BASE}/api/faqs/search", params={"q": text, "telegram_user": user}, timeout=20)
    data = response.json()
    send(chat_id, data.get("answer", "No encontre respuesta."))


def main():
    if not TOKEN:
        print("TELEGRAM_BOT_TOKEN vacio. El servicio queda inactivo pero no rompe el compose.")
        while True:
            time.sleep(60)
    offset = None
    print("SmartBot Telegram iniciado")
    while True:
        try:
            params = {"timeout": 20}
            if offset:
                params["offset"] = offset
            updates = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates", params=params, timeout=30).json()
            for update in updates.get("result", []):
                offset = update["update_id"] + 1
                if "callback_query" in update:
                    handle_callback(update["callback_query"])
                elif "message" in update:
                    handle_message(update["message"])
        except Exception as exc:
            print("Error bot:", exc)
            time.sleep(5)
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()

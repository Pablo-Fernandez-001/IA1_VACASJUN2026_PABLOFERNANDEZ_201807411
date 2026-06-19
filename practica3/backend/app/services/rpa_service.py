from pathlib import Path

from app.core.config import settings
from app.models.entities import Invoice


def default_rpa_url() -> str:
    if settings.rpa_form_url:
        return settings.rpa_form_url
    project_root = Path(__file__).resolve().parents[3]
    return (project_root / "frontend" / "rpa_form.html").as_uri()


def register_invoice_in_form(invoice: Invoice) -> dict:
    target_url = default_rpa_url()
    payload = {
        "invoice_number": invoice.invoice_number,
        "provider_name": invoice.provider_name,
        "provider_nit": invoice.provider_nit,
        "total": f"{invoice.total:.2f}",
        "status": invoice.status,
    }
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(target_url)
            page.fill("#invoice_number", payload["invoice_number"])
            page.fill("#provider_name", payload["provider_name"])
            page.fill("#provider_nit", payload["provider_nit"])
            page.fill("#total", payload["total"])
            page.select_option("#status", payload["status"])
            page.click("#submit_rpa")
            page.wait_for_selector("#rpa_result.ready", timeout=5000)
            result = page.inner_text("#rpa_result")
            browser.close()
        return {"status": "Procesado", "target_url": target_url, "result": result}
    except Exception as exc:
        demo_result = "RPA demo: datos preparados para el formulario simulado. " + str(payload)
        return {"status": "Pendiente", "target_url": target_url, "result": f"{demo_result}. Detalle navegador: {exc}"}

import json
import re
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.entities import Invoice, ProcessingLog, RpaRun, User


def default_rpa_url() -> str:
    if settings.rpa_form_url:
        return settings.rpa_form_url
    if settings.public_url:
        return f"{settings.public_url.rstrip('/')}/rpa_form.html"
    project_root = Path(__file__).resolve().parents[3]
    return (project_root / "frontend" / "rpa_form.html").as_uri()


def _evidence_stem(invoice: Invoice) -> str:
    number = re.sub(r"[^a-zA-Z0-9_-]+", "_", invoice.invoice_number).strip("_") or str(invoice.id)
    return f"rpa_invoice_{invoice.id}_{number}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"


def register_invoice_in_form(invoice: Invoice) -> dict:
    target_url = default_rpa_url()
    evidence_dir = Path(settings.rpa_evidence_dir)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    stem = _evidence_stem(invoice)
    screenshot_path = evidence_dir / f"{stem}.png"
    receipt_path = evidence_dir / f"{stem}.json"
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
            page = browser.new_page(viewport={"width": 1280, "height": 900})
            page.goto(target_url, wait_until="domcontentloaded", timeout=15000)
            page.fill("#invoice_number", payload["invoice_number"])
            page.fill("#provider_name", payload["provider_name"])
            page.fill("#provider_nit", payload["provider_nit"])
            page.fill("#total", payload["total"])
            page.select_option("#status", payload["status"])
            page.click("#submit_rpa")
            page.wait_for_selector("#rpa_result.ready", timeout=5000)
            result = page.inner_text("#rpa_result")
            page.screenshot(path=str(screenshot_path), full_page=True)
            browser.close()
        receipt_path.write_text(
            json.dumps({"target_url": target_url, "payload": payload, "result": result}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return {
            "status": "Procesado",
            "target_url": target_url,
            "evidence_path": str(screenshot_path),
            "result": result,
        }
    except Exception as exc:
        error_path = evidence_dir / f"{stem}_error.txt"
        error_path.write_text(
            f"URL: {target_url}\nPayload: {json.dumps(payload, ensure_ascii=False)}\nError: {exc}\n",
            encoding="utf-8",
        )
        return {
            "status": "Error",
            "target_url": target_url,
            "evidence_path": str(error_path),
            "result": f"RPA no pudo completar el formulario: {exc}",
        }


def run_and_persist(db: Session, invoice: Invoice, user: User) -> RpaRun:
    result = register_invoice_in_form(invoice)
    run = RpaRun(
        invoice_id=invoice.id,
        status=result["status"],
        target_url=result["target_url"],
        evidence_path=result["evidence_path"],
        result=result["result"],
    )
    db.add(run)
    db.add(
        ProcessingLog(
            username=user.username,
            user_id=user.id,
            document_name=invoice.file_name,
            status=result["status"],
            result=f"RPA formulario: {result['result']}",
            error_detail=result["result"] if result["status"] == "Error" else "",
            invoice_id=invoice.id,
        )
    )
    db.commit()
    db.refresh(run)
    return run

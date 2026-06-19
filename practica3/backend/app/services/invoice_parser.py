import re
import unicodedata
from datetime import date, datetime
from pathlib import Path


def _clean(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text)
    return re.sub(r"[ \t]+", " ", normalized)


def _money(value: str | None) -> float:
    if not value:
        return 0.0
    value = value.replace("Q", "").replace("$", "").replace(",", "").strip()
    match = re.search(r"-?\d+(?:\.\d{1,2})?", value)
    return round(float(match.group(0)), 2) if match else 0.0


def _find(patterns: list[str], text: str, flags: int = re.IGNORECASE) -> str:
    for pattern in patterns:
        match = re.search(pattern, text, flags)
        if match:
            return match.group(1).strip(" :#-\n\t")
    return ""


def _parse_date(raw: str) -> date | None:
    if not raw:
        return None
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(raw.strip(), fmt).date()
        except ValueError:
            continue
    return None


def parse_invoice_text(raw_text: str, file_name: str = "") -> dict:
    text = _clean(raw_text)
    invoice_number = _find(
        [
            r"(?:factura|invoice)\s*(?:no\.?|numero|n[uú]mero|#)?\s*[:#-]?\s*([A-Z0-9-]{3,})",
            r"\b(?:serie|documento)\s*[:#-]?\s*([A-Z0-9-]{3,})",
        ],
        text,
    )
    if not invoice_number:
        invoice_number = Path(file_name).stem.upper().replace("_", "-")[:80] or "SIN-NUMERO"

    date_raw = _find(
        [
            r"(?:fecha|date)\s*[:#-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            r"(?:fecha|date)\s*[:#-]?\s*(\d{4}-\d{1,2}-\d{1,2})",
            r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{4})\b",
        ],
        text,
    )
    issue_date = _parse_date(date_raw)
    provider_name = _find(
        [
            r"(?:proveedor|emisor|empresa|cliente)\s*[:#-]?\s*([A-ZÁÉÍÓÚÑa-záéíóúñ0-9 .,&-]{3,80})",
            r"^\s*([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑa-záéíóúñ0-9 .,&-]{4,80})\s*$",
        ],
        text,
        re.IGNORECASE | re.MULTILINE,
    )
    nit = _find([r"\bNIT\s*[:#-]?\s*([0-9Kk-]{5,20})", r"\b([0-9]{5,12}-?[0-9Kk])\b"], text)
    subtotal = _money(
        _find([r"(?:subtotal|sub total)\s*[:#-]?\s*(?:Q|\$)?\s*([0-9,]+(?:\.\d{1,2})?)"], text)
    )
    taxes = _money(_find([r"(?:iva|impuestos?|tax)\s*[:#-]?\s*(?:Q|\$)?\s*([0-9,]+(?:\.\d{1,2})?)"], text))
    total = _money(
        _find(
            [
                r"(?:total\s*a\s*pagar|monto\s*total|grand\s*total|total)\s*[:#-]?\s*(?:Q|\$)?\s*([0-9,]+(?:\.\d{1,2})?)"
            ],
            text,
        )
    )
    if total <= 0 and subtotal > 0:
        total = round(subtotal + taxes, 2)
    if subtotal <= 0 and total > 0:
        subtotal = round(max(total - taxes, 0), 2)
    return {
        "invoice_number": invoice_number[:90],
        "issue_date": issue_date,
        "provider_name": (provider_name or "Proveedor no identificado")[:180],
        "provider_nit": (nit or "CF")[:40].upper(),
        "subtotal": subtotal,
        "taxes": taxes,
        "total": total,
    }

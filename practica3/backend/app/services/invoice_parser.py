import re
import unicodedata
from datetime import date, datetime
from pathlib import Path


def _clean(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text).replace("\r\n", "\n").replace("\r", "\n")
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in normalized.split("\n")]
    return "\n".join(line for line in lines if line)


def _money(value: str | None) -> float:
    if not value:
        return 0.0
    cleaned = re.sub(r"[^0-9,.-]", "", value)
    if not cleaned:
        return 0.0
    if "," in cleaned and "." in cleaned:
        if cleaned.rfind(".") > cleaned.rfind(","):
            cleaned = cleaned.replace(",", "")
        else:
            cleaned = cleaned.replace(".", "").replace(",", ".")
    elif "," in cleaned:
        tail = cleaned.rsplit(",", 1)[-1]
        cleaned = cleaned.replace(",", ".") if len(tail) <= 2 else cleaned.replace(",", "")
    try:
        return round(float(cleaned), 2)
    except ValueError:
        return 0.0


def _find(patterns: list[str], text: str, flags: int = re.IGNORECASE) -> str:
    for pattern in patterns:
        match = re.search(pattern, text, flags)
        if match:
            return match.group(1).strip(" :#-\n\t")
    return ""


def _labeled_money(text: str, labels: str) -> float:
    matches = re.findall(
        rf"(?im)^\s*(?:{labels})(?:\s*\d+(?:[.,]\d+)?\s*%)?\s*:?[ \t]*(?:Q|USD|\$)?[ \t]*([0-9][0-9.,]*)\s*$",
        text,
    )
    return _money(matches[-1]) if matches else 0.0


def _parse_date(raw: str) -> date | None:
    if not raw:
        return None
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%y", "%Y/%m/%d"):
        try:
            return datetime.strptime(raw.strip(), fmt).date()
        except ValueError:
            continue
    return None


def parse_invoice_text(raw_text: str, file_name: str = "") -> dict:
    text = _clean(raw_text)
    invoice_number = _find(
        [
            r"\b(FAC-[A-Z0-9-]*\d{3,})\b",
            r"(?:factura|invoice)\s*(?:no\.?|numero|n[uú]mero|#)?\s*[:#-]?\s*([A-Z0-9][A-Z0-9-]{2,})",
            r"\b(?:serie|documento)\s*[:#-]?\s*([A-Z0-9-]{3,})",
        ],
        text,
    )
    if not invoice_number:
        invoice_number = Path(file_name).stem.upper().replace("_", "-")[:80] or "SIN-NUMERO"

    date_raw = _find(
        [
            r"(?im)^\s*(?:fecha|date)\s*[:#-]?\s*(\d{1,4}[/-]\d{1,2}[/-]\d{1,4})\s*$",
            r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{4})\b",
        ],
        text,
    )
    provider_name = _find(
        [
            r"(?im)^\s*(?:proveedor|emisor|empresa)\s*[:#-]?\s*([^\n]{3,180})$",
            r"(?im)^\s*raz[oó]n\s+social\s*[:#-]?\s*([^\n]{3,180})$",
        ],
        text,
    )
    nit = _find(
        [r"(?im)^\s*NIT\s*[:#-]?\s*([0-9Kk-]{5,20})\s*$", r"\b([0-9]{5,12}-[0-9Kk])\b"],
        text,
    )
    subtotal = _labeled_money(text, r"subtotal|sub\s*total")
    taxes = _labeled_money(text, r"iva|impuestos?|tax")
    total = _labeled_money(text, r"total\s+a\s+pagar|monto\s+total|grand\s+total|total")
    if total <= 0 and subtotal > 0:
        total = round(subtotal + taxes, 2)
    if subtotal <= 0 and total > 0:
        subtotal = round(max(total - taxes, 0), 2)
    return {
        "invoice_number": invoice_number[:90],
        "issue_date": _parse_date(date_raw),
        "provider_name": (provider_name or "Proveedor no identificado")[:180],
        "provider_nit": (nit or "CF")[:40].upper(),
        "subtotal": subtotal,
        "taxes": taxes,
        "total": total,
    }

import re
from datetime import date

from sqlalchemy.orm import Session

from app.models.entities import Invoice


def validate_invoice_data(db: Session, data: dict, current_invoice_id: int | None = None) -> list[str]:
    errors: list[str] = []
    invoice_number = str(data.get("invoice_number") or "").strip()
    provider_name = str(data.get("provider_name") or "").strip()
    nit = str(data.get("provider_nit") or "").strip().upper()
    if not invoice_number or invoice_number == "SIN-NUMERO":
        errors.append("Campo obligatorio faltante: invoice_number")
    if not provider_name or provider_name.lower() == "proveedor no identificado":
        errors.append("Campo obligatorio faltante: provider_name")
    if not nit:
        errors.append("Campo obligatorio faltante: provider_nit")
    if not isinstance(data.get("issue_date"), date):
        errors.append("La fecha no tiene un formato valido")

    subtotal = float(data.get("subtotal") or 0)
    taxes = float(data.get("taxes") or 0)
    total = float(data.get("total") or 0)
    if subtotal < 0 or taxes < 0:
        errors.append("Subtotal e impuestos deben ser montos no negativos")
    if total <= 0:
        errors.append("El total debe ser mayor que cero")
    if subtotal > 0 and abs((subtotal + taxes) - total) > 0.10:
        errors.append("El total no coincide con subtotal mas impuestos")
    if nit != "CF" and not re.fullmatch(r"[0-9]{5,12}-?[0-9K]", nit):
        errors.append("El NIT no tiene un formato razonablemente valido")

    duplicate_query = db.query(Invoice).filter(
        Invoice.invoice_number == invoice_number,
        Invoice.provider_name == provider_name,
        Invoice.total == total,
    )
    if current_invoice_id is not None:
        duplicate_query = duplicate_query.filter(Invoice.id != current_invoice_id)
    if duplicate_query.first():
        errors.append("Factura duplicada por numero, proveedor y total")
    return errors

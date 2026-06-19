import re
from datetime import date

from sqlalchemy.orm import Session

from app.models.entities import Invoice


def validate_invoice_data(db: Session, data: dict, current_invoice_id: int | None = None) -> list[str]:
    errors: list[str] = []
    required = ["invoice_number", "provider_name", "provider_nit"]
    for field in required:
        if not str(data.get(field) or "").strip():
            errors.append(f"Campo obligatorio faltante: {field}")
    if not isinstance(data.get("issue_date"), date):
        errors.append("La fecha no tiene un formato valido")
    if float(data.get("total") or 0) <= 0:
        errors.append("El total debe ser mayor que cero")
    nit = str(data.get("provider_nit") or "")
    if nit.upper() != "CF" and not re.fullmatch(r"[0-9]{5,12}-?[0-9K]", nit.upper()):
        errors.append("El NIT no tiene un formato razonablemente valido")

    duplicate_query = db.query(Invoice).filter(
        Invoice.invoice_number == data.get("invoice_number"),
        Invoice.provider_name == data.get("provider_name"),
        Invoice.total == float(data.get("total") or 0),
    )
    if current_invoice_id is not None:
        duplicate_query = duplicate_query.filter(Invoice.id != current_invoice_id)
    if duplicate_query.first():
        errors.append("Factura duplicada por numero, proveedor y total")
    return errors

from datetime import date

from app.database.session import SessionLocal
from app.services.invoice_parser import parse_invoice_text
from app.services.validation_service import validate_invoice_data


OCR_SAMPLE = """
FACTURA                         FAC-00005
Proveedor: Hotel Llobet S.Coop.
NIT: 4322338-2
Fecha: 30/12/2025
Cant. Descripcion Precio Total
4 Manual Q 86.67 Q 346.68
Subtotal: Q 2386.15
IVA 12%: Q 286.34
TOTAL: Q 2672.49
"""


def test_parser_extracts_required_fields_and_final_total(client):
    data = parse_invoice_text(OCR_SAMPLE, "factura_005.png")
    assert data == {
        "invoice_number": "FAC-00005",
        "issue_date": date(2025, 12, 30),
        "provider_name": "Hotel Llobet S.Coop.",
        "provider_nit": "4322338-2",
        "subtotal": 2386.15,
        "taxes": 286.34,
        "total": 2672.49,
    }
    with SessionLocal() as db:
        assert validate_invoice_data(db, data) == []


def test_validation_rejects_inconsistent_amounts(client):
    data = parse_invoice_text(OCR_SAMPLE, "factura_005.png")
    data["total"] = 10
    with SessionLocal() as db:
        errors = validate_invoice_data(db, data)
    assert "El total no coincide con subtotal mas impuestos" in errors

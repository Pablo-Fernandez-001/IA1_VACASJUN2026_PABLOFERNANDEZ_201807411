import csv
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.entities import Invoice, Report


def _report_dir() -> Path:
    path = Path(settings.report_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def generate_csv(db: Session, username: str = "system") -> Path:
    target = _report_dir() / f"reporte_facturas_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    invoices = db.query(Invoice).order_by(Invoice.created_at.desc()).all()
    with target.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["id", "numero", "fecha", "proveedor", "nit", "subtotal", "impuestos", "total", "estado"])
        for invoice in invoices:
            writer.writerow(
                [
                    invoice.id,
                    invoice.invoice_number,
                    invoice.issue_date or "",
                    invoice.provider_name,
                    invoice.provider_nit,
                    invoice.subtotal,
                    invoice.taxes,
                    invoice.total,
                    invoice.status,
                ]
            )
    db.add(Report(report_type="csv", file_path=str(target), generated_by=username))
    db.commit()
    return target


def generate_pdf(db: Session, username: str = "system") -> Path:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

    target = _report_dir() / f"reporte_facturas_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
    invoices = db.query(Invoice).order_by(Invoice.created_at.desc()).limit(80).all()
    rows = [["No.", "Fecha", "Proveedor", "NIT", "Total", "Estado"]]
    rows.extend(
        [
            invoice.invoice_number,
            str(invoice.issue_date or ""),
            invoice.provider_name[:28],
            invoice.provider_nit,
            f"Q {invoice.total:.2f}",
            invoice.status,
        ]
        for invoice in invoices
    )
    document = SimpleDocTemplate(str(target), pagesize=letter, title="Reporte SmartInvoice")
    table = Table(rows, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1d4ed8")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5e1")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ]
        )
    )
    document.build([table])
    db.add(Report(report_type="pdf", file_path=str(target), generated_by=username))
    db.commit()
    return target

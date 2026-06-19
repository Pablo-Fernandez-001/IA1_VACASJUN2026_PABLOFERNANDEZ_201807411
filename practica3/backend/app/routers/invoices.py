import json
import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_current_user
from app.database.session import get_db
from app.models.entities import Invoice, ProcessingLog, Provider, RpaRun, User
from app.schemas.dto import InvoiceOut
from app.services.invoice_parser import parse_invoice_text
from app.services.ocr_service import extract_text
from app.services.rpa_service import register_invoice_in_form
from app.services.validation_service import validate_invoice_data
from app.utils.files import safe_upload_path

router = APIRouter(prefix="/api/invoices", tags=["invoices"])


def _ensure_provider(db: Session, data: dict) -> Provider | None:
    nit = data.get("provider_nit") or "CF"
    provider = db.query(Provider).filter(Provider.nit == nit).first()
    if provider:
        return provider
    if data.get("provider_name") and nit:
        provider = Provider(name=data["provider_name"], nit=nit)
        db.add(provider)
        db.flush()
        return provider
    return None


def _create_invoice_from_file(db: Session, current_user: User, target: Path, original_name: str) -> Invoice:
    raw_text = extract_text(str(target))
    data = parse_invoice_text(raw_text, original_name)
    errors = validate_invoice_data(db, data)
    provider = _ensure_provider(db, data)
    invoice = Invoice(
        **data,
        status="Procesado" if not errors else "Rechazado",
        file_name=original_name,
        file_path=str(target),
        raw_text=raw_text,
        validation_errors=json.dumps(errors, ensure_ascii=False),
        user_id=current_user.id,
        provider_id=provider.id if provider else None,
    )
    db.add(invoice)
    db.flush()
    db.add(
        ProcessingLog(
            username=current_user.username,
            document_name=invoice.file_name,
            status=invoice.status,
            result="; ".join(errors) if errors else "Factura procesada y almacenada correctamente",
            invoice_id=invoice.id,
        )
    )
    db.commit()
    db.refresh(invoice)
    return invoice


@router.post("/upload", response_model=InvoiceOut)
def upload_invoice(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    target = safe_upload_path(settings.upload_dir, file)
    with target.open("wb") as destination:
        shutil.copyfileobj(file.file, destination)
    try:
        return _create_invoice_from_file(db, current_user, target, file.filename or target.name)
    except Exception as exc:
        db.add(
            ProcessingLog(
                username=current_user.username,
                document_name=file.filename or target.name,
                status="Error",
                result=str(exc),
            )
        )
        db.commit()
        raise HTTPException(status_code=500, detail=f"No se pudo procesar la factura: {exc}") from exc


@router.get("", response_model=list[InvoiceOut])
def list_invoices(_: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Invoice).order_by(Invoice.created_at.desc()).all()


@router.get("/{invoice_id}", response_model=InvoiceOut)
def get_invoice(invoice_id: int, _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    invoice = db.get(Invoice, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return invoice


@router.post("/{invoice_id}/validate", response_model=InvoiceOut)
def validate_invoice(invoice_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    invoice = db.get(Invoice, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    data = {
        "invoice_number": invoice.invoice_number,
        "issue_date": invoice.issue_date,
        "provider_name": invoice.provider_name,
        "provider_nit": invoice.provider_nit,
        "total": invoice.total,
    }
    errors = validate_invoice_data(db, data, current_invoice_id=invoice.id)
    invoice.validation_errors = json.dumps(errors, ensure_ascii=False)
    invoice.status = "Procesado" if not errors else "Rechazado"
    db.add(
        ProcessingLog(
            username=current_user.username,
            document_name=invoice.file_name,
            status=invoice.status,
            result="Validacion manual ejecutada" if not errors else "; ".join(errors),
            invoice_id=invoice.id,
        )
    )
    db.commit()
    db.refresh(invoice)
    return invoice


@router.post("/{invoice_id}/rpa-register")
def rpa_register(invoice_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    invoice = db.get(Invoice, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    result = register_invoice_in_form(invoice)
    run = RpaRun(invoice_id=invoice.id, status=result["status"], target_url=result["target_url"], result=result["result"])
    db.add(run)
    db.add(
        ProcessingLog(
            username=current_user.username,
            document_name=invoice.file_name,
            status=result["status"],
            result=f"RPA formulario: {result['result']}",
            invoice_id=invoice.id,
        )
    )
    db.commit()
    return {"id": run.id, **result}


@router.post("/seed-demo")
def seed_from_dataset(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    dataset = Path(__file__).resolve().parents[3] / "data" / "facturas_generadas"
    processed = []
    for source in sorted(dataset.glob("factura_*.*")):
        processed.append(_create_invoice_from_file(db, current_user, source, source.name).id)
    return {"processed": processed, "total": len(processed)}

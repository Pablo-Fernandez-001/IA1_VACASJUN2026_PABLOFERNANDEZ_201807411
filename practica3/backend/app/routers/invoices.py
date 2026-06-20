import json
import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_current_user
from app.database.session import get_db
from app.models.entities import Invoice, ProcessingLog, Provider, User
from app.schemas.dto import InvoiceOut, RejectInvoiceRequest, RpaRunOut
from app.services.invoice_parser import parse_invoice_text
from app.services.ocr_service import extract_text, has_meaningful_ocr_text
from app.services.rpa_service import run_and_persist
from app.services.validation_service import validate_invoice_data
from app.utils.files import safe_storage_path, safe_upload_path

router = APIRouter(prefix="/api/invoices", tags=["invoices"])


def _get_invoice(db: Session, invoice_id: int) -> Invoice:
    invoice = db.get(Invoice, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return invoice


def _add_log(
    db: Session,
    user: User,
    invoice: Invoice,
    status: str,
    result: str,
    error_detail: str = "",
) -> None:
    db.add(
        ProcessingLog(
            username=user.username,
            user_id=user.id,
            document_name=invoice.file_name,
            status=status,
            result=result,
            error_detail=error_detail,
            invoice_id=invoice.id,
        )
    )


def _ensure_provider(db: Session, data: dict) -> Provider | None:
    nit = str(data.get("provider_nit") or "").upper()
    name = str(data.get("provider_name") or "")
    if not nit or nit == "CF" or name.lower() == "proveedor no identificado":
        return None
    provider = db.query(Provider).filter(Provider.nit == nit).first()
    if provider:
        return provider
    provider = Provider(name=name, nit=nit)
    db.add(provider)
    db.flush()
    return provider


def _process_existing_invoice(db: Session, user: User, invoice: Invoice, action: str) -> Invoice:
    try:
        raw_text = extract_text(invoice.file_path, evidence_prefix=f"invoice_{invoice.id}_{Path(invoice.file_name).stem}")
        data = parse_invoice_text(raw_text, invoice.file_name)
        errors = validate_invoice_data(db, data, current_invoice_id=invoice.id)
        provider = _ensure_provider(db, data)
        for field, value in data.items():
            setattr(invoice, field, value)
        invoice.provider_id = provider.id if provider else None
        invoice.raw_text = raw_text
        invoice.validation_errors = json.dumps(errors, ensure_ascii=False)
        if not has_meaningful_ocr_text(raw_text):
            invoice.status = "Error"
            result = "OCR no produjo texto util"
        elif errors:
            invoice.status = "Rechazado"
            result = "; ".join(errors)
        else:
            invoice.status = "Procesado"
            result = "Factura procesada, validada y almacenada correctamente"
        _add_log(db, user, invoice, invoice.status, f"{action}: {result}", result if invoice.status == "Error" else "")
        db.commit()
        db.refresh(invoice)
        return invoice
    except Exception as exc:
        invoice.status = "Error"
        invoice.validation_errors = json.dumps([str(exc)], ensure_ascii=False)
        _add_log(db, user, invoice, "Error", f"{action} fallo", str(exc))
        db.commit()
        raise HTTPException(status_code=500, detail=f"No se pudo procesar la factura: {exc}") from exc


@router.post("/upload", response_model=InvoiceOut, status_code=201)
def upload_invoice(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        target = safe_upload_path(settings.upload_dir, file)
    except HTTPException as exc:
        db.add(
            ProcessingLog(
                username=current_user.username,
                user_id=current_user.id,
                document_name=file.filename or "archivo_sin_nombre",
                status="Error",
                result="Carga rechazada por formato invalido",
                error_detail=str(exc.detail),
            )
        )
        db.commit()
        raise
    try:
        with target.open("wb") as destination:
            shutil.copyfileobj(file.file, destination)
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"No se pudo guardar el archivo: {exc}") from exc
    invoice = Invoice(
        invoice_number=f"PENDIENTE-{target.stem[-10:]}",
        issue_date=None,
        provider_name="Proveedor no identificado",
        provider_nit="CF",
        subtotal=0,
        taxes=0,
        total=0,
        status="Pendiente",
        file_name=file.filename or target.name,
        file_path=str(target),
        raw_text="",
        validation_errors="[]",
        user_id=current_user.id,
    )
    db.add(invoice)
    db.flush()
    _add_log(db, current_user, invoice, "Pendiente", "Documento cargado; procesamiento iniciado")
    db.commit()
    db.refresh(invoice)
    return _process_existing_invoice(db, current_user, invoice, "Procesamiento inicial")


@router.get("", response_model=list[InvoiceOut])
def list_invoices(
    status: str | None = Query(default=None),
    search: str | None = Query(default=None, max_length=120),
    limit: int = Query(default=200, ge=1, le=500),
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Invoice)
    if status:
        query = query.filter(Invoice.status == status)
    if search:
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(Invoice.invoice_number.ilike(term), Invoice.provider_name.ilike(term), Invoice.provider_nit.ilike(term))
        )
    return query.order_by(Invoice.created_at.desc()).limit(limit).all()


@router.post("/seed-demo")
def seed_from_dataset(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    dataset = Path(settings.dataset_dir)
    if not dataset.exists():
        raise HTTPException(status_code=404, detail="Dataset de facturas no encontrado")
    processed: list[dict] = []
    for source in sorted(dataset.glob("factura_*.*")):
        target = safe_storage_path(settings.upload_dir, source.name)
        shutil.copy2(source, target)
        invoice = Invoice(
            invoice_number=f"PENDIENTE-{target.stem[-10:]}",
            provider_name="Proveedor no identificado",
            provider_nit="CF",
            subtotal=0,
            taxes=0,
            total=0,
            status="Pendiente",
            file_name=source.name,
            file_path=str(target),
            raw_text="",
            validation_errors="[]",
            user_id=current_user.id,
        )
        db.add(invoice)
        db.flush()
        _add_log(db, current_user, invoice, "Pendiente", "Documento del dataset cargado")
        db.commit()
        db.refresh(invoice)
        result = _process_existing_invoice(db, current_user, invoice, "Procesamiento de dataset")
        processed.append({"id": result.id, "file": source.name, "status": result.status})
    return {"processed": processed, "total": len(processed)}


@router.get("/{invoice_id}", response_model=InvoiceOut)
def get_invoice(invoice_id: int, _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _get_invoice(db, invoice_id)


@router.get("/{invoice_id}/file")
def download_original(invoice_id: int, _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    invoice = _get_invoice(db, invoice_id)
    path = Path(invoice.file_path)
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Archivo original no disponible")
    return FileResponse(path, filename=invoice.file_name)


@router.post("/{invoice_id}/process", response_model=InvoiceOut)
def process_invoice(invoice_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _process_existing_invoice(db, user, _get_invoice(db, invoice_id), "Procesamiento solicitado")


@router.post("/{invoice_id}/reprocess", response_model=InvoiceOut)
def reprocess_invoice(invoice_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _process_existing_invoice(db, user, _get_invoice(db, invoice_id), "Reproceso solicitado")


@router.post("/{invoice_id}/validate", response_model=InvoiceOut)
def validate_invoice(invoice_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    invoice = _get_invoice(db, invoice_id)
    data = {
        "invoice_number": invoice.invoice_number,
        "issue_date": invoice.issue_date,
        "provider_name": invoice.provider_name,
        "provider_nit": invoice.provider_nit,
        "subtotal": invoice.subtotal,
        "taxes": invoice.taxes,
        "total": invoice.total,
    }
    errors = validate_invoice_data(db, data, current_invoice_id=invoice.id)
    invoice.validation_errors = json.dumps(errors, ensure_ascii=False)
    invoice.status = "Procesado" if not errors else "Rechazado"
    _add_log(db, user, invoice, invoice.status, "Validacion manual correcta" if not errors else "; ".join(errors))
    db.commit()
    db.refresh(invoice)
    return invoice


@router.post("/{invoice_id}/reject", response_model=InvoiceOut)
def reject_invoice(
    invoice_id: int,
    payload: RejectInvoiceRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    invoice = _get_invoice(db, invoice_id)
    invoice.status = "Rechazado"
    try:
        errors = json.loads(invoice.validation_errors or "[]")
    except json.JSONDecodeError:
        errors = []
    errors.append(payload.reason)
    invoice.validation_errors = json.dumps(errors, ensure_ascii=False)
    _add_log(db, user, invoice, "Rechazado", payload.reason)
    db.commit()
    db.refresh(invoice)
    return invoice


@router.post("/{invoice_id}/rpa-register", response_model=RpaRunOut, deprecated=True)
def legacy_rpa_register(invoice_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return run_and_persist(db, _get_invoice(db, invoice_id), user)

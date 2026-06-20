from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_current_user
from app.database.session import get_db
from app.models.entities import Invoice, RpaRun, User
from app.schemas.dto import RpaRunOut
from app.services.rpa_service import run_and_persist

router = APIRouter(prefix="/api/rpa", tags=["rpa"])


@router.post("/invoices/{invoice_id}/register", response_model=RpaRunOut)
def register_invoice(invoice_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    invoice = db.get(Invoice, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return run_and_persist(db, invoice, user)


@router.get("/runs", response_model=list[RpaRunOut])
def list_runs(
    invoice_id: int | None = Query(default=None),
    status: str | None = Query(default=None),
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(RpaRun)
    if invoice_id is not None:
        query = query.filter(RpaRun.invoice_id == invoice_id)
    if status:
        query = query.filter(RpaRun.status == status)
    return query.order_by(RpaRun.created_at.desc()).limit(300).all()


@router.get("/runs/{run_id}", response_model=RpaRunOut)
def get_run(run_id: int, _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    run = db.get(RpaRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Ejecucion RPA no encontrada")
    return run


@router.get("/runs/{run_id}/evidence")
def download_evidence(run_id: int, _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    run = db.get(RpaRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Ejecucion RPA no encontrada")
    path = Path(run.evidence_path).resolve()
    evidence_root = Path(settings.rpa_evidence_dir).resolve()
    if evidence_root not in path.parents or not path.is_file():
        raise HTTPException(status_code=404, detail="Evidencia RPA no disponible")
    return FileResponse(path, filename=path.name)

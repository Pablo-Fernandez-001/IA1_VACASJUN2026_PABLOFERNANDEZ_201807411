from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.session import get_db
from app.models.entities import ProcessingLog, User
from app.schemas.dto import LogOut

router = APIRouter(prefix="/api/logs", tags=["logs"])


@router.get("", response_model=list[LogOut])
def list_logs(
    status: str | None = Query(default=None),
    invoice_id: int | None = Query(default=None),
    search: str | None = Query(default=None, max_length=120),
    limit: int = Query(default=300, ge=1, le=1000),
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(ProcessingLog)
    if status:
        query = query.filter(ProcessingLog.status == status)
    if invoice_id is not None:
        query = query.filter(ProcessingLog.invoice_id == invoice_id)
    if search:
        term = f"%{search.strip()}%"
        query = query.filter(or_(ProcessingLog.document_name.ilike(term), ProcessingLog.result.ilike(term)))
    return query.order_by(ProcessingLog.created_at.desc()).limit(limit).all()


@router.get("/{log_id}", response_model=LogOut)
def get_log(log_id: int, _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    log = db.get(ProcessingLog, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Registro de bitacora no encontrado")
    return log

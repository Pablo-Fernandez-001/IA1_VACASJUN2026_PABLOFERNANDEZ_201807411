from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.session import get_db
from app.models.entities import Invoice, ProcessingLog, Provider, Report, RpaRun, User

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/metrics")
def metrics(_: User = Depends(get_current_user), db: Session = Depends(get_db)):
    by_status = dict(db.query(Invoice.status, func.count(Invoice.id)).group_by(Invoice.status).all())
    return {
        "providers": db.query(Provider).count(),
        "invoices": db.query(Invoice).count(),
        "total_amount": round(db.query(func.coalesce(func.sum(Invoice.total), 0)).scalar() or 0, 2),
        "logs": db.query(ProcessingLog).count(),
        "reports": db.query(Report).count(),
        "rpa_runs": db.query(RpaRun).count(),
        "by_status": by_status,
    }

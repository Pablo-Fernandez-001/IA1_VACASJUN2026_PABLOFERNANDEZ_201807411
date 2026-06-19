from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.session import get_db
from app.models.entities import ProcessingLog, User
from app.schemas.dto import LogOut

router = APIRouter(prefix="/api/logs", tags=["logs"])


@router.get("", response_model=list[LogOut])
def list_logs(_: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(ProcessingLog).order_by(ProcessingLog.created_at.desc()).limit(300).all()

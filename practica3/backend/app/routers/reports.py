from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.session import get_db
from app.models.entities import Report, User
from app.schemas.dto import EmailReportRequest
from app.services.email_service import send_report
from app.services.report_service import generate_csv, generate_pdf

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/csv")
def report_csv(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    path = generate_csv(db, current_user.username)
    return FileResponse(path, filename=path.name, media_type="text/csv")


@router.get("/pdf")
def report_pdf(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    path = generate_pdf(db, current_user.username)
    return FileResponse(path, filename=path.name, media_type="application/pdf")


@router.post("/email")
def email_report(payload: EmailReportRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    path = generate_pdf(db, current_user.username) if payload.report_type == "pdf" else generate_csv(db, current_user.username)
    result = send_report(str(payload.recipient), path)
    report = db.query(Report).filter(Report.file_path == str(path)).order_by(Report.id.desc()).first()
    if report:
        report.emailed_to = str(payload.recipient)
        report.email_status = result["status"]
        db.commit()
    return result

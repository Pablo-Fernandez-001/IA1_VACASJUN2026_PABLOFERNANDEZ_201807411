from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.session import get_db
from app.models.entities import ProcessingLog, Report, User
from app.schemas.dto import EmailReportRequest
from app.services.email_service import send_report
from app.services.report_service import generate_csv, generate_pdf

router = APIRouter(prefix="/api/reports", tags=["reports"])


def _log_report(db: Session, user: User, status: str, result: str, error: str = "") -> None:
    db.add(
        ProcessingLog(
            username=user.username,
            user_id=user.id,
            document_name="reporte_administrativo",
            status=status,
            result=result,
            error_detail=error,
        )
    )
    db.commit()


@router.get("")
def list_reports(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    reports = db.query(Report).order_by(Report.created_at.desc()).limit(200).all()
    return [
        {
            "id": report.id,
            "created_at": report.created_at,
            "report_type": report.report_type,
            "file_path": report.file_path,
            "generated_by": report.generated_by,
            "emailed_to": report.emailed_to,
            "email_status": report.email_status,
            "sent_by_email": report.sent_by_email,
        }
        for report in reports
    ]


@router.get("/csv")
def report_csv(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    path = generate_csv(db, current_user.username)
    _log_report(db, current_user, "Procesado", f"Reporte CSV generado: {path.name}")
    return FileResponse(path, filename=path.name, media_type="text/csv")


@router.get("/pdf")
def report_pdf(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    path = generate_pdf(db, current_user.username)
    _log_report(db, current_user, "Procesado", f"Reporte PDF generado: {path.name}")
    return FileResponse(path, filename=path.name, media_type="application/pdf")


@router.post("/email")
def email_report(payload: EmailReportRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        path = generate_pdf(db, current_user.username) if payload.report_type == "pdf" else generate_csv(db, current_user.username)
        result = send_report(payload.recipient, path)
        report = db.query(Report).filter(Report.file_path == str(path)).order_by(Report.id.desc()).first()
        if report:
            report.emailed_to = payload.recipient
            report.email_status = result["status"]
            report.sent_by_email = result["status"] == "sent"
        _log_report(db, current_user, "Procesado", f"Correo {result['status']}: {result['detail']}")
        return result
    except Exception as exc:
        db.rollback()
        _log_report(db, current_user, "Error", "Fallo el envio de reporte", str(exc))
        raise HTTPException(status_code=500, detail=f"No se pudo enviar el reporte: {exc}") from exc

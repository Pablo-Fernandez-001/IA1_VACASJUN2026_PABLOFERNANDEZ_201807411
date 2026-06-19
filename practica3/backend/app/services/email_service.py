import smtplib
from email.message import EmailMessage
from pathlib import Path

from app.core.config import settings


def send_report(recipient: str, report_path: Path) -> dict:
    if not settings.smtp_host or not settings.smtp_user or not settings.smtp_password:
        demo_path = report_path.with_suffix(report_path.suffix + ".email_demo.txt")
        demo_path.write_text(
            f"Modo demo de correo\nPara: {recipient}\nAdjunto: {report_path.name}\n",
            encoding="utf-8",
        )
        return {"status": "demo", "detail": f"Credenciales SMTP ausentes. Evidencia: {demo_path}"}

    message = EmailMessage()
    message["Subject"] = "Reporte SmartInvoice"
    message["From"] = settings.smtp_from
    message["To"] = recipient
    message.set_content("Adjunto se envia el reporte administrativo generado por SmartInvoice.")
    message.add_attachment(
        report_path.read_bytes(),
        maintype="application",
        subtype="octet-stream",
        filename=report_path.name,
    )
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as smtp:
        if settings.smtp_tls:
            smtp.starttls()
        smtp.login(settings.smtp_user, settings.smtp_password)
        smtp.send_message(message)
    return {"status": "sent", "detail": f"Reporte enviado a {recipient}"}

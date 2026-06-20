from pathlib import Path

from app.models.entities import Invoice
from app.database.session import SessionLocal
from app.services import rpa_service


def test_health_auth_and_provider_crud(client, auth_headers):
    health = client.get("/api/health")
    assert health.status_code == 200
    assert health.json()["database"] == "connected"
    created = client.post(
        "/api/providers",
        headers=auth_headers,
        json={"name": "Proveedor QA", "nit": "1234567-8", "email": "qa@example.com", "category": "Pruebas"},
    )
    assert created.status_code == 200
    provider_id = created.json()["id"]
    assert client.get(f"/api/providers/{provider_id}", headers=auth_headers).status_code == 200
    updated = client.put(
        f"/api/providers/{provider_id}",
        headers=auth_headers,
        json={"name": "Proveedor QA Editado", "nit": "1234567-8", "email": "qa@example.com", "category": "Pruebas"},
    )
    assert updated.json()["name"] == "Proveedor QA Editado"
    assert client.delete(f"/api/providers/{provider_id}", headers=auth_headers).status_code == 200


def test_invalid_upload_and_invoice_workflow(client, auth_headers):
    invalid = client.post(
        "/api/invoices/upload",
        headers=auth_headers,
        files={"file": ("factura.txt", b"contenido", "text/plain")},
    )
    assert invalid.status_code == 400

    with SessionLocal() as db:
        invoice = Invoice(
            invoice_number="FAC-TEST-1",
            issue_date=None,
            provider_name="Proveedor QA",
            provider_nit="1234567-8",
            subtotal=100,
            taxes=12,
            total=112,
            status="Pendiente",
            file_name="factura_test.png",
            file_path=str(Path(__file__)),
            raw_text="texto de prueba",
            validation_errors="[]",
            user_id=1,
        )
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        invoice_id = invoice.id

    detail = client.get(f"/api/invoices/{invoice_id}", headers=auth_headers)
    assert detail.status_code == 200
    rejected = client.post(
        f"/api/invoices/{invoice_id}/reject",
        headers=auth_headers,
        json={"reason": "Documento ilegible"},
    )
    assert rejected.json()["status"] == "Rechazado"
    logs = client.get(f"/api/logs?invoice_id={invoice_id}", headers=auth_headers).json()
    assert logs and logs[0]["status"] == "Rechazado"


def test_csv_report_and_demo_email(client, auth_headers):
    csv_response = client.get("/api/reports/csv", headers=auth_headers)
    assert csv_response.status_code == 200
    assert "text/csv" in csv_response.headers["content-type"]
    pdf_response = client.get("/api/reports/pdf", headers=auth_headers)
    assert pdf_response.status_code == 200
    assert "application/pdf" in pdf_response.headers["content-type"]
    assert pdf_response.content.startswith(b"%PDF")
    email = client.post(
        "/api/reports/email",
        headers=auth_headers,
        json={"recipient": "evaluador@example.com", "report_type": "csv"},
    )
    assert email.status_code == 200
    assert email.json()["status"] in {"demo", "sent"}


def test_rpa_endpoint_persists_evidence_reference(client, auth_headers, monkeypatch, tmp_path):
    evidence = tmp_path / "rpa.png"
    evidence.write_bytes(b"png")
    monkeypatch.setattr(
        rpa_service,
        "register_invoice_in_form",
        lambda invoice: {
            "status": "Procesado",
            "target_url": "http://frontend/rpa_form.html",
            "evidence_path": str(evidence),
            "result": "Formulario completado",
        },
    )
    with SessionLocal() as db:
        invoice = Invoice(
            invoice_number="FAC-RPA-1",
            provider_name="Proveedor RPA",
            provider_nit="7654321-0",
            subtotal=100,
            taxes=12,
            total=112,
            status="Procesado",
            file_name="rpa.png",
            file_path=str(evidence),
            raw_text="texto suficiente para una factura de prueba",
            validation_errors="[]",
            user_id=1,
        )
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        invoice_id = invoice.id
    response = client.post(f"/api/rpa/invoices/{invoice_id}/register", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "Procesado"
    assert response.json()["evidence_path"] == str(evidence)

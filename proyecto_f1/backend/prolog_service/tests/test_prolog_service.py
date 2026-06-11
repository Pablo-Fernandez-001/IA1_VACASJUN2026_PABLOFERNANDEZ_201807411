from fastapi.testclient import TestClient
import pytest
from app.main import app

client = TestClient(app)

DIAGNOSIS_CASES = [
    (["no_enciende", "sin_led"], "fuente_poder_danada"),
    (["beeps_arranque", "pantalla_azul", "reinicios_inesperados"], "falla_ram"),
    (["pantalla_negra", "ventiladores_giran"], "falla_video_gpu"),
    (["sobrecalentamiento", "ruido_ventilador", "apagones_repentinos"], "sobrecalentamiento_cpu"),
    (["no_detecta_disco", "disco_100", "lentitud_general"], "disco_danado"),
    (["error_sistema_operativo", "actualizacion_fallida"], "sistema_operativo_corrupto"),
    (["virus_popups", "lentitud_general", "programas_se_cierran"], "malware"),
    (["no_conecta_wifi", "internet_lento"], "driver_red"),
    (["usb_no_funciona", "teclado_no_responde", "mouse_no_responde"], "puertos_usb_danados"),
    (["bateria_no_carga", "apagones_repentinos"], "bateria_cargador"),
    (["fecha_hora_se_reinicia"], "pila_cmos"),
    (["lentitud_general", "disco_100"], "bajo_rendimiento_general"),
]

def test_health():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['service'] == 'prolog-service'


def test_symptoms_catalog_meets_project_minimum():
    response = client.get("/symptoms")
    assert response.status_code == 200

    symptoms = response.json()["symptoms"]
    assert len(symptoms) >= 15
    assert {"id", "name", "category", "weight"}.issubset(symptoms[0])


def test_diagnose_gpu_failure():
    response = client.post(
        "/diagnose",
        json={"symptoms": ["pantalla_negra", "ventiladores_giran"]},
    )
    assert response.status_code == 200

    top = response.json()["diagnostics"][0]
    assert top["id"] == "falla_video_gpu"
    assert top["score"] >= 45
    assert len(top["recommendations"]) >= 1


def test_diagnose_fallback_when_no_rule_matches():
    response = client.post("/diagnose", json={"symptoms": ["internet_lento"]})
    assert response.status_code == 200

    top = response.json()["diagnostics"][0]
    assert top["id"] == "sin_diagnostico_concluyente"


@pytest.mark.parametrize(("symptoms", "expected_id"), DIAGNOSIS_CASES)
def test_documented_diagnosis_cases(symptoms, expected_id):
    response = client.post("/diagnose", json={"symptoms": symptoms})
    assert response.status_code == 200

    top = response.json()["diagnostics"][0]
    assert top["id"] == expected_id
    assert top["recommendations"]

from app.services.formatters import build_telegram_text


def test_build_telegram_text_contains_top_diagnosis():
    result = {"diagnostics": [{"name": "RAM defectuosa", "category": "Hardware", "severity": "alta", "score": 90, "recommendations": ["Probar memoria RAM"]}]}
    text = build_telegram_text("Pablo", ["pantalla_azul"], result)
    assert "RAM defectuosa" in text
    assert "Pablo" in text

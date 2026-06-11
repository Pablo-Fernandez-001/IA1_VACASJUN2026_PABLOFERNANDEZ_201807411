def build_telegram_text(user_name: str, symptoms: list[str], result: dict) -> str:
    diagnostics = result.get("diagnostics", [])
    top = diagnostics[0] if diagnostics else {}
    lines = [
        "🧠 Doctor Byte - Diagnóstico realizado",
        f"Usuario: {user_name}",
        f"Síntomas seleccionados: {', '.join(symptoms)}",
        "",
    ]
    if top:
        lines.extend([
            f"Diagnóstico principal: {top.get('name', 'No concluyente')}",
            f"Categoría: {top.get('category', 'N/A')}",
            f"Severidad: {top.get('severity', 'N/A')}",
            f"Confianza: {top.get('score', 0)}%",
            "",
            "Recomendaciones:",
        ])
        for rec in top.get("recommendations", []):
            lines.append(f"- {rec}")
    else:
        lines.append("No se encontró diagnóstico concluyente.")
    return "\n".join(lines)

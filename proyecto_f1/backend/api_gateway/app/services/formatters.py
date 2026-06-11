def build_telegram_text(user_name: str, symptoms: list[str], result: dict) -> str:
    diagnostics = result.get("diagnostics", [])
    top = diagnostics[0] if diagnostics else {}
    lines = [
        "Doctor Byte - Diagnostico realizado",
        f"Usuario: {user_name}",
        f"Sintomas seleccionados: {', '.join(symptoms)}",
        "",
    ]
    if top:
        lines.extend([
            f"Diagnostico principal: {top.get('name', 'No concluyente')}",
            f"Categoria: {top.get('category', 'N/A')}",
            f"Severidad: {top.get('severity', 'N/A')}",
            f"Probabilidad diagnostica: {top.get('probability', top.get('score', 0))}%",
            f"Porcentaje de problema: {top.get('problem_percentage', 0)}%",
            f"Probabilidad de efectividad: {top.get('effectiveness_probability', 0)}%",
            "",
            "Ruta de solucion:",
        ])
        for step in top.get("solution_steps", []):
            lines.append(f"- {step}")
        lines.extend(["", "Recomendaciones:"])
        for rec in top.get("recommendations", []):
            lines.append(f"- {rec}")
    else:
        lines.append("No se encontro diagnostico concluyente.")
    return "\n".join(lines)

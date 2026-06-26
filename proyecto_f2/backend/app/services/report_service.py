from __future__ import annotations

import textwrap
from datetime import datetime


PAGE_WIDTH = 595
PAGE_HEIGHT = 842
MARGIN = 36
CONTENT_WIDTH = PAGE_WIDTH - (MARGIN * 2)

COLORS = {
    "ink": (0.098, 0.137, 0.129),
    "muted": (0.408, 0.447, 0.427),
    "line": (0.875, 0.894, 0.867),
    "paper": (1, 1, 1),
    "soft": (0.968, 0.984, 0.972),
    "nav": (0.078, 0.125, 0.118),
    "green": (0.043, 0.420, 0.341),
    "green_soft": (0.875, 0.949, 0.922),
    "lime": (0.796, 0.910, 0.357),
    "amber": (0.957, 0.722, 0.247),
    "red_soft": (0.972, 0.875, 0.863),
}


def _clean(value) -> str:
    text = "" if value is None else str(value)
    return (
        text.replace("→", "->")
        .replace("←", "<-")
        .replace("↑", "arriba")
        .replace("↓", "abajo")
        .replace("×", "x")
        .replace("·", "-")
    )


def _pdf_escape(value) -> str:
    safe = _clean(value).encode("cp1252", "replace").decode("cp1252")
    return safe.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _format_dt(value) -> str:
    if not value:
        return "-"
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if hasattr(value, "isoformat"):
        return value.isoformat(sep=" ", timespec="seconds")
    return str(value)


def _speed_text(speed: dict | None) -> str:
    if not speed:
        return "Normal (650 ms/paso, 1x)"
    return f'{speed.get("label", "Normal")} ({speed.get("interval_ms", 650)} ms/paso, {speed.get("multiplier", 1)}x)'


def _route_text(route: list[dict], limit: int = 7) -> str:
    if not route:
        return "-"
    points = [f'({point.get("x")},{point.get("y")})' for point in route[:limit]]
    if len(route) > limit:
        points.append(f"... +{len(route) - limit}")
    return " -> ".join(points)


def _action_label(action: str) -> str:
    return {
        "mover_arriba": "Mover arriba",
        "mover_abajo": "Mover abajo",
        "mover_izquierda": "Mover izquierda",
        "mover_derecha": "Mover derecha",
        "recoger_paquete": "Recoger paquete",
        "entregar_paquete": "Entregar paquete",
        "esperar": "Esperar",
    }.get(action, action)


class PdfCanvas:
    def __init__(self) -> None:
        self.pages: list[str] = []
        self.commands: list[str] = []
        self.y = PAGE_HEIGHT - MARGIN
        self.page_number = 0
        self.new_page()

    def new_page(self) -> None:
        if self.commands:
            self._footer()
            self.pages.append("\n".join(self.commands))
        self.page_number += 1
        self.commands = []
        self.y = PAGE_HEIGHT - MARGIN
        self._page_background()

    def finish(self) -> bytes:
        self._footer()
        self.pages.append("\n".join(self.commands))
        return self._build_pdf()

    def ensure(self, height: float) -> None:
        if self.y - height < MARGIN + 22:
            self.new_page()

    def _page_background(self) -> None:
        self.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, COLORS["soft"])
        self.rect(MARGIN, MARGIN, CONTENT_WIDTH, PAGE_HEIGHT - (MARGIN * 2), COLORS["paper"], stroke=COLORS["line"])

    def _footer(self) -> None:
        self.text("Smart Warehouse - Analitica", MARGIN, 22, 7, COLORS["muted"], font="bold")
        self.text(f"Pagina {self.page_number}", PAGE_WIDTH - MARGIN - 48, 22, 7, COLORS["muted"])

    def rect(self, x: float, y: float, width: float, height: float, fill, stroke=None, line_width: float = 0.7) -> None:
        if fill is not None:
            self.commands.append(f"q {fill[0]:.3f} {fill[1]:.3f} {fill[2]:.3f} rg {x:.2f} {y:.2f} {width:.2f} {height:.2f} re f Q")
        if stroke is not None:
            self.commands.append(f"q {stroke[0]:.3f} {stroke[1]:.3f} {stroke[2]:.3f} RG {line_width:.2f} w {x:.2f} {y:.2f} {width:.2f} {height:.2f} re S Q")

    def line(self, x1: float, y1: float, x2: float, y2: float, color=COLORS["line"], line_width: float = 0.7) -> None:
        self.commands.append(f"q {color[0]:.3f} {color[1]:.3f} {color[2]:.3f} RG {line_width:.2f} w {x1:.2f} {y1:.2f} m {x2:.2f} {y2:.2f} l S Q")

    def text(self, value, x: float, y: float, size: float = 10, color=COLORS["ink"], font: str = "regular") -> None:
        font_name = "F2" if font == "bold" else "F1"
        self.commands.append(
            f"BT /{font_name} {size:.2f} Tf {color[0]:.3f} {color[1]:.3f} {color[2]:.3f} rg {x:.2f} {y:.2f} Td ({_pdf_escape(value)}) Tj ET"
        )

    def wrapped_text(self, value, x: float, y: float, max_width: float, size: float = 9, color=COLORS["ink"], font: str = "regular", max_lines: int | None = None, leading: float | None = None) -> float:
        chars = max(12, int(max_width / (size * 0.48)))
        lines = textwrap.wrap(_clean(value), width=chars, break_long_words=False) or [""]
        if max_lines and len(lines) > max_lines:
            lines = lines[:max_lines]
            lines[-1] = f"{lines[-1][: max(0, len(lines[-1]) - 3)]}..."
        line_height = leading or (size + 3)
        for index, line in enumerate(lines):
            self.text(line, x, y - (index * line_height), size, color, font)
        return len(lines) * line_height

    def _build_pdf(self) -> bytes:
        objects: list[bytes] = []

        def add_object(payload: str | bytes) -> int:
            objects.append(payload.encode("latin-1") if isinstance(payload, str) else payload)
            return len(objects)

        catalog_id = add_object("<< /Type /Catalog /Pages 2 0 R >>")
        pages_id = add_object(b"")
        regular_font_id = add_object("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
        bold_font_id = add_object("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>")
        page_ids: list[int] = []
        for content in self.pages:
            content_bytes = content.encode("cp1252", "replace")
            content_id = add_object(b"<< /Length " + str(len(content_bytes)).encode("ascii") + b" >>\nstream\n" + content_bytes + b"\nendstream")
            page_id = add_object(
                f"<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 {PAGE_WIDTH} {PAGE_HEIGHT}] "
                f"/Resources << /Font << /F1 {regular_font_id} 0 R /F2 {bold_font_id} 0 R >> >> "
                f"/Contents {content_id} 0 R >>"
            )
            page_ids.append(page_id)
        objects[pages_id - 1] = f"<< /Type /Pages /Kids [{' '.join(f'{page_id} 0 R' for page_id in page_ids)}] /Count {len(page_ids)} >>".encode("latin-1")

        output = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = [0]
        for index, payload in enumerate(objects, start=1):
            offsets.append(len(output))
            output.extend(f"{index} 0 obj\n".encode("ascii"))
            output.extend(payload)
            output.extend(b"\nendobj\n")
        xref_at = len(output)
        output.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
        output.extend(b"0000000000 65535 f \n")
        for offset in offsets[1:]:
            output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
        output.extend(
            f"trailer\n<< /Size {len(objects) + 1} /Root {catalog_id} 0 R >>\nstartxref\n{xref_at}\n%%EOF\n".encode("ascii")
        )
        return bytes(output)


def _section(canvas: PdfCanvas, title: str, kicker: str | None = None) -> None:
    canvas.ensure(42)
    canvas.y -= 18
    if kicker:
        canvas.text(kicker.upper(), MARGIN + 18, canvas.y, 7, COLORS["green"], font="bold")
        canvas.y -= 12
    canvas.text(title, MARGIN + 18, canvas.y, 15, COLORS["ink"], font="bold")
    canvas.y -= 18


def _metric_card(canvas: PdfCanvas, x: float, y_top: float, width: float, title: str, value: str, copy: str) -> None:
    height = 58
    canvas.rect(x, y_top - height, width, height, COLORS["paper"], stroke=COLORS["line"])
    canvas.text(title.upper(), x + 10, y_top - 17, 6.5, COLORS["muted"], font="bold")
    canvas.wrapped_text(value, x + 10, y_top - 34, width - 20, 16, COLORS["ink"], font="bold", max_lines=1)
    canvas.wrapped_text(copy, x + 10, y_top - 47, width - 20, 6.5, COLORS["muted"], max_lines=1)


def _draw_hero(canvas: PdfCanvas, simulation: dict) -> None:
    top = PAGE_HEIGHT - MARGIN
    height = 92
    canvas.rect(MARGIN, top - height, CONTENT_WIDTH, height, COLORS["nav"])
    canvas.rect(MARGIN + 18, top - 32, 34, 22, COLORS["lime"])
    canvas.rect(MARGIN + 62, top - 31, 106, 20, COLORS["green"])
    canvas.text("SMART WAREHOUSE", MARGIN + 67, top - 25, 8, COLORS["paper"], font="bold")
    canvas.text(f'Reporte de corrida #{simulation["id"]}', MARGIN + 18, top - 56, 22, COLORS["paper"], font="bold")
    canvas.wrapped_text(simulation["scenario"], MARGIN + 18, top - 74, 350, 9, (0.760, 0.824, 0.800), max_lines=1)
    canvas.rect(PAGE_WIDTH - MARGIN - 132, top - 62, 112, 30, COLORS["green"])
    canvas.text(simulation["status"].upper(), PAGE_WIDTH - MARGIN - 118, top - 44, 9, COLORS["paper"], font="bold")
    canvas.text("ANALITICA PDF", PAGE_WIDTH - MARGIN - 118, top - 54, 6.5, COLORS["green_soft"], font="bold")
    canvas.y = top - height - 22


def _draw_metrics(canvas: PdfCanvas, data: dict) -> None:
    simulation = data["simulation"]
    analytics = data["analytics"]
    cards = [
        ("Duracion", f'{simulation["duration_seconds"]} s', "Tiempo acumulado"),
        ("Pasos", str(simulation["total_steps"]), "Decisiones registradas"),
        ("Entregas", str(simulation["deliveries"]), f'{analytics["pickups"]} recolecciones'),
        ("Movimientos", str(simulation["moves"]), "Acciones de navegacion"),
        ("Eficiencia", f'{float(simulation["efficiency"]):.2f}%', "Entregas por movimiento"),
        ("Velocidad", f'{simulation.get("speed", {}).get("multiplier", 1)}x', _speed_text(simulation.get("speed"))),
    ]
    card_width = (CONTENT_WIDTH - 24) / 3
    for row in range(2):
        y_top = canvas.y - (row * 70)
        for col in range(3):
            title, value, copy = cards[(row * 3) + col]
            _metric_card(canvas, MARGIN + 18 + (col * (card_width + 12)), y_top, card_width, title, value, copy)
    canvas.y -= 144


def _draw_action_chart(canvas: PdfCanvas, analytics: dict) -> None:
    _section(canvas, "Distribucion de acciones", "trazabilidad")
    entries = sorted(analytics["action_counts"].items(), key=lambda item: item[1], reverse=True)
    if not entries:
        canvas.text("Sin acciones registradas.", MARGIN + 18, canvas.y, 9, COLORS["muted"])
        canvas.y -= 20
        return
    max_count = max(count for _, count in entries) or 1
    for action, count in entries:
        canvas.ensure(24)
        label = _action_label(action)
        canvas.text(label, MARGIN + 18, canvas.y, 8, COLORS["ink"], font="bold")
        canvas.rect(MARGIN + 128, canvas.y - 6, 300, 7, (0.929, 0.941, 0.925))
        canvas.rect(MARGIN + 128, canvas.y - 6, 300 * (count / max_count), 7, COLORS["green"])
        canvas.text(str(count), MARGIN + 438, canvas.y - 1, 8, COLORS["muted"], font="bold")
        canvas.y -= 18


def _draw_configuration(canvas: PdfCanvas, simulation: dict) -> None:
    configuration = simulation.get("initial_configuration") or {}
    _section(canvas, "Configuracion inicial", "escenario")
    canvas.ensure(88)
    summary = [
        ("Mapa", f'{configuration.get("map", {}).get("width", "-")} x {configuration.get("map", {}).get("height", "-")}'),
        ("Paquetes", str(len(configuration.get("packages", [])))),
        ("Estanterias", str(len(configuration.get("obstacles", [])))),
        ("Zonas", str(len(configuration.get("zones", [])))),
    ]
    card_width = (CONTENT_WIDTH - 54) / 4
    for index, (label, value) in enumerate(summary):
        x = MARGIN + 18 + (index * (card_width + 6))
        canvas.rect(x, canvas.y - 44, card_width, 44, COLORS["soft"], stroke=COLORS["line"])
        canvas.text(label.upper(), x + 8, canvas.y - 15, 6.5, COLORS["muted"], font="bold")
        canvas.text(value, x + 8, canvas.y - 31, 13, COLORS["ink"], font="bold")
    canvas.y -= 62
    zones = configuration.get("zones", [])
    packages = configuration.get("packages", [])
    zone_text = ", ".join(f'{zone.get("id")} ({zone.get("x")},{zone.get("y")})' for zone in zones) or "Sin zonas"
    packages_text = ", ".join(f'{package.get("id", "?").upper()}->{package.get("zone")}' for package in packages[:8]) or "Sin paquetes"
    if len(packages) > 8:
        packages_text += f", +{len(packages) - 8}"
    canvas.wrapped_text(f"Zonas: {zone_text}", MARGIN + 18, canvas.y, CONTENT_WIDTH - 36, 8, COLORS["muted"], max_lines=2)
    canvas.y -= 24
    canvas.wrapped_text(f"Paquetes: {packages_text}", MARGIN + 18, canvas.y, CONTENT_WIDTH - 36, 8, COLORS["muted"], max_lines=2)
    canvas.y -= 24


def _draw_speed_trace(canvas: PdfCanvas, analytics: dict, simulation: dict) -> None:
    trace = analytics.get("speed_trace") or [{"speed": simulation.get("speed"), "created_at": simulation.get("started_at")}]
    _section(canvas, "Velocidad de recorrido", "control")
    for item in trace:
        canvas.ensure(20)
        canvas.rect(MARGIN + 18, canvas.y - 12, 8, 8, COLORS["lime"])
        canvas.text(_speed_text(item.get("speed")), MARGIN + 34, canvas.y - 5, 8.5, COLORS["ink"], font="bold")
        canvas.text(f'desde {_format_dt(item.get("created_at"))}', MARGIN + 216, canvas.y - 5, 8, COLORS["muted"])
        canvas.y -= 18


def _draw_steps(canvas: PdfCanvas, data: dict) -> None:
    _section(canvas, "Recorrido paso a paso", "prolog bfs")
    headers = ["Paso", "Accion", "Robot", "Ruta", "Explicacion"]
    widths = [42, 86, 60, 88, CONTENT_WIDTH - 36 - 42 - 86 - 60 - 88]

    def table_header() -> None:
        canvas.ensure(28)
        x = MARGIN + 18
        canvas.rect(x, canvas.y - 20, CONTENT_WIDTH - 36, 20, COLORS["green"])
        for header, width in zip(headers, widths):
            canvas.text(header.upper(), x + 6, canvas.y - 13, 6.5, COLORS["paper"], font="bold")
            x += width
        canvas.y -= 20

    table_header()
    for index, step in enumerate(data["steps"]):
        reason_height = max(22, len(textwrap.wrap(_clean(step["reason"] or "-"), width=58, break_long_words=False)) * 9 + 14)
        row_height = min(reason_height, 70)
        if canvas.y - row_height < MARGIN + 28:
            canvas.new_page()
            _section(canvas, "Recorrido paso a paso", "prolog bfs")
            table_header()
        fill = COLORS["paper"] if index % 2 == 0 else COLORS["soft"]
        x = MARGIN + 18
        canvas.rect(x, canvas.y - row_height, CONTENT_WIDTH - 36, row_height, fill, stroke=COLORS["line"])
        values = [
            f'#{step["step_number"]}',
            _action_label(step["action"]),
            f'({step["robot"].get("x")},{step["robot"].get("y")})',
            f'{step["route_length"]} nodos',
        ]
        for value, width in zip(values, widths[:4]):
            canvas.wrapped_text(value, x + 6, canvas.y - 14, width - 10, 7.5, COLORS["ink"], font="bold", max_lines=2)
            x += width
        explanation = f'{step["reason"] or "-"} | Ruta: {_route_text(step["route"])}'
        canvas.wrapped_text(explanation, x + 6, canvas.y - 14, widths[-1] - 10, 7.2, COLORS["muted"], max_lines=6, leading=9)
        canvas.y -= row_height


def build_analytics_pdf(data: dict) -> bytes:
    canvas = PdfCanvas()
    simulation = data["simulation"]
    _draw_hero(canvas, simulation)
    _draw_metrics(canvas, data)
    _draw_action_chart(canvas, data["analytics"])
    _draw_configuration(canvas, simulation)
    _draw_speed_trace(canvas, data["analytics"], simulation)
    _draw_steps(canvas, data)
    return canvas.finish()

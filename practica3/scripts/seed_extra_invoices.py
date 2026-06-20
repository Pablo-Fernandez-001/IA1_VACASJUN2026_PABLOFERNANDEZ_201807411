from datetime import date, timedelta
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


DATASET_DIR = Path(__file__).resolve().parents[1] / "data" / "facturas_generadas"
PROVIDERS = [
    "Distribuidora Aurora S.A.",
    "Servicios Tecnicos Maya",
    "Papeleria Central S.A.",
    "Logistica del Pacifico",
    "Suministros Altiplano",
    "Comercial La Reforma",
    "Tecnologia Quetzal",
    "Alimentos del Valle",
    "Mantenimiento Integral",
    "Importadora Monja Blanca",
]


def _font(size: int, bold: bool = False):
    names = [
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    for path in names:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def generate_invoice(number: int) -> Path:
    index = number - 11
    subtotal = round(850 + index * 137.45, 2)
    taxes = round(subtotal * 0.12, 2)
    total = round(subtotal + taxes, 2)
    issue_date = date(2026, 1, 5) + timedelta(days=index * 7)
    nit = f"{7100000 + index * 173}-{(index + 1) % 10}"
    target = DATASET_DIR / f"factura_{number:03d}.png"

    image = Image.new("RGB", (900, 1200), "white")
    draw = ImageDraw.Draw(image)
    title = _font(42, bold=True)
    heading = _font(25, bold=True)
    body = _font(23)
    draw.text((55, 55), "FACTURA", fill="black", font=title)
    draw.text((635, 65), f"FAC-{number:05d}", fill="black", font=heading)
    draw.line((55, 125, 845, 125), fill="black", width=2)
    draw.text((55, 175), f"Proveedor: {PROVIDERS[index]}", fill="black", font=body)
    draw.text((55, 220), f"NIT: {nit}", fill="black", font=body)
    draw.text((55, 265), f"Fecha: {issue_date.strftime('%d/%m/%Y')}", fill="black", font=body)
    draw.text((55, 360), "Descripcion", fill="black", font=heading)
    draw.text((520, 360), "Precio", fill="black", font=heading)
    items = [("Insumos administrativos", subtotal * 0.45), ("Servicios profesionales", subtotal * 0.35), ("Transporte y entrega", subtotal * 0.20)]
    y = 420
    for description, amount in items:
        draw.text((55, y), description, fill="black", font=body)
        draw.text((600, y), f"Q {amount:.2f}", fill="black", font=body)
        y += 55
    draw.line((500, 650, 845, 650), fill="black", width=2)
    draw.text((520, 700), "Subtotal:", fill="black", font=body)
    draw.text((700, 700), f"Q {subtotal:.2f}", fill="black", font=body)
    draw.text((520, 755), "IVA 12%:", fill="black", font=body)
    draw.text((700, 755), f"Q {taxes:.2f}", fill="black", font=body)
    draw.text((520, 825), "TOTAL:", fill="black", font=heading)
    draw.text((700, 825), f"Q {total:.2f}", fill="black", font=heading)
    draw.line((55, 1040, 845, 1040), fill="black", width=2)
    draw.text((55, 1080), "Documento sintetico para pruebas academicas de OCR.", fill="black", font=body)
    image.save(target, optimize=True)
    return target


def main() -> None:
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    for old_pdf in DATASET_DIR.glob("factura_01[1-9].pdf"):
        old_pdf.unlink()
    for number in range(11, 21):
        target = generate_invoice(number)
        print(f"generada {target.name}")


if __name__ == "__main__":
    main()

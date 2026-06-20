import re
from pathlib import Path

from app.core.config import settings
from app.services.vision_service import document_to_images, embedded_pdf_text, preprocess_for_ocr


def _safe_prefix(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", value).strip("_")[:80] or "invoice"


def has_meaningful_ocr_text(text: str) -> bool:
    useful = "\n".join(line for line in text.splitlines() if not line.startswith("[OCR") and not line.startswith("[Renderizado"))
    return len(re.sub(r"\W", "", useful)) >= 20


def extract_text(path: str, evidence_prefix: str | None = None) -> str:
    source = Path(path)
    chunks: list[str] = []
    if source.suffix.lower() == ".pdf":
        try:
            embedded = embedded_pdf_text(path)
        except ModuleNotFoundError:
            embedded = ""
        if embedded.strip():
            chunks.append(embedded)
    try:
        import pytesseract
    except ModuleNotFoundError:
        chunks.append("[OCR no disponible: instale pytesseract o use Docker Compose]")
        return "\n".join(chunk.strip() for chunk in chunks if chunk.strip())

    try:
        images = document_to_images(path)
    except ModuleNotFoundError as exc:
        chunks.append(f"[Renderizado no disponible: falta {exc.name}. Use Docker Compose]")
        return "\n".join(chunk.strip() for chunk in chunks if chunk.strip())

    evidence_dir = Path(settings.ocr_evidence_dir)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    prefix = _safe_prefix(evidence_prefix or source.stem)
    for index, image in enumerate(images, start=1):
        prepared = preprocess_for_ocr(image)
        prepared.save(evidence_dir / f"{prefix}_pagina_{index}_preprocesada.png")
        try:
            text = pytesseract.image_to_string(prepared, lang="spa+eng", config="--oem 3 --psm 6")
        except pytesseract.TesseractNotFoundError:
            text = "[OCR no disponible: instale Tesseract o use Docker Compose]"
        except pytesseract.TesseractError as exc:
            text = f"[OCR finalizo con error: {exc}]"
        chunks.append(text)
    result = "\n".join(chunk.strip() for chunk in chunks if chunk.strip())
    (evidence_dir / f"{prefix}_ocr.txt").write_text(result, encoding="utf-8")
    return result

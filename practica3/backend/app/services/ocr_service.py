from pathlib import Path

from app.services.vision_service import document_to_images, embedded_pdf_text, preprocess_for_ocr


def extract_text(path: str) -> str:
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

    for image in images:
        prepared = preprocess_for_ocr(image)
        try:
            text = pytesseract.image_to_string(prepared, lang="spa+eng")
        except pytesseract.TesseractNotFoundError:
            text = "[OCR no disponible: instale Tesseract o use Docker Compose]"
        except pytesseract.TesseractError as exc:
            text = f"[OCR finalizo con error: {exc}]"
        chunks.append(text)
    return "\n".join(chunk.strip() for chunk in chunks if chunk.strip())

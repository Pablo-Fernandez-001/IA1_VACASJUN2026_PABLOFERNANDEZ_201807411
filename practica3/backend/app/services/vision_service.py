from pathlib import Path


def document_to_images(path: str, max_pages: int = 3):
    from PIL import Image

    source = Path(path)
    if source.suffix.lower() == ".pdf":
        import fitz

        images: list[Image.Image] = []
        with fitz.open(source) as doc:
            for page in doc[:max_pages]:
                pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                images.append(Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples))
        return images
    return [Image.open(source).convert("RGB")]


def embedded_pdf_text(path: str, max_pages: int = 3) -> str:
    source = Path(path)
    if source.suffix.lower() != ".pdf":
        return ""
    import fitz

    chunks: list[str] = []
    with fitz.open(source) as doc:
        for page in doc[:max_pages]:
            chunks.append(page.get_text("text"))
    return "\n".join(chunk for chunk in chunks if chunk.strip())


def _deskew(binary, cv2, np):
    points = np.column_stack(np.where(binary < 255))
    if len(points) < 20:
        return binary
    angle = cv2.minAreaRect(points)[-1]
    angle = -(90 + angle) if angle < -45 else -angle
    if abs(angle) < 0.1 or abs(angle) > 15:
        return binary
    height, width = binary.shape[:2]
    matrix = cv2.getRotationMatrix2D((width / 2, height / 2), angle, 1.0)
    return cv2.warpAffine(binary, matrix, (width, height), flags=cv2.INTER_CUBIC, borderValue=255)


def preprocess_for_ocr(image):
    from PIL import Image

    try:
        import cv2
        import numpy as np
    except ModuleNotFoundError:
        return image.convert("L")

    array = np.array(image.convert("RGB"))
    gray = cv2.cvtColor(array, cv2.COLOR_RGB2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    denoised = cv2.medianBlur(binary, 3)
    corrected = _deskew(denoised, cv2, np)
    return Image.fromarray(corrected)

# SmartInvoice - Practica 3 IA1

SmartInvoice procesa facturas PDF/JPG/JPEG/PNG con Computer Vision, OCR local, validacion automatica, base de datos, bitacora, reportes CSV/PDF, correo SMTP/demo y RPA sobre un formulario web simulado.

## Documentacion

Los documentos Markdown de soporte estan en `docs/`:

- `docs/MANUAL_TECNICO.md`
- `docs/MANUAL_USUARIO.md`
- `docs/prompt_practica3.md`
- `docs/recurso_facturas_generadas.md`
- `docs/transcripcion_practica3.md`

## Ejecutar rapido en local

Desde la raiz del repositorio:

```powershell
cd practica3
$env:PYTHONPATH="backend"
$env:DATABASE_URL="sqlite:///./smartinvoice_dev.db"
$env:UPLOAD_DIR="./uploads"
$env:REPORT_DIR="./reports"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8300
```

En otra terminal:

```powershell
cd practica3/frontend
python -m http.server 8311 --bind 127.0.0.1
```

Abrir:

- Frontend: http://127.0.0.1:8311/login.html
- API: http://127.0.0.1:8300/api/health
- Swagger: http://127.0.0.1:8300/docs

Usuario inicial:

- Usuario: `admin`
- Contrasena: `admin123`

## Ejecutar con Docker Compose

```powershell
cd practica3
docker compose up --build
```

Abrir:

- Frontend: http://localhost:8301
- API: http://localhost:8300/api/health
- Swagger: http://localhost:8300/docs

Docker instala Tesseract, OpenCV y Playwright Chromium para OCR/CV/RPA completo.

## Como ver que funciona

1. Entrar al frontend e iniciar sesion con `admin` / `admin123`.
2. Ir a `Proveedores` y crear un proveedor de prueba.
3. Ir a `Facturas`.
4. Subir una factura de `data/facturas_generadas/`, por ejemplo `factura_005.png`.
5. Revisar el estado generado y pulsar `OCR` para ver el texto bruto.
6. Pulsar `Validar` para revalidar campos.
7. Pulsar `RPA` para llenar el formulario web simulado.
8. Ir a `Bitacora` y confirmar que quedaron registros.
9. Ir a `Reportes` y descargar CSV o PDF.

## Dataset

El ZIP `facturas_generadas.zip` fue extraido en:

```text
data/facturas_generadas/
```

El ZIP original traia 10 documentos. Se agrego y ejecuto `scripts/seed_extra_invoices.py` para completar 20 archivos de prueba.

## Estructura

```text
backend/        API FastAPI, modelos y servicios OCR/CV/RPA/reportes
frontend/       panel administrativo HTML/CSS/JS
data/           dataset de facturas de prueba
docs/           manuales, prompt y transcripcion
reports/        reportes generados
uploads/        documentos cargados por usuarios
scripts/        utilidades de seed
```

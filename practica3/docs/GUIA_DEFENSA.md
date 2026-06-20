# Guia rapida para defensa

## Flujo en 60 segundos

El usuario inicia sesion, carga una factura y FastAPI guarda el archivo. OpenCV prepara cada pagina y Tesseract obtiene texto local. Un parser propio extrae campos, las reglas validan montos/NIT/duplicados y SQLAlchemy persiste factura y bitacora. El panel permite revisar, rechazar o reprocesar. ReportLab/CSV generan reportes, SMTP los envia y Playwright registra los datos en un formulario simulado dejando captura.

## Preguntas probables

### 1. Por que Python

Integra FastAPI, OpenCV, Tesseract, SQLAlchemy, ReportLab y Playwright en un solo backend mantenible. Ademas cumple la restriccion del enunciado.

### 2. Donde esta la inteligencia artificial

En Computer Vision y OCR: OpenCV mejora el documento y Tesseract reconoce caracteres. La extraccion posterior usa reglas y heuristicas propias, no IA generativa externa.

### 3. Como evita datos incorrectos

Valida campos obligatorios, fecha, NIT, montos positivos, la suma subtotal+impuestos y duplicados. El resultado queda `Procesado`, `Rechazado` o `Error` con detalle en bitacora.

### 4. Como funciona RPA

Playwright abre el formulario real, llena cinco controles, envia, espera confirmacion y toma captura. El resultado y ruta de evidencia se guardan en `rpa_runs`.

### 5. Que persiste la base de datos

Usuarios, proveedores, facturas, texto OCR, bitacoras, reportes y ejecuciones RPA. PostgreSQL se usa en Docker; SQLite solo facilita desarrollo local.

### 6. Que levanta Docker Compose

PostgreSQL, FastAPI con Tesseract/Chromium y Nginx con el frontend. Los health checks controlan el orden de arranque.

### 7. Que pasa si falla OCR

La factura no desaparece: queda con estado `Error`, texto/error disponible y entrada de bitacora. Luego puede reprocesarse.

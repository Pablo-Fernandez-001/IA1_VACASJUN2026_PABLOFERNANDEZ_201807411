# Checklist 100 puntos - SmartInvoice

## Backend y API REST - 20

- [x] FastAPI y Swagger en `/docs`.
- [x] Routers `auth`, `providers`, `invoices`, `logs`, `reports`, `rpa`, `dashboard`.
- [x] Arquitectura por capas documentada.
- [x] Errores 400, 401, 404, 422 y 500; errores OCR quedan en bitacora.

## Base de datos - 15

- [x] PostgreSQL en Docker Compose y SQLite local justificado.
- [x] Modelo y diagrama ER documentados.
- [x] Persistencia de usuarios, proveedores, facturas, logs, reportes y RPA.

## Panel administrativo - 20

- [x] Login, registro y rutas protegidas por token.
- [x] CRUD completo de proveedores.
- [x] Lista, filtros, detalle, original, OCR, validacion, rechazo y reproceso de facturas.
- [x] Bitacora con filtros, estado, usuario, resultado y error.

## OCR y Computer Vision - 15

- [x] PDF/JPG/JPEG/PNG y rechazo de extensiones invalidas.
- [x] Tesseract local.
- [x] Numero, fecha, proveedor, NIT, subtotal, impuestos y total.
- [x] Escala de grises, Otsu, limpieza, correccion de inclinacion y evidencia.
- [x] Validacion de obligatorios, NIT, montos, suma y duplicados.
- [x] Lote de 20 ejecutado sin errores OCR; dos duplicados previos fueron rechazados correctamente.

## RPA - 10

- [x] Playwright abre y llena el formulario simulado.
- [x] Endpoint y persistencia en `rpa_runs`.
- [x] Captura/recibo automatico descargable.

## Reportes y correo - 5

- [x] CSV y PDF descargables.
- [x] SMTP configurable y modo demo con evidencia.
- [x] Reportes y correos registrados en bitacora.

## Docker y despliegue - 5

- [x] Compose con frontend, backend y PostgreSQL.
- [x] Dockerfile unificado y `render.yaml` preparados para nube.
- [ ] Colocar URL publica real luego de desplegar en la cuenta del estudiante.

## Documentacion y defensa - 10

- [x] Manual tecnico y usuario.
- [x] Diagramas de arquitectura y ER.
- [x] Guia de defensa y preguntas probables.
- [x] Entrega UEDI preparada.

## Penalizaciones

- [x] Backend/OCR/RPA en Python.
- [x] OCR real y local.
- [x] Base SQL real.
- [x] RPA real, no simulado desde Python.
- [x] Sin API generativa para extraer facturas.
- [ ] Confirmar carga final en UEDI.

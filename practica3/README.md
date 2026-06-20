# SmartInvoice - Practica 3 IA1

Plataforma para procesar facturas PDF/JPG/JPEG/PNG mediante Computer Vision, OCR local y RPA. Incluye autenticacion, CRUD de proveedores, validacion, PostgreSQL, bitacora, reportes CSV/PDF, correo SMTP/demo y evidencias automaticas.

## URL publica

**Pendiente de asignar desde la cuenta de nube del estudiante.** La imagen `Dockerfile.cloud` y `render.yaml` estan preparadas; siga `docs/DESPLIEGUE_NUBE.md` y reemplace esta linea con la URL real antes de entregar.

## Inicio con Docker Compose

```powershell
cd practica3
Copy-Item .env.example .env
docker compose up --build -d
docker compose ps
```

- Panel: http://localhost:8301
- API: http://localhost:8300/api/health
- Swagger: http://localhost:8300/docs
- Usuario inicial: `admin`
- Contrasena inicial: `admin123`

Docker levanta PostgreSQL, FastAPI con Tesseract/Playwright y Nginx.

## Demostracion recomendada

1. Iniciar sesion.
2. Crear y editar un proveedor.
3. Cargar `data/facturas_generadas/factura_005.png`.
4. Abrir `Detalle` y revisar campos, OCR bruto, validacion y archivo original.
5. Probar `Rechazar`, `Reprocesar` y filtros por estado.
6. Ejecutar `RPA` y descargar la captura desde `Ejecuciones RPA`.
7. Consultar la bitacora filtrada.
8. Descargar reportes CSV/PDF y enviar uno por correo/demo.
9. Mostrar archivos creados en `evidencias/ocr/` y `evidencias/rpa/`.

## Pruebas automatizadas

```powershell
cd practica3/backend
pip install -r requirements.txt
python -m pytest tests -q
```

La suite cubre health, login, CRUD, errores de carga, parser, validacion aritmetica, rechazo, bitacora, CSV y correo demo.

## Dataset

`data/facturas_generadas/` contiene 20 documentos. Los primeros 10 provienen del ZIP y `scripts/seed_extra_invoices.py` completa el conjunto de evaluacion.

## Documentacion

- [Manual tecnico](docs/MANUAL_TECNICO.md)
- [Manual de usuario](docs/MANUAL_USUARIO.md)
- [Checklist 100 puntos](docs/checklist_100_practica3.md)
- [Guia de defensa](docs/GUIA_DEFENSA.md)
- [Entrega UEDI](docs/ENTREGA_UEDI.md)
- [Despliegue](docs/DESPLIEGUE_NUBE.md)
- [Fuentes de evaluacion](docs/evaluacion/)
- [Evidencias](evidencias/README.md)

## Estructura

```text
practica3/
|-- backend/             FastAPI, SQLAlchemy, OCR/CV, RPA y tests
|-- frontend/            Panel administrativo y formulario simulado
|-- data/                20 facturas de prueba
|-- docs/                Manuales, checklist, defensa y fuentes
|-- evidencias/          OCR, RPA, Docker y despliegue
|-- reports/             Reportes generados (ignorado por Git)
|-- uploads/             Archivos cargados (ignorado por Git)
|-- Dockerfile.cloud     Imagen unificada para nube
|-- docker-compose.yml   PostgreSQL + backend + frontend
`-- render.yaml          Blueprint de despliegue
```

## Guia rapida para defensa

- Python integra FastAPI, OpenCV, Tesseract, SQLAlchemy, ReportLab y Playwright.
- OpenCV prepara el documento; Tesseract reconoce texto localmente.
- El parser propio extrae siete campos y las reglas validan NIT, montos, suma y duplicados.
- SQLAlchemy persiste usuarios, proveedores, facturas, logs, reportes y RPA.
- Playwright llena un formulario real y guarda captura.
- Docker Compose coordina PostgreSQL, backend y frontend con health checks.
- Un fallo deja estado `Error`, detalle en bitacora y opcion de reproceso.

Las respuestas ampliadas estan en `docs/GUIA_DEFENSA.md`.

# Prompt de resolución — practica3 / SmartInvoice

Actúa como desarrollador full-stack y asistente de arquitectura para resolver la **Práctica 3 de Inteligencia Artificial 1: SmartInvoice**. Debes trabajar primero esta práctica antes de iniciar `proyecto_f2`.

## Contexto del repositorio y lineamientos globales

Trabaja dentro del mismo repositorio del curso de IA1. En la raíz deben coexistir, sin sobrescribirse entre sí, las carpetas:

```text
practica1/
proyecto_f1/
practica2/
proyecto_f2/
practica3/
```

Antes de programar, revisa `practica1`, `proyecto_f1` y `practica2` para mantener una estructura similar, reutilizar estilo de documentación, dockerización, forma de endpoints y forma de integración frontend/backend/Prolog cuando aplique. No copies código roto ni dependencias innecesarias: úsalo solo como guía de formato y coherencia del repositorio.

Cuando un requisito no exista en los proyectos anteriores, impleméntalo de la forma más limpia, directa y mantenible posible, priorizando funcionalidad comprobable. Evita soluciones solo simuladas salvo cuando el enunciado lo permita explícitamente. Usa base de datos para persistencia real de datos; no dejes persistencia principal en JSON.

Cada carpeta debe quedar autocontenida, con su propio `README.md`, `MANUAL_TECNICO.md`, `MANUAL_USUARIO.md`, archivos de configuración, instrucciones de instalación, ejecución, pruebas y evidencias. Mantén commits descriptivos y no mezcles cambios de `practica3` con `proyecto_f2` en el mismo paso si se puede evitar.

## Ubicación obligatoria

Crea y trabaja únicamente dentro de:

```text
practica3/
```

No modifiques `practica1`, `proyecto_f1`, `practica2` ni `proyecto_f2`, salvo que sea estrictamente necesario para configuración general del repositorio y se documente.

## Archivos fuente disponibles

Usa estos recursos como fuente principal:

```text
Practica 3 - IA1 JUNIO.docx.pdf
facturas_generadas.zip
practica3/transcripcion_practica3.md
practica3/recurso_facturas_generadas.md
```

`facturas_generadas.zip` pertenece a esta práctica. Extrae su contenido dentro de una ruta documentada, por ejemplo:

```text
practica3/data/facturas_generadas/
```

El ZIP contiene facturas PDF y PNG. Deben utilizarse como dataset inicial de pruebas para OCR y Computer Vision. Si solo hay 10 facturas, agrega un script o seed que permita completar al menos 20 facturas de prueba para cumplir la evaluación.

## Objetivo del sistema

Implementar **SmartInvoice**, una plataforma inteligente para procesar facturas digitales usando Computer Vision, OCR y RPA. El sistema debe permitir cargar facturas PDF/JPG/JPEG/PNG, extraer datos relevantes, validarlos, guardarlos en base de datos, generar reportes, registrar bitácora y enviar resultados por correo.

## Requisitos obligatorios que debes cumplir

Implementa como mínimo:

1. Backend en **Python** exclusivamente.
2. API REST con FastAPI o Flask. Se recomienda FastAPI por claridad y documentación automática.
3. Base de datos real para usuarios, proveedores, facturas, bitácoras y reportes. Recomendado: PostgreSQL con Docker Compose. SQLite solo si se justifica para modo local.
4. Frontend administrativo en HTML/CSS/JavaScript o framework liviano compatible con Docker.
5. Autenticación funcional.
6. CRUD completo de proveedores.
7. Gestión y consulta de facturas procesadas.
8. Carga de facturas en PDF, JPG, JPEG y PNG.
9. Módulo local de Computer Vision con OpenCV para preprocesamiento: escala de grises, binarización, limpieza, corrección simple y preparación para OCR.
10. Módulo OCR local con Tesseract, EasyOCR o equivalente. No usar servicios externos de IA generativa para extraer la información.
11. Extracción automática de:
    - Número de factura.
    - Fecha.
    - Nombre del proveedor.
    - NIT.
    - Subtotal.
    - Impuestos.
    - Total.
12. Validación automática antes de guardar definitivamente:
    - campos obligatorios,
    - total mayor que cero,
    - formato de fecha,
    - NIT válido o razonablemente validado,
    - detección básica de duplicados por número/proveedor/total.
13. Bitácora de procesamiento con fecha/hora, usuario, documento, estado y resultado.
14. Estados: `Procesado`, `Pendiente`, `Error`, `Rechazado`.
15. Reportes administrativos en PDF, Excel o CSV. Implementa al menos CSV y PDF; Excel es deseable.
16. RPA funcional con Selenium o Playwright para registrar la información extraída en un formulario web simulado dentro del mismo proyecto.
17. Envío automático de reportes por correo usando SMTP configurable por variables de entorno. Debe tener modo demo si no hay credenciales reales.
18. Dockerfile(s) y `docker-compose.yml` funcionales.
19. Despliegue documentado para nube libre: Render, Railway, GCP, AWS, Azure o equivalente.
20. URL pública preparada para evaluación cuando se despliegue.
21. Repositorio GitHub con historial de cambios.
22. Documentación de instalación, ejecución, despliegue y uso.

## Estructura mínima recomendada

Genera una estructura similar a esta, ajustándola si el repositorio previo usa otra convención clara:

```text
practica3/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   ├── database/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routers/
│   │   ├── services/
│   │   │   ├── ocr_service.py
│   │   │   ├── vision_service.py
│   │   │   ├── invoice_parser.py
│   │   │   ├── validation_service.py
│   │   │   ├── report_service.py
│   │   │   ├── email_service.py
│   │   │   └── rpa_service.py
│   │   └── utils/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── index.html
│   ├── login.html
│   ├── dashboard.html
│   ├── providers.html
│   ├── invoices.html
│   ├── logs.html
│   ├── reports.html
│   ├── rpa_form.html
│   ├── css/
│   └── js/
├── data/
│   └── facturas_generadas/
├── reports/
├── uploads/
├── docker-compose.yml
├── .env.example
├── README.md
├── MANUAL_TECNICO.md
├── MANUAL_USUARIO.md
└── transcripcion_practica3.md
```

## API mínima sugerida

Implementa endpoints como:

```text
POST   /api/auth/login
POST   /api/auth/register
GET    /api/me
GET    /api/providers
POST   /api/providers
PUT    /api/providers/{id}
DELETE /api/providers/{id}
POST   /api/invoices/upload
GET    /api/invoices
GET    /api/invoices/{id}
POST   /api/invoices/{id}/validate
POST   /api/invoices/{id}/rpa-register
GET    /api/logs
GET    /api/reports/csv
GET    /api/reports/pdf
POST   /api/reports/email
GET    /api/dashboard/metrics
```

## Base de datos mínima

Incluye migraciones o creación automática para:

- `users`
- `providers`
- `invoices`
- `processing_logs`
- `reports`
- `rpa_runs`

No guardes los datos principales solo en archivos JSON.

## Criterios de aceptación

Al terminar, verifica y documenta:

- `docker compose up --build` levanta frontend, backend y base de datos.
- Se puede iniciar sesión.
- Se pueden crear, editar, consultar y eliminar proveedores.
- Se puede subir una factura PDF y una PNG del ZIP.
- El sistema procesa localmente el documento con OpenCV + OCR.
- Se extraen los campos requeridos y se visualiza el texto OCR bruto para depuración.
- Se guarda la factura procesada en base de datos.
- Se registra bitácora.
- Se genera reporte CSV/PDF.
- El RPA llena un formulario web simulado con los datos extraídos.
- El envío de correo funciona o queda en modo demo documentado.
- Hay manual técnico y manual de usuario dentro de `practica3/`.

## Manual técnico obligatorio

Crea `practica3/MANUAL_TECNICO.md` con:

- Resumen del sistema.
- Arquitectura y diagrama en Mermaid.
- Tecnologías utilizadas.
- Estructura de carpetas.
- Modelo de base de datos.
- Endpoints REST.
- Flujo OCR + Computer Vision.
- Flujo RPA.
- Generación de reportes.
- Configuración de correo.
- Variables de entorno.
- Docker y Docker Compose.
- Instrucciones de despliegue en nube.
- Requerimientos funcionales y no funcionales.
- Posibles mejoras futuras.

## Manual de usuario obligatorio

Crea `practica3/MANUAL_USUARIO.md` con:

- Cómo iniciar el sistema.
- Cómo registrarse o iniciar sesión.
- Cómo administrar proveedores.
- Cómo cargar facturas.
- Cómo revisar facturas procesadas.
- Cómo validar/rechazar resultados.
- Cómo generar reportes.
- Cómo ejecutar RPA.
- Cómo enviar reportes por correo.
- Cómo interpretar estados y errores.

## Orden de trabajo

1. Lee la transcripción completa del enunciado.
2. Revisa estructura de prácticas/proyectos anteriores solo como guía.
3. Crea la carpeta `practica3/` y su estructura.
4. Implementa backend, base de datos y modelos.
5. Implementa OCR/CV y prueba con `facturas_generadas.zip`.
6. Implementa frontend y dashboard.
7. Implementa RPA, reportes y correo.
8. Agrega Docker Compose.
9. Crea manual técnico y manual de usuario.
10. Prueba flujo completo y deja evidencias.

## Transcripción base del enunciado

Usa como referencia completa el archivo `practica3/transcripcion_practica3.md`. No contradigas el PDF original. Si hay conflicto entre este prompt y el PDF, prioriza el PDF y documenta la decisión.

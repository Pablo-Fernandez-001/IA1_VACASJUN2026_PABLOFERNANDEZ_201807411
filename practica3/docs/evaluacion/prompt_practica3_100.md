# Prompt de resolución — practica3 / SmartInvoice orientado a 100 puntos

Actúa como desarrollador full-stack, arquitecto de software y asistente de documentación para resolver la **Práctica 3 de Inteligencia Artificial 1: SmartInvoice**. El objetivo es construir una solución funcional, demostrable y documentada para apuntar a **100/100** según el enunciado y la hoja de calificación.

Debes trabajar **primero esta práctica** antes de iniciar `proyecto_f2`.

---

## 1. Contexto del repositorio y lineamientos globales

Trabaja dentro del mismo repositorio del curso de IA1. En la raíz deben coexistir, sin sobrescribirse entre sí, las carpetas:

```text
practica1/
proyecto_f1/
practica2/
proyecto_f2/
practica3/
```

Antes de programar, revisa `practica1`, `proyecto_f1` y `practica2` para mantener una estructura similar, reutilizar estilo de documentación, dockerización, endpoints, frontend/backend y forma de evidencias cuando aplique. No copies código roto ni dependencias innecesarias: úsalo solo como guía de formato y coherencia.

Cuando un requisito no exista en los proyectos anteriores, impleméntalo de la forma más limpia, directa y mantenible posible, priorizando funcionalidad comprobable. Evita soluciones solo simuladas salvo cuando el enunciado lo permita explícitamente. Usa base de datos para persistencia real; no dejes persistencia principal en JSON.

Cada carpeta debe quedar autocontenida, con su propio `README.md`, `MANUAL_TECNICO.md`, `MANUAL_USUARIO.md`, archivos de configuración, instrucciones de instalación, ejecución, pruebas y evidencias.

---

## 2. Ubicación obligatoria

Crea y trabaja únicamente dentro de:

```text
practica3/
```

No modifiques `practica1`, `proyecto_f1`, `practica2` ni `proyecto_f2`, salvo que sea estrictamente necesario para configuración general del repositorio y se documente.

---

## 3. Archivos fuente disponibles

Usa estos recursos como fuente principal:

```text
Practica 3 - IA1 JUNIO.docx.pdf
[IA1]HC_Practica3-VACJUN.docx.pdf
facturas_generadas.zip
practica3/transcripcion_practica3.md
practica3/transcripcion_hc_practica3.md
practica3/recurso_facturas_generadas.md
practica3/checklist_100_practica3.md
```

`facturas_generadas.zip` pertenece a esta práctica. Extrae su contenido dentro de una ruta documentada, por ejemplo:

```text
practica3/data/facturas_generadas/
```

El ZIP contiene facturas PDF y PNG. Deben utilizarse como dataset inicial de pruebas para OCR y Computer Vision. Si solo hay 10 facturas, agrega un script o seed que permita completar al menos 20 facturas de prueba para cumplir con el enunciado.

---

## 4. Prioridad de cumplimiento

Usa esta prioridad si encuentras diferencias entre documentos:

1. **Hoja de calificación:** manda para el punteo y penalizaciones.
2. **Enunciado oficial:** manda para el alcance técnico general.
3. **Transcripciones:** son apoyo para no volver a leer los PDF.
4. **Prácticas/proyectos anteriores:** solo son guía de estructura y estilo.

No omitas nada que aparezca en la hoja de calificación, aunque parezca repetido con el enunciado.

---

## 5. Objetivo del sistema

Implementar **SmartInvoice**, una plataforma inteligente para procesar facturas digitales usando **Computer Vision, OCR y RPA**. El sistema debe permitir cargar facturas PDF/JPG/JPEG/PNG, extraer datos relevantes, validarlos, guardarlos en base de datos, generar reportes, registrar bitácora, enviar resultados por correo y demostrar una automatización RPA funcional.

---

## 6. Requisitos obligatorios del enunciado

Implementa como mínimo:

1. Backend en **Python** exclusivamente.
2. API REST con FastAPI o Flask. Se recomienda FastAPI por claridad y documentación automática.
3. Base de datos real para usuarios, proveedores, facturas, bitácoras y reportes. Recomendado: PostgreSQL con Docker Compose. SQLite solo si se justifica para modo local, pero prioriza una base SQL completa.
4. Frontend administrativo en HTML/CSS/JavaScript o framework liviano compatible con Docker.
5. Autenticación funcional.
6. CRUD completo de proveedores.
7. Gestión y consulta de facturas procesadas.
8. Carga de facturas en PDF, JPG, JPEG y PNG.
9. Módulo local de Computer Vision con OpenCV para preprocesamiento: escala de grises, binarización, limpieza, corrección simple y preparación para OCR.
10. Módulo OCR local con Tesseract, EasyOCR o equivalente. **No usar servicios externos de IA generativa para extraer toda la información.**
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

---

## 7. Requisitos agregados por la hoja de calificación para apuntar a 100

La solución debe estar organizada específicamente para cubrir cada bloque de la hoja de calificación.

### 7.1 Backend y API REST — 20 pts

Debes garantizar:

- **API REST funcional — 5 pts**
  - Backend levanta correctamente.
  - Endpoints responden con JSON válido.
  - Swagger/OpenAPI disponible si usas FastAPI.
  - Todas las rutas principales conectan con base de datos y servicios reales.

- **Endpoints correctamente organizados — 5 pts**
  - Separar routers por dominio: `auth`, `providers`, `invoices`, `logs`, `reports`, `rpa`, `dashboard`.
  - Usar prefijo `/api`.
  - Mantener nombres claros y consistentes.

- **Patrón de arquitectura utilizado y justificado — 5 pts**
  - Usar arquitectura por capas o MVC/Services/Repository.
  - Justificar el patrón en `MANUAL_TECNICO.md`.
  - Incluir diagrama Mermaid de arquitectura.

- **Manejo básico de errores — 5 pts**
  - Implementar errores HTTP adecuados: 400, 401, 404, 422, 500.
  - Validar archivos no permitidos.
  - Validar datos incompletos.
  - Registrar errores en bitácora.
  - Evitar que el sistema se caiga por un OCR fallido.

### 7.2 Base de Datos — 15 pts

Debes garantizar:

- **Base de datos configurada y conectada — 5 pts**
  - Debe levantar desde Docker Compose.
  - Backend debe conectarse por variables de entorno.
  - Incluir migraciones o creación automática de tablas.

- **Modelo de datos correcto — 5 pts**
  - Documentar el modelo en `MANUAL_TECNICO.md`.
  - Incluir diagrama ER o Mermaid.
  - Usar relaciones claras entre usuarios, proveedores, facturas y bitácoras.

- **Persistencia de proveedores, facturas, usuarios y bitácoras — 5 pts**
  - No usar JSON como persistencia principal.
  - Guardar usuarios autenticables.
  - Guardar proveedores.
  - Guardar facturas procesadas y resultados OCR.
  - Guardar bitácora de procesamiento.

### 7.3 Panel Administrativo — 20 pts

Debes garantizar:

- **Mecanismo de autenticación funcional — 5 pts**
  - Login real.
  - Registro o usuario seed.
  - Protección básica de rutas administrativas.

- **CRUD de proveedores — 5 pts**
  - Crear, listar, editar y eliminar proveedores.
  - Asociar proveedor con facturas cuando sea posible.

- **Gestión y consulta de facturas procesadas — 5 pts**
  - Ver lista de facturas.
  - Ver detalle de cada factura.
  - Ver archivo original o nombre/ruta.
  - Ver texto OCR bruto y campos extraídos.
  - Validar, rechazar o reprocesar si aplica.

- **Consulta de bitácoras y resultados de procesamiento — 5 pts**
  - Vista de historial.
  - Filtrar o consultar por estado.
  - Mostrar errores, usuario, fecha, documento y resultado.

### 7.4 OCR y Computer Vision — 15 pts

Debes garantizar:

- **Carga de documentos PDF/JPG/PNG — 3 pts**
  - Aceptar PDF, JPG, JPEG y PNG.
  - Rechazar extensiones inválidas.

- **OCR funcional — 5 pts**
  - OCR local mediante Tesseract, EasyOCR o equivalente.
  - Guardar texto OCR bruto para depuración.

- **Extracción de campos requeridos — 5 pts**
  - Extraer número de factura, fecha, proveedor, NIT, subtotal, impuestos y total.
  - Implementar parser con expresiones regulares y heurísticas tolerantes.

- **Validación automática de datos extraídos — 2 pts**
  - Validar campos obligatorios.
  - Validar montos numéricos.
  - Validar total/subtotal/impuestos cuando sea posible.
  - Marcar como `Procesado`, `Error` o `Rechazado` según resultado.

### 7.5 Automatización RPA — 10 pts

Debes garantizar:

- **Automatización funcional mediante Selenium, Playwright o equivalente — 5 pts**
  - Implementar script real de RPA.
  - El script debe abrir un formulario web simulado y llenar campos.
  - Debe poder ejecutarse desde backend o endpoint.

- **Registro automático de información en formularios o sistemas simulados — 3 pts**
  - Crear `frontend/rpa_form.html` o ruta equivalente.
  - Llenar datos extraídos de factura automáticamente.
  - Guardar resultado en `rpa_runs`.

- **Evidencia de ejecución y resultados — 2 pts**
  - Crear carpeta `practica3/evidencias/rpa/`.
  - Guardar capturas o logs de ejecución.
  - Documentar cómo reproducirlo en el manual técnico y usuario.

### 7.6 Reportes y Correos — 5 pts

Debes garantizar:

- **Generación de reportes PDF, Excel o CSV — 3 pts**
  - Implementar al menos CSV y PDF.
  - Guardar reportes en `practica3/reports/`.
  - Permitir descarga desde frontend o endpoint.

- **Envío automático por correo electrónico — 2 pts**
  - Configurar SMTP por `.env`.
  - Incluir modo demo si no hay credenciales.
  - Registrar envío en logs.

### 7.7 Docker y Despliegue — 5 pts

Debes garantizar:

- **Docker Compose funcional — 2 pts**
  - `docker compose up --build` debe levantar frontend, backend y base de datos.
  - Incluir `.env.example`.
  - Documentar puertos.

- **Despliegue en nube con URL pública funcional — 3 pts**
  - Documentar despliegue paso a paso.
  - Preparar variables de entorno.
  - Dejar espacio claro en README para URL pública.
  - Incluir comandos para GCP, Render, Railway o proveedor elegido.

### 7.8 Documentación — 5 pts

Debes garantizar:

- **Manual técnico — 2 pts**
  - Crear `practica3/MANUAL_TECNICO.md`.
  - Debe explicar arquitectura, endpoints, base de datos, OCR/CV, RPA, reportes, correo, Docker y despliegue.

- **Manual de usuario — 2 pts**
  - Crear `practica3/MANUAL_USUARIO.md`.
  - Debe explicar login, proveedores, facturas, bitácoras, reportes, RPA y correo.

- **Diagrama de arquitectura y modelo de datos — 1 pt**
  - Incluir ambos diagramas en el manual técnico.
  - Usar Mermaid para que sea fácil de renderizar en GitHub.

### 7.9 Defensa y preguntas — 5 pts

Debes preparar dentro de la documentación:

- Explicación de arquitectura y flujo del sistema — 2 pts.
- Respuestas preparadas para al menos 3 preguntas probables — 3 pts.

Crea una sección en `README.md` o `MANUAL_TECNICO.md` llamada:

```md
## Guía rápida para defensa
```

Incluye explicación simple de:

1. Por qué se usa Python.
2. Cómo funciona OCR y Computer Vision.
3. Cómo se guardan datos en base de datos.
4. Cómo funciona el RPA.
5. Cómo se generan reportes y correos.
6. Cómo Docker Compose levanta el sistema.
7. Qué pasa si una factura falla.

---

## 8. Penalizaciones que debes evitar obligatoriamente

La hoja de calificación incluye penalizaciones fuertes. Diseña el proyecto para evitarlas completamente.

- **No entregar en UEDI — penalización 100%**
  - Preparar ZIP o instrucciones finales para subir a UEDI.
  - Crear `practica3/ENTREGA_UEDI.md` con checklist de entrega.

- **No usar Python — penalización 100%**
  - Backend, OCR y RPA deben estar implementados en Python.

- **No usar OCR — penalización 50%**
  - OCR debe ser real y local.
  - No basta con datos quemados.

- **No usar base de datos — penalización 50%**
  - Persistir usuarios, proveedores, facturas y bitácoras.

- **No utilizar una base de datos SQL o NoSQL — penalización 50%**
  - Usar PostgreSQL, MySQL, SQLite, MongoDB o equivalente.
  - Recomendado: PostgreSQL.

- **No implementar RPA funcional — penalización 30%**
  - Debe existir automatización real con Selenium/Playwright.
  - Debe tener evidencia.

- **Utilizar servicios externos que realicen toda la extracción mediante IA generativa — penalización 30%**
  - No usar ChatGPT/API externa/servicios generativos para extraer toda la factura.
  - Permitido: OCR local y reglas propias de parsing.

- **Copias totales o parciales — nota final 0**
  - Generar solución propia.
  - Evitar copiar repositorios completos.
  - Documentar decisiones propias.

---

## 9. Estructura mínima recomendada actualizada para 100

Genera una estructura similar a esta, ajustándola si el repositorio previo usa otra convención clara:

```text
practica3/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── errors.py
│   │   ├── database/
│   │   │   ├── connection.py
│   │   │   ├── init_db.py
│   │   │   └── migrations/
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── provider.py
│   │   │   ├── invoice.py
│   │   │   ├── processing_log.py
│   │   │   ├── report.py
│   │   │   └── rpa_run.py
│   │   ├── schemas/
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── providers.py
│   │   │   ├── invoices.py
│   │   │   ├── logs.py
│   │   │   ├── reports.py
│   │   │   ├── rpa.py
│   │   │   └── dashboard.py
│   │   ├── services/
│   │   │   ├── ocr_service.py
│   │   │   ├── vision_service.py
│   │   │   ├── invoice_parser.py
│   │   │   ├── validation_service.py
│   │   │   ├── report_service.py
│   │   │   ├── email_service.py
│   │   │   └── rpa_service.py
│   │   └── utils/
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── index.html
│   ├── login.html
│   ├── dashboard.html
│   ├── providers.html
│   ├── invoices.html
│   ├── invoice_detail.html
│   ├── logs.html
│   ├── reports.html
│   ├── rpa_form.html
│   ├── css/
│   └── js/
├── data/
│   └── facturas_generadas/
├── uploads/
├── reports/
├── evidencias/
│   ├── rpa/
│   ├── ocr/
│   ├── docker/
│   └── despliegue/
├── docs/
│   └── diagramas/
├── docker-compose.yml
├── .env.example
├── README.md
├── MANUAL_TECNICO.md
├── MANUAL_USUARIO.md
├── ENTREGA_UEDI.md
├── transcripcion_practica3.md
├── transcripcion_hc_practica3.md
├── checklist_100_practica3.md
└── recurso_facturas_generadas.md
```

---

## 10. API mínima obligatoria y organizada

Implementa endpoints como mínimo:

```text
POST   /api/auth/register
POST   /api/auth/login
GET    /api/me

GET    /api/providers
POST   /api/providers
GET    /api/providers/{id}
PUT    /api/providers/{id}
DELETE /api/providers/{id}

POST   /api/invoices/upload
GET    /api/invoices
GET    /api/invoices/{id}
POST   /api/invoices/{id}/process
POST   /api/invoices/{id}/validate
POST   /api/invoices/{id}/reject
POST   /api/invoices/{id}/reprocess

GET    /api/logs
GET    /api/logs/{id}

GET    /api/reports/csv
GET    /api/reports/pdf
POST   /api/reports/email

POST   /api/rpa/invoices/{id}/register
GET    /api/rpa/runs

GET    /api/dashboard/metrics
GET    /api/health
```

Todos los endpoints deben tener:

- respuesta JSON clara,
- validación básica,
- manejo de error,
- registro en bitácora cuando aplique,
- documentación en el manual técnico.

---

## 11. Base de datos mínima

Incluye migraciones o creación automática para:

- `users`
- `providers`
- `invoices`
- `processing_logs`
- `reports`
- `rpa_runs`

Modelo sugerido:

```text
users
- id
- name
- email
- password_hash
- role
- created_at

providers
- id
- name
- nit
- email
- phone
- address
- created_at

invoices
- id
- provider_id
- invoice_number
- invoice_date
- nit
- subtotal
- taxes
- total
- status
- original_filename
- file_path
- raw_ocr_text
- validation_errors
- created_by
- created_at
- updated_at

processing_logs
- id
- invoice_id
- user_id
- document_name
- status
- result_message
- error_detail
- created_at

reports
- id
- report_type
- file_path
- generated_by
- sent_by_email
- created_at

rpa_runs
- id
- invoice_id
- status
- evidence_path
- result_message
- created_at
```

---

## 12. Criterios de aceptación para probar antes de entregar

Al terminar, verifica y documenta:

- `docker compose up --build` levanta frontend, backend y base de datos.
- Se puede iniciar sesión.
- Se pueden crear, editar, consultar y eliminar proveedores.
- Se puede subir una factura PDF y una PNG del ZIP.
- El sistema procesa localmente el documento con OpenCV + OCR.
- Se extraen los campos requeridos y se visualiza el texto OCR bruto para depuración.
- Se valida automáticamente la factura.
- Se guarda la factura procesada en base de datos.
- Se registra bitácora.
- Se consulta bitácora desde panel administrativo.
- Se genera reporte CSV/PDF.
- Se puede enviar reporte por correo o simular envío documentado.
- El RPA llena un formulario web simulado con los datos extraídos.
- Se guardan evidencias de RPA.
- El README contiene URL pública o sección clara para colocarla.
- Hay manual técnico y manual de usuario dentro de `practica3/`.
- Hay diagrama de arquitectura y modelo de datos.
- Hay guía rápida para defensa.
- Existe `ENTREGA_UEDI.md` con checklist de entrega.

---

## 13. Manual técnico obligatorio

Crea `practica3/MANUAL_TECNICO.md` con:

- Resumen del sistema.
- Arquitectura utilizada y justificación del patrón.
- Diagrama de arquitectura en Mermaid.
- Tecnologías utilizadas.
- Estructura de carpetas.
- Modelo de base de datos.
- Diagrama de modelo de datos en Mermaid.
- Endpoints REST.
- Manejo de errores.
- Flujo OCR + Computer Vision.
- Flujo de extracción y validación.
- Flujo RPA.
- Generación de reportes.
- Configuración de correo.
- Variables de entorno.
- Docker y Docker Compose.
- Instrucciones de despliegue en nube.
- Evidencias esperadas.
- Requerimientos funcionales y no funcionales.
- Guía rápida para defensa.
- Posibles mejoras futuras.

---

## 14. Manual de usuario obligatorio

Crea `practica3/MANUAL_USUARIO.md` con:

- Cómo iniciar el sistema.
- Cómo registrarse o iniciar sesión.
- Cómo administrar proveedores.
- Cómo cargar facturas.
- Cómo revisar facturas procesadas.
- Cómo interpretar campos extraídos.
- Cómo validar, rechazar o reprocesar resultados.
- Cómo consultar bitácoras.
- Cómo generar reportes.
- Cómo ejecutar RPA.
- Cómo enviar reportes por correo.
- Cómo interpretar estados y errores.

---

## 15. Evidencias obligatorias recomendadas

Crea la carpeta:

```text
practica3/evidencias/
```

Incluye o deja preparado:

```text
practica3/evidencias/ocr/
practica3/evidencias/rpa/
practica3/evidencias/docker/
practica3/evidencias/despliegue/
```

Guardar evidencias como:

- capturas del panel administrativo,
- capturas o logs del OCR,
- capturas o logs del RPA,
- capturas de Docker Compose corriendo,
- capturas del despliegue en nube,
- reporte generado,
- ejemplo de correo o modo demo.

---

## 16. Archivo de entrega UEDI

Crea `practica3/ENTREGA_UEDI.md` con:

```md
# Entrega UEDI — Práctica 3 SmartInvoice

## Checklist final

- [ ] Repositorio GitHub actualizado.
- [ ] Código dentro de `practica3/`.
- [ ] Backend en Python.
- [ ] OCR funcional.
- [ ] Base de datos SQL o NoSQL funcional.
- [ ] RPA funcional.
- [ ] Docker Compose funcional.
- [ ] Despliegue con URL pública.
- [ ] Manual técnico.
- [ ] Manual de usuario.
- [ ] Evidencias.
- [ ] Subido a UEDI.

## URL pública

Pendiente colocar URL.

## Repositorio

Pendiente colocar enlace.
```

---

## 17. Orden de trabajo recomendado

1. Lee `transcripcion_practica3.md`.
2. Lee `transcripcion_hc_practica3.md`.
3. Lee `checklist_100_practica3.md`.
4. Revisa estructura de prácticas/proyectos anteriores solo como guía.
5. Crea o actualiza la carpeta `practica3/`.
6. Extrae `facturas_generadas.zip` en `data/facturas_generadas/`.
7. Implementa Docker Compose con backend, frontend y base de datos.
8. Implementa backend Python con arquitectura por capas.
9. Implementa autenticación y usuarios.
10. Implementa proveedores CRUD.
11. Implementa carga de facturas.
12. Implementa Computer Vision y OCR.
13. Implementa parser de campos.
14. Implementa validación automática.
15. Implementa persistencia en base de datos.
16. Implementa bitácoras.
17. Implementa panel administrativo.
18. Implementa reportes CSV/PDF.
19. Implementa correo SMTP o modo demo.
20. Implementa RPA con evidencia.
21. Agrega documentación técnica y de usuario.
22. Agrega diagramas.
23. Agrega guía de defensa.
24. Agrega `ENTREGA_UEDI.md`.
25. Prueba flujo completo.
26. Preparar despliegue y URL pública.

---

## 18. Flujo completo que debe poder demostrarse

Durante la evaluación se debe poder mostrar este flujo:

```text
Login
→ Panel administrativo
→ Carga de factura PDF/PNG
→ Preprocesamiento con Computer Vision
→ OCR local
→ Extracción de campos
→ Validación automática
→ Guardado en base de datos
→ Consulta de factura procesada
→ Consulta de bitácora
→ Generación de reporte
→ Envío de reporte por correo
→ Ejecución de RPA sobre formulario simulado
→ Evidencia del resultado
```

---

## 19. Resultado esperado

Al finalizar, la carpeta `practica3/` debe contener una solución funcional y defendible que cubra todos los puntos de la hoja de calificación y evite todas las penalizaciones. No entregues una solución incompleta, sin OCR, sin base de datos, sin RPA o sin Docker Compose, porque esas faltas reducen fuertemente la nota.

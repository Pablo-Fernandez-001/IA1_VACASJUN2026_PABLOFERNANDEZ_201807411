# Manual de Usuario - SmartInvoice

## Iniciar

```powershell
cd practica3
Copy-Item .env.example .env
docker compose up --build -d
```

Abra http://localhost:8301. Usuario inicial: `admin`; contrasena: `admin123`.

## Registro e inicio de sesion

Puede usar el administrador inicial o crear un usuario desde login. Las secciones administrativas requieren token; al expirar volvera al login.

## Proveedores

En `Proveedores` puede crear, listar, editar y eliminar. El NIT no puede repetirse. Cuando OCR identifica un NIT nuevo, SmartInvoice puede crear la asociacion automaticamente.

## Cargar una factura

1. Entre a `Facturas`.
2. Elija PDF, JPG, JPEG o PNG.
3. Pulse `Procesar`.
4. Espere el mensaje de Computer Vision/OCR.

Una extension distinta se rechaza y queda en bitacora. `Procesar dataset` ejecuta las 20 facturas de prueba y puede tardar.

## Consultar y filtrar

Use texto para buscar por numero, proveedor o NIT y seleccione estado. `Detalle` muestra:

- archivo original descargable,
- numero, fecha, proveedor y NIT,
- subtotal, impuestos y total,
- estado y errores de validacion,
- texto OCR bruto,
- bitacora y RPA asociados.

## Validar, rechazar y reprocesar

- `Validar`: repite reglas sobre los campos guardados.
- `Rechazar`: solicita motivo y conserva trazabilidad.
- `Reprocesar`: vuelve a ejecutar CV, OCR, parser y validacion sobre el original.

## Bitacora

La vista permite buscar por documento/resultado y filtrar por estado. Muestra fecha, usuario, documento, resultado y detalle de error.

## RPA

Desde una factura pulse `RPA`. Playwright abre el formulario, llena campos, envia y toma captura. Revise `Ejecuciones RPA` para estado y descarga de evidencia. Un estado `Error` indica que Chromium o el formulario no estuvieron disponibles; revise el TXT de evidencia y reintente.

## Reportes

En `Reportes` puede descargar CSV/PDF y consultar historial. Para correo ingrese destinatario y formato:

- `sent`: SMTP envio el mensaje.
- `demo`: faltan credenciales; se creo evidencia local.
- `Error`: revise bitacora y variables SMTP.

## Estados

- `Pendiente`: procesamiento iniciado.
- `Procesado`: OCR y reglas correctos.
- `Rechazado`: datos invalidos o rechazo administrativo.
- `Error`: fallo tecnico u OCR sin texto util.

## Evidencias

- OCR: `evidencias/ocr/`.
- RPA: `evidencias/rpa/` y descarga desde panel.
- Docker/nube: instrucciones en sus carpetas de evidencia.

## Solucion de problemas

- API no responde: `docker compose ps` y `docker compose logs backend`.
- OCR no disponible: use Docker, que instala Tesseract `spa+eng`.
- RPA falla: confirme que `frontend` este saludable y reconstruya backend para instalar Chromium.
- Base no conecta: revise `POSTGRES_*` y elimine solo el volumen de desarrollo si acepta perder datos.

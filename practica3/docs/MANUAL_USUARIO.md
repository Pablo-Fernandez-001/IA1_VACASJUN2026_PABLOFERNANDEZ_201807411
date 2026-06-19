# Manual de Usuario - SmartInvoice

## Iniciar el sistema

```bash
cd practica3
cp .env.example .env
docker compose up --build
```

Abra http://localhost:8301.

## Iniciar sesion

Use el usuario inicial:

- Usuario: `admin`
- Contrasena: `admin123`

Tambien puede registrar un usuario nuevo desde la pantalla de login.

## Administrar proveedores

Entre a `Proveedores`, complete nombre, NIT, correo, telefono, direccion y categoria. Use `Editar` para actualizar datos o `Eliminar` para quitar un proveedor.

## Cargar facturas

Entre a `Facturas`, seleccione un archivo PDF/JPG/JPEG/PNG y pulse `Procesar`. El sistema guarda el archivo, ejecuta OCR, extrae campos y muestra el estado.

## Revisar facturas procesadas

En la tabla de facturas puede ver numero, fecha, proveedor, NIT, total y estado. Use `OCR` para revisar el texto bruto extraido.

## Validar o rechazar

Use `Validar` para reejecutar reglas de validacion. Si faltan campos, el total es cero, el NIT es invalido o hay duplicado, la factura queda `Rechazado`.

## Ejecutar RPA

En una factura, pulse `RPA`. El sistema abrira el formulario simulado y registrara los datos extraidos. El resultado queda en bitacora.

## Generar reportes

Entre a `Reportes` y descargue CSV o PDF. Tambien puede escribir un correo y enviar el reporte. Si no hay SMTP configurado, SmartInvoice genera una evidencia local en modo demo.

## Interpretar estados

- `Procesado`: datos extraidos y validados.
- `Pendiente`: tarea preparada o RPA sin navegador disponible.
- `Error`: fallo tecnico durante el procesamiento.
- `Rechazado`: datos incompletos, invalidos o duplicados.

## Bitacora

La seccion `Bitacora` muestra fecha, usuario, documento, estado y resultado de cada operacion importante.

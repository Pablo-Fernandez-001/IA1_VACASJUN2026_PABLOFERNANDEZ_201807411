# Despliegue en nube

## Imagen unificada

Desde la carpeta de la practica:

```powershell
cd practica3
docker build -f Dockerfile.cloud -t smartinvoice-cloud .
docker run --rm -p 8500:8000 -e DATABASE_URL=sqlite:////app/smartinvoice.db -e JWT_SECRET=local-cloud smartinvoice-cloud
```

Abrir `http://localhost:8500/login.html`.

## Render Blueprint

1. Conectar el repositorio de GitHub a Render.
2. Crear un Blueprint usando `practica3/render.yaml`; el `rootDir` limita el contexto a la practica.
3. Completar las variables SMTP opcionales.
4. Esperar el health check `/api/health`.
5. Copiar la URL asignada a `PUBLIC_URL` y al README.
6. Probar login, una factura y RPA desde la URL publica.

`Dockerfile.cloud` sirve API y frontend en el mismo dominio, incluye Tesseract y Chromium, y obtiene PostgreSQL mediante `DATABASE_URL`.

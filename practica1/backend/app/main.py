from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.core.config import settings
from app.cities_feature.router import router as cities_router
from app.routes_feature.router import router as routes_router
from app.connections_feature.router import router as connections_router


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend Python orientado por funcionalidades que consulta SWI-Prolog.",
    version=settings.VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cities_router)
app.include_router(routes_router)
app.include_router(connections_router)


@app.get("/")
def root():
    return {
        "mensaje": "API funcionando correctamente",
        "arquitectura": "Feature-Based Layered Architecture",
        "motor_logico": "SWI-Prolog",
        "backend": "FastAPI"
    }


@app.get("/estado", response_class=HTMLResponse)
def status_page():
    return """
    <!doctype html>
    <html lang="es">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Backend Practica 1</title>
        <style>
          body {
            margin: 0;
            min-height: 100vh;
            display: grid;
            place-items: center;
            background: #0f172a;
            color: #e2e8f0;
            font-family: Arial, sans-serif;
          }
          main {
            width: min(720px, calc(100% - 32px));
            padding: 32px;
            border: 1px solid rgba(148, 163, 184, 0.35);
            border-radius: 18px;
            background: #111827;
            box-shadow: 0 24px 70px rgba(0, 0, 0, 0.35);
          }
          h1 { margin: 0 0 12px; font-size: 40px; }
          p { color: #cbd5e1; line-height: 1.7; }
          dl {
            display: grid;
            grid-template-columns: 180px 1fr;
            gap: 12px 18px;
            margin: 24px 0;
          }
          dt { color: #93c5fd; font-weight: 700; }
          dd { margin: 0; }
          a {
            color: #bfdbfe;
            font-weight: 700;
          }
        </style>
      </head>
      <body>
        <main>
          <h1>API funcionando correctamente</h1>
          <p>Servidor FastAPI activo y conectado al motor logico SWI-Prolog.</p>
          <dl>
            <dt>Backend</dt><dd>FastAPI</dd>
            <dt>Arquitectura</dt><dd>Feature-Based Layered Architecture</dd>
            <dt>Motor logico</dt><dd>SWI-Prolog</dd>
            <dt>Documentacion</dt><dd><a href="/docs">/docs</a></dd>
          </dl>
        </main>
      </body>
    </html>
    """

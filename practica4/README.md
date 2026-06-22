# RoboMaze — Práctica 4 de Inteligencia Artificial 1

Aplicación web interactiva para construir laberintos, resolverlos en un backend
Python con **Breadth-First Search (BFS)** y **Depth-First Search (DFS)**, visualizar
la exploración y comparar longitud, nodos visitados y tiempo de ejecución.

> Universidad de San Carlos de Guatemala · Facultad de Ingeniería  
> Vacaciones del primer semestre 2026 · Entrega: **24/06/2026**

## Cumplimiento destacado

- BFS y DFS implementados manualmente en Python; no se usan librerías de rutas.
- API REST FastAPI con arquitectura por capas y documentación Swagger.
- Editor visual con inicio, destino, obstáculos, animación y modo responsivo.
- Cinco casos JSON: directo, moderado, largo, trampa para DFS y sin solución.
- Comparación automática con métricas y conclusión explicativa.
- Validaciones de límites, bloqueos, duplicados, tamaño y JSON.
- 22 pruebas automatizadas de algoritmos, validaciones y API.
- Ejecución local o con Docker Compose, sin base de datos.

## Tecnologías

Python 3.11+, FastAPI, Pydantic, Uvicorn, Pytest, HTML5, CSS3, JavaScript
vanilla, Nginx y Docker Compose.

## Inicio rápido en Windows

Terminal 1 — backend:

```powershell
cd practica4\backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8400
```

Terminal 2 — frontend:

```powershell
cd practica4\frontend
python -m http.server 5500
```

Abrir http://localhost:5500. También es posible abrir `frontend/index.html`
directamente. La API queda en http://localhost:8400 y Swagger en
http://localhost:8400/docs.

### Inicio rápido en Linux/macOS

```bash
cd practica4/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8400
```

En otra terminal:

```bash
cd practica4/frontend
python3 -m http.server 5500
```

## Docker Compose

Desde `practica4/`:

```powershell
docker compose up --build -d
docker compose ps
```

- Interfaz: http://localhost:8401
- API: http://localhost:8400/api/health
- Swagger: http://localhost:8400/docs
- Detener: `docker compose down`

Docker solo levanta FastAPI y Nginx; el proyecto respeta la restricción de no
utilizar base de datos.

## Endpoints principales

| Método | Ruta | Función |
|---|---|---|
| GET | `/api/health` | Verifica el backend |
| POST | `/api/maze/solve/bfs` | Ejecuta BFS |
| POST | `/api/maze/solve/dfs` | Ejecuta DFS |
| POST | `/api/maze/solve/compare` | Compara ambos algoritmos |
| GET | `/api/maze/examples` | Devuelve los cinco casos |
| GET | `/api/maze/examples/{id}` | Devuelve un caso por id |

Ejemplo mínimo:

```json
{
  "rows": 5,
  "cols": 5,
  "start": {"row": 0, "col": 0},
  "goal": {"row": 4, "col": 4},
  "obstacles": [{"row": 1, "col": 1}]
}
```

## Pruebas y verificación

```powershell
cd practica4\backend
pip install -r requirements.txt
python -m pytest tests -q

cd ..
python scripts\verificar_practica4.py
```

Resultado de referencia: `22 passed` y verificador `100/100`.

## Estructura

```text
practica4/
├── backend/
│   ├── app/
│   │   ├── api/                 Endpoints HTTP
│   │   ├── core/                Configuración
│   │   ├── models/              Schemas Pydantic
│   │   └── services/            BFS, DFS, validación y comparación
│   └── tests/                   Pruebas unitarias/de integración
├── frontend/                    Interfaz HTML/CSS/JS
├── examples/                    Cinco laberintos JSON
├── docs/                        Diagramas, evidencias y guías
├── postman/                     Colección de pruebas REST
├── scripts/                     Verificador y ejecución Windows
├── docker-compose.yml
├── MANUAL_TECNICO.md
├── MANUAL_USUARIO.md
├── ENTREGA_UEDI.md
└── transcripcion_practica4.md
```

## Documentación

- [Manual técnico](MANUAL_TECNICO.md)
- [Manual de usuario](MANUAL_USUARIO.md)
- [Entrega UEDI](ENTREGA_UEDI.md)
- [Checklist de 100 puntos](docs/CHECKLIST_100.md)
- [Guía de defensa](docs/GUIA_DEFENSA.md)
- [Evidencias](docs/evidencias/README.md)
- [Colección Postman](postman/RoboMaze.postman_collection.json)

## Historial sugerido de commits

La rúbrica exige al menos cinco commits funcionales y progresivos. Antes de la
entrega, registrar el avance real con mensajes equivalentes a:

```text
estructura inicial de practica4 robomaze
implementacion backend fastapi y modelos de laberinto
implementacion bfs y dfs con validaciones
frontend interactivo para laberintos y ejecucion de algoritmos
documentacion manuales evidencias y entrega final
```

No se recomienda simular fechas ni reescribir el historial; los commits deben
reflejar trabajo real.

## Datos del estudiante

- Estudiante: **Pablo Fernández**
- Carné: **201807411**
- Repositorio: https://github.com/Pablo-Fernandez-001/IA1_VACASJUN2026_PABLOFERNANDEZ_201807411

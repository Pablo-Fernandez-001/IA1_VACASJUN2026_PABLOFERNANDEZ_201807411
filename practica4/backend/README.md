# Backend RoboMaze

API REST en FastAPI. La logica se divide en rutas HTTP, modelos Pydantic,
validacion de dominio y servicios de busqueda manual BFS/DFS.

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8400
```

- Swagger: http://localhost:8400/docs
- Salud: http://localhost:8400/api/health
- Pruebas: `python -m pytest tests -q`

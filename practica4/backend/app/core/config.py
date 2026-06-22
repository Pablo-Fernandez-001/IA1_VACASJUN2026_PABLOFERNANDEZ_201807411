import os
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[3]
EXAMPLES_DIR = Path(os.getenv("EXAMPLES_DIR", str(PROJECT_DIR / "examples")))

APP_TITLE = "RoboMaze API"
APP_VERSION = "1.0.0"
MAX_MAZE_SIZE = 100

# Permite abrir el frontend como archivo, con http.server o desde Docker/Nginx.
CORS_ORIGINS = ["*"]

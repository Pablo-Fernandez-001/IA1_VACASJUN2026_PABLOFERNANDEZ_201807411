from pathlib import Path


class Settings:
    PROJECT_NAME = "Ruta mas corta entre ciudades"
    VERSION = "0.1.0"

    BASE_DIR = Path(__file__).resolve().parents[3]
    PROLOG_FILE = BASE_DIR / "prolog" / "rutas.pl"


settings = Settings()
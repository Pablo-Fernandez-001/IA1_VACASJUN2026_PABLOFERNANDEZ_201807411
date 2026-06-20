import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


def _load_dotenv() -> None:
    env_path = Path(__file__).resolve().parents[3] / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on", "si"}


_load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_name: str = "SmartInvoice"
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./smartinvoice.db")
    jwt_secret: str = os.getenv("JWT_SECRET", "smartinvoice-local-secret")
    access_token_minutes: int = int(os.getenv("ACCESS_TOKEN_MINUTES", "480"))
    cors_origins: str = os.getenv("CORS_ORIGINS", "*")
    upload_dir: str = os.getenv("UPLOAD_DIR", "./uploads")
    report_dir: str = os.getenv("REPORT_DIR", "./reports")
    evidence_dir: str = os.getenv("EVIDENCE_DIR", "./evidencias")
    dataset_dir: str = os.getenv("DATASET_DIR", "./data/facturas_generadas")
    smtp_host: str = os.getenv("SMTP_HOST", "")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: str = os.getenv("SMTP_USER", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    smtp_from: str = os.getenv("SMTP_FROM", "smartinvoice@example.local")
    smtp_tls: bool = _bool("SMTP_TLS", True)
    rpa_form_url: str = os.getenv("RPA_FORM_URL", "")
    public_url: str = os.getenv("PUBLIC_URL") or os.getenv("RENDER_EXTERNAL_URL", "")

    @property
    def ocr_evidence_dir(self) -> str:
        return str(Path(self.evidence_dir) / "ocr")

    @property
    def rpa_evidence_dir(self) -> str:
        return str(Path(self.evidence_dir) / "rpa")

    @property
    def sqlalchemy_database_url(self) -> str:
        if self.database_url.startswith("postgres://"):
            return self.database_url.replace("postgres://", "postgresql+psycopg2://", 1)
        if self.database_url.startswith("postgresql://"):
            return self.database_url.replace("postgresql://", "postgresql+psycopg2://", 1)
        return self.database_url

    @property
    def cors_origin_list(self) -> list[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

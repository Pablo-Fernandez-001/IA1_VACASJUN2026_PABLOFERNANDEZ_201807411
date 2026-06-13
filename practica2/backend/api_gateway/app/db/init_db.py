from pathlib import Path

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import AdminUser
from app.db.session import Base, engine

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SEED_PATH = Path(__file__).resolve().parents[2] / "seeds" / "seed.sql"


def load_sql_seed_if_needed() -> None:
    raw = engine.raw_connection()
    try:
        cursor = raw.driver_connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM questions")
        if cursor.fetchone()[0] == 0:
            raw.driver_connection.executescript(SEED_PATH.read_text(encoding="utf-8"))
            raw.commit()
    finally:
        raw.close()


def init_db(db: Session) -> None:
    Base.metadata.create_all(bind=engine)
    load_sql_seed_if_needed()
    db.expire_all()

    if not db.query(AdminUser).filter_by(username=settings.admin_username).first():
        db.add(
            AdminUser(
                username=settings.admin_username,
                password_hash=pwd_context.hash(settings.admin_password),
            )
        )
        db.commit()

from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.database.session import Base, engine
from app.models.entities import User


def init_db(db: Session) -> None:
    Base.metadata.create_all(bind=engine)
    _apply_compatible_migrations()
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        db.add(
            User(
                username="admin",
                email="admin@smartinvoice.local",
                full_name="Administrador SmartInvoice",
                password_hash=get_password_hash("admin123"),
            )
        )
        db.commit()


def _apply_compatible_migrations() -> None:
    """Adds rubric fields to databases created by an earlier project version."""
    additions = {
        "users": {"role": "VARCHAR(30) DEFAULT 'admin'"},
        "processing_logs": {
            "error_detail": "TEXT DEFAULT ''",
            "user_id": "INTEGER",
        },
        "reports": {"sent_by_email": "BOOLEAN DEFAULT FALSE"},
        "rpa_runs": {"evidence_path": "VARCHAR(500) DEFAULT ''"},
    }
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    with engine.begin() as connection:
        for table, columns in additions.items():
            if table not in tables:
                continue
            existing = {column["name"] for column in inspector.get_columns(table)}
            for column, definition in columns.items():
                if column not in existing:
                    connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {definition}"))

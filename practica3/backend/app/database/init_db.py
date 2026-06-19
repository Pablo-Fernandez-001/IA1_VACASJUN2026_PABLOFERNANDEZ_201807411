from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.database.session import Base, engine
from app.models.entities import User


def init_db(db: Session) -> None:
    Base.metadata.create_all(bind=engine)
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

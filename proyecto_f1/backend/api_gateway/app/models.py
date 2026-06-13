from datetime import datetime
from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

class DiagnosisHistory(Base):
    __tablename__ = "diagnosis_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_name: Mapped[str] = mapped_column(String(120), default="Usuario")
    selected_symptoms: Mapped[str] = mapped_column(Text, nullable=False)
    result_json: Mapped[str] = mapped_column(Text, nullable=False)
    top_diagnosis: Mapped[str] = mapped_column(String(180), default="Sin diagnóstico")
    telegram_sent: Mapped[str] = mapped_column(String(20), default="no")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SystemConfig(Base):
    __tablename__ = "system_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    bot_id: Mapped[str] = mapped_column(String(120), default="")
    bot_active: Mapped[bool] = mapped_column(Boolean, default=True)
    welcome_message: Mapped[str] = mapped_column(
        Text,
        default="Hola, soy Doctor Byte. Usa /sintomas para consultar el catalogo.",
    )
    diagnosis_message: Mapped[str] = mapped_column(
        Text,
        default="Analice tus sintomas con el motor experto Prolog.",
    )
    no_diagnosis_message: Mapped[str] = mapped_column(
        Text,
        default="No encontre un diagnostico concluyente.",
    )

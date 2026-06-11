from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Text
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

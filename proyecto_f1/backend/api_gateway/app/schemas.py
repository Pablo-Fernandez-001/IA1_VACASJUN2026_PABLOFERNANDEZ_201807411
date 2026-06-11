from datetime import datetime
from pydantic import BaseModel, Field

class DiagnoseRequest(BaseModel):
    symptoms: list[str] = Field(min_length=1, description="Lista de síntomas seleccionados")
    user_name: str = "Usuario"
    notify_telegram: bool = False
    telegram_chat_id: str | None = None

class DiagnosisRecord(BaseModel):
    id: int
    user_name: str
    selected_symptoms: list[str]
    result: dict
    top_diagnosis: str
    telegram_sent: str
    created_at: datetime

class TelegramMessage(BaseModel):
    chat_id: str | None = None
    text: str

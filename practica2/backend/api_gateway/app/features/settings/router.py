from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import get_current_admin
from app.db.models import Setting
from app.db.session import get_db
from app.services.telegram_client import send_telegram_message

router = APIRouter(prefix="/api/settings", tags=["settings"])
class SettingIn(BaseModel):
    value: str
    description: str = ""

class TelegramTestIn(BaseModel):
    text: str = "SmartBot Practica 2: mensaje de prueba."
    chat_id: str | None = None

@router.get("", dependencies=[Depends(get_current_admin)])
def list_settings(db: Session = Depends(get_db)):
    return db.query(Setting).order_by(Setting.key).all()

@router.put("/{key}", dependencies=[Depends(get_current_admin)])
def upsert_setting(key: str, payload: SettingIn, db: Session = Depends(get_db)):
    obj = db.get(Setting, key)
    if not obj:
        obj = Setting(key=key, value=payload.value, description=payload.description)
        db.add(obj)
    else:
        obj.value = payload.value
        obj.description = payload.description or obj.description
    db.commit(); db.refresh(obj); return obj

@router.delete("/{key}", dependencies=[Depends(get_current_admin)])
def delete_setting(key: str, db: Session = Depends(get_db)):
    obj = db.get(Setting, key)
    if not obj: raise HTTPException(404, "Configuración no encontrada")
    db.delete(obj); db.commit(); return {"ok": True}

@router.post("/telegram/test", dependencies=[Depends(get_current_admin)])
def send_telegram_test(payload: TelegramTestIn, db: Session = Depends(get_db)):
    configured = db.get(Setting, "telegram_chat_id")
    chat_id = payload.chat_id or (configured.value if configured and configured.value else settings.telegram_default_chat_id)
    return send_telegram_message(chat_id=chat_id, text=payload.text)

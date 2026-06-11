from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.security import get_current_admin
from app.db.models import Setting
from app.db.session import get_db

router = APIRouter(prefix="/api/settings", tags=["settings"])
class SettingIn(BaseModel):
    value: str
    description: str = ""

@router.get("")
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

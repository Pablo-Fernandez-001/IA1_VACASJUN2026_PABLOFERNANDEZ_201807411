from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.security import create_access_token, verify_password, get_current_admin
from app.db.models import AdminUser
from app.db.session import get_db

router = APIRouter(prefix="/api/auth", tags=["auth"])

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(AdminUser).filter_by(username=payload.username, is_active=True).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return {"access_token": create_access_token(user.username), "token_type": "bearer", "username": user.username}

@router.get("/me")
def me(user: AdminUser = Depends(get_current_admin)):
    return {"id": user.id, "username": user.username}

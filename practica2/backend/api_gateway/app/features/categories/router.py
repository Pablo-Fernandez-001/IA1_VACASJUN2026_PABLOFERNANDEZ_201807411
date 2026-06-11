from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.security import get_current_admin
from app.db.models import Category
from app.db.session import get_db

router = APIRouter(prefix="/api/categories", tags=["categories"])
class CategoryIn(BaseModel):
    name: str
    description: str = ""

@router.get("")
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).order_by(Category.name).all()

@router.post("", dependencies=[Depends(get_current_admin)])
def create_category(payload: CategoryIn, db: Session = Depends(get_db)):
    obj = Category(**payload.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@router.put("/{category_id}", dependencies=[Depends(get_current_admin)])
def update_category(category_id: int, payload: CategoryIn, db: Session = Depends(get_db)):
    obj = db.get(Category, category_id)
    if not obj: raise HTTPException(404, "Categoría no encontrada")
    for k,v in payload.model_dump().items(): setattr(obj,k,v)
    db.commit(); db.refresh(obj); return obj

@router.delete("/{category_id}", dependencies=[Depends(get_current_admin)])
def delete_category(category_id: int, db: Session = Depends(get_db)):
    obj = db.get(Category, category_id)
    if not obj: raise HTTPException(404, "Categoría no encontrada")
    db.delete(obj); db.commit(); return {"ok": True}

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.core.security import get_current_admin
from app.db.models import Category, Faq, QueryLog, Setting
from app.db.session import get_db

router = APIRouter(prefix="/api/faqs", tags=["faqs"])
class FaqIn(BaseModel):
    question: str
    answer: str
    keywords: str = ""
    category_id: int
    is_active: bool = True

@router.get("")
def list_faqs(db: Session = Depends(get_db)):
    return db.query(Faq).order_by(Faq.id).all()

@router.post("", dependencies=[Depends(get_current_admin)])
def create_faq(payload: FaqIn, db: Session = Depends(get_db)):
    obj = Faq(**payload.model_dump())
    db.add(obj); db.commit(); db.refresh(obj); return obj

@router.put("/{faq_id}", dependencies=[Depends(get_current_admin)])
def update_faq(faq_id: int, payload: FaqIn, db: Session = Depends(get_db)):
    obj = db.get(Faq, faq_id)
    if not obj: raise HTTPException(404, "FAQ no encontrada")
    for k,v in payload.model_dump().items(): setattr(obj,k,v)
    db.commit(); db.refresh(obj); return obj

@router.delete("/{faq_id}", dependencies=[Depends(get_current_admin)])
def delete_faq(faq_id: int, db: Session = Depends(get_db)):
    obj = db.get(Faq, faq_id)
    if not obj: raise HTTPException(404, "FAQ no encontrada")
    db.delete(obj); db.commit(); return {"ok": True}

@router.get("/search")
def search_faq(q: str, telegram_user: str = "panel", db: Session = Depends(get_db)):
    clean = q.strip().lower()
    faqs = db.query(Faq).filter(Faq.is_active == True).all()
    best = None; score = 0
    for faq in faqs:
        hay = f"{faq.question} {faq.keywords}".lower()
        tokens = [t for t in clean.split() if len(t) > 2]
        current = sum(1 for t in tokens if t in hay)
        if clean in hay: current += 5
        if current > score:
            best, score = faq, current
    if best and score > 0:
        cat = db.get(Category, best.category_id)
        resp = {"found": True, "question": best.question, "answer": best.answer, "category": cat.name if cat else ""}
        db.add(QueryLog(telegram_user=telegram_user, query_text=q, response_text=best.answer, matched_type="faq", category=resp["category"]))
        db.commit()
        return resp
    msg = db.get(Setting, "unknown_message")
    answer = msg.value if msg else "No encontré respuesta registrada."
    db.add(QueryLog(telegram_user=telegram_user, query_text=q, response_text=answer, matched_type="unknown", category=""))
    db.commit()
    return {"found": False, "answer": answer}

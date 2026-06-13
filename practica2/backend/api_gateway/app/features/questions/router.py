from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import get_current_admin
from app.db.models import Category, Question
from app.db.session import get_db

router = APIRouter(prefix="/api/questions", tags=["questions"])


class QuestionIn(BaseModel):
    text: str = Field(min_length=3, max_length=500)
    keywords: str = Field(default="", max_length=500)
    category_id: int
    is_active: bool = True


@router.get("")
def list_questions(db: Session = Depends(get_db)):
    return db.query(Question).order_by(Question.id).all()


@router.post("", dependencies=[Depends(get_current_admin)])
def create_question(payload: QuestionIn, db: Session = Depends(get_db)):
    if not db.get(Category, payload.category_id):
        raise HTTPException(422, "Categoria no encontrada")
    obj = Question(**payload.model_dump())
    db.add(obj)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(409, "Ya existe una pregunta con ese texto") from exc
    db.refresh(obj)
    return obj


@router.put("/{question_id}", dependencies=[Depends(get_current_admin)])
def update_question(question_id: int, payload: QuestionIn, db: Session = Depends(get_db)):
    obj = db.get(Question, question_id)
    if not obj:
        raise HTTPException(404, "Pregunta no encontrada")
    if not db.get(Category, payload.category_id):
        raise HTTPException(422, "Categoria no encontrada")
    for key, value in payload.model_dump().items():
        setattr(obj, key, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(409, "Ya existe una pregunta con ese texto") from exc
    db.refresh(obj)
    return obj


@router.delete("/{question_id}", dependencies=[Depends(get_current_admin)])
def delete_question(question_id: int, db: Session = Depends(get_db)):
    obj = db.get(Question, question_id)
    if not obj:
        raise HTTPException(404, "Pregunta no encontrada")
    db.delete(obj)
    db.commit()
    return {"deleted": True, "id": question_id}

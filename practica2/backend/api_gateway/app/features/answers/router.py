from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.security import get_current_admin
from app.db.models import Answer, Question
from app.db.session import get_db

router = APIRouter(prefix="/api/answers", tags=["answers"])


class AnswerIn(BaseModel):
    question_id: int
    text: str = Field(min_length=2, max_length=2000)
    priority: int = Field(default=1, ge=1, le=100)
    is_active: bool = True


@router.get("")
def list_answers(db: Session = Depends(get_db)):
    return db.query(Answer).order_by(Answer.question_id, Answer.priority, Answer.id).all()


@router.post("", dependencies=[Depends(get_current_admin)])
def create_answer(payload: AnswerIn, db: Session = Depends(get_db)):
    if not db.get(Question, payload.question_id):
        raise HTTPException(422, "Pregunta no encontrada")
    obj = Answer(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/{answer_id}", dependencies=[Depends(get_current_admin)])
def update_answer(answer_id: int, payload: AnswerIn, db: Session = Depends(get_db)):
    obj = db.get(Answer, answer_id)
    if not obj:
        raise HTTPException(404, "Respuesta no encontrada")
    if not db.get(Question, payload.question_id):
        raise HTTPException(422, "Pregunta no encontrada")
    for key, value in payload.model_dump().items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{answer_id}", dependencies=[Depends(get_current_admin)])
def delete_answer(answer_id: int, db: Session = Depends(get_db)):
    obj = db.get(Answer, answer_id)
    if not obj:
        raise HTTPException(404, "Respuesta no encontrada")
    db.delete(obj)
    db.commit()
    return {"deleted": True, "id": answer_id}

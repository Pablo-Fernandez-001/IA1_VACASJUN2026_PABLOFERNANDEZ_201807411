import re
import unicodedata

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.models import Answer, Category, QueryLog, Question, Setting
from app.db.session import get_db

router = APIRouter(prefix="/api/search", tags=["search"])


def normalize(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return " ".join(re.findall(r"[a-z0-9]+", ascii_value.lower()))


@router.get("")
def search(
    q: str = Query(min_length=2, max_length=500),
    telegram_user: str = "panel",
    db: Session = Depends(get_db),
):
    clean = normalize(q)
    tokens = {token for token in clean.split() if len(token) > 2}
    questions = db.query(Question).filter(Question.is_active.is_(True)).all()
    best = None
    best_score = 0
    for question in questions:
        haystack = normalize(f"{question.text} {question.keywords}")
        score = sum(1 for token in tokens if token in haystack)
        if clean == normalize(question.text):
            score += 20
        elif clean and clean in haystack:
            score += 5
        if score > best_score:
            best = question
            best_score = score

    if best and best_score > 0:
        answer = (
            db.query(Answer)
            .filter(Answer.question_id == best.id, Answer.is_active.is_(True))
            .order_by(Answer.priority, Answer.id)
            .first()
        )
        if answer:
            category = db.get(Category, best.category_id)
            category_name = category.name if category else ""
            db.add(QueryLog(
                telegram_user=telegram_user,
                query_text=q,
                response_text=answer.text,
                matched_type="faq",
                category=category_name,
            ))
            db.commit()
            return {
                "found": True,
                "question_id": best.id,
                "question": best.text,
                "answer": answer.text,
                "category": category_name,
                "score": best_score,
            }

    setting = db.get(Setting, "unknown_message")
    message = setting.value if setting else "No encontre una respuesta registrada."
    db.add(QueryLog(
        telegram_user=telegram_user,
        query_text=q,
        response_text=message,
        matched_type="unknown",
        category="",
    ))
    db.commit()
    return {"found": False, "answer": message}

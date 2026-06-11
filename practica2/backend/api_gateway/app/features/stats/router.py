from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.core.security import get_current_admin
from app.db.models import Category, Faq, QueryLog
from app.db.session import get_db

router = APIRouter(prefix="/api/stats", tags=["stats"])

@router.get("", dependencies=[Depends(get_current_admin)])
def stats(db: Session = Depends(get_db)):
    total = db.query(QueryLog).count()
    users = db.query(QueryLog.telegram_user).distinct().count()
    by_type = db.query(QueryLog.matched_type, func.count(QueryLog.id)).group_by(QueryLog.matched_type).all()
    top_queries = db.query(QueryLog.query_text, func.count(QueryLog.id).label("total")).group_by(QueryLog.query_text).order_by(func.count(QueryLog.id).desc()).limit(10).all()
    categories = db.query(QueryLog.category, func.count(QueryLog.id)).group_by(QueryLog.category).order_by(func.count(QueryLog.id).desc()).limit(10).all()
    return {
        "total_queries": total,
        "unique_users": users,
        "by_type": [{"type": t or "sin tipo", "total": c} for t,c in by_type],
        "top_queries": [{"query": q, "total": c} for q,c in top_queries],
        "categories": [{"category": cat or "sin categoría", "total": c} for cat,c in categories]
    }

@router.get("/logs", dependencies=[Depends(get_current_admin)])
def logs(db: Session = Depends(get_db)):
    return db.query(QueryLog).order_by(QueryLog.created_at.desc()).limit(100).all()

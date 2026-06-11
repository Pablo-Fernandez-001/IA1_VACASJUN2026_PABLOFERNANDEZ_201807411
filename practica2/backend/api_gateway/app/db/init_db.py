import json
from pathlib import Path
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.db.models import AdminUser, Category, Diagnosis, DiagnosticRule, Faq, RuleSymptom, Setting, Symptom
from app.db.session import Base, engine

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SEED_PATH = Path(__file__).resolve().parents[2] / "seeds" / "seed_data.json"


def init_db(db: Session):
    Base.metadata.create_all(bind=engine)
    if not db.query(AdminUser).filter_by(username="IA1-User").first():
        db.add(AdminUser(username="IA1-User", password_hash=pwd_context.hash("IA1-password@_new")))

    if not db.query(Setting).filter_by(key="telegram_chat_id").first():
        db.add(Setting(key="telegram_chat_id", value="", description="Chat o grupo de Telegram para enviar mensajes"))
    if not db.query(Setting).filter_by(key="unknown_message").first():
        db.add(Setting(key="unknown_message", value="No encontré una respuesta exacta. Prueba con /diagnostico o escribe otra consulta.", description="Mensaje cuando no hay FAQ"))

    # No se guardan FAQ ni reglas en código fuente. Se cargan desde archivo JSON de semilla.
    if db.query(Category).count() == 0 and SEED_PATH.exists():
        data = json.loads(SEED_PATH.read_text(encoding="utf-8"))
        cat_map = {}
        for c in data["categories"]:
            obj = Category(**c)
            db.add(obj); db.flush(); cat_map[c["name"]] = obj.id
        for f in data["faqs"]:
            db.add(Faq(question=f["question"], answer=f["answer"], keywords=f.get("keywords", ""), category_id=cat_map[f["category"]]))
        sym_map = {}
        for s in data["symptoms"]:
            obj = Symptom(**s)
            db.add(obj); db.flush(); sym_map[s["code"]] = obj.id
        diag_map = {}
        for d in data["diagnoses"]:
            d = dict(d)
            d["solution_route"] = json.dumps(d.get("solution_route", []), ensure_ascii=False)
            obj = Diagnosis(**d)
            db.add(obj); db.flush(); diag_map[d["code"]] = obj.id
        for r in data["rules"]:
            rule = DiagnosticRule(name=r["name"], diagnosis_id=diag_map[r["diagnosis_code"]], weight=r.get("weight", 100.0), explanation=r.get("explanation", ""))
            db.add(rule); db.flush()
            for code in r.get("symptoms", []):
                db.add(RuleSymptom(rule_id=rule.id, symptom_id=sym_map[code], required=True))
    db.commit()

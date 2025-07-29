# DB와 직접 상호작용(Create, Read, Update, Delete) 담당
# router.py에서 DB 코드를 반복하지 않도록 역할 분리용 -> router.py에서 import crud


from sqlalchemy.orm import Session
from app.core.search.models import Paper
from app.core.search.schemas import PaperCreate

def create_paper(db: Session, paper: PaperCreate):
    db_paper = Paper(**paper.dict())
    db.add(db_paper)
    db.commit()
    db.refresh(db_paper)
    return db_paper


def get_paper(db: Session, paper_id: int):
    return db.query(Paper).filter(Paper.id == paper_id).first()

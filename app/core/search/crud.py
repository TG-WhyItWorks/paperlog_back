# DB와 직접 상호작용(Create, Read, Update, Delete) 담당
# router.py에서 DB 코드를 반복하지 않도록 역할 분리용 -> router.py에서 import crud


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.search.models import Paper
from app.core.search.schemas import PaperCreate

async def create_paper(db: AsyncSession, paper: PaperCreate):
    db_paper = Paper(**paper.dict())
    db.add(db_paper)
    await db.commit()
    await db.refresh(db_paper)
    return db_paper


async def get_paper(db: AsyncSession, paper_id: int):
    result = await db.execute(select(Paper).filter(Paper.id == paper_id))
    return result.scalar_one_or_none()

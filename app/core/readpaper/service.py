from datetime import datetime,UTC
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.readpaper.schemas import ReadPaperCreate,ReadPaperUpdate
from app.core.search.models import Paper
from app.core.readpaper.models import ReadPaper
from sqlalchemy import func
from typing import List



async def get_readpaper(db: AsyncSession, readpaper_id: int):
    stmt = select(ReadPaper).options(selectinload(ReadPaper.user),selectinload(ReadPaper.paper)).where(ReadPaper.id == readpaper_id)
    result = await db.execute(stmt)
    return result.scalars().first()

async def create_readpaper(db: AsyncSession, readpaper_create: ReadPaperCreate):
    db_readpaper = ReadPaper(
        user_id=readpaper_create.user_id,
        paper_id=readpaper_create.paper_id,
        create_date=datetime.now(UTC)
    )
    db.add(db_readpaper)
    await db.commit()
    await db.refresh(db_readpaper)
    return db_readpaper



async def update_readpaper(db: AsyncSession, db_readpaper: ReadPaper, readpaper_update: ReadPaperUpdate):
    db_readpaper.user_id = readpaper_update.user_id
    db_readpaper.paper_id = readpaper_update.paper_id
    db.add(db_readpaper)
    await db.commit()
    await db.refresh(db_readpaper)
    return db_readpaper





async def delete_readpaper(db: AsyncSession, db_readpaper: ReadPaper):
    await db.delete(db_readpaper)
    await db.commit()




async def get_papers_read_by_user(
    db: AsyncSession,
    user_id: int
) -> List[Paper]:
    stmt = (
        select(Paper)
        .join(ReadPaper, ReadPaper.paper_id == Paper.id)
        .where(ReadPaper.user_id == user_id)
    )
    result = await db.execute(stmt)
    return result.scalars().all()
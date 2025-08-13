from datetime import datetime,UTC
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.readpaper.schemas import ReadPaperCreate,ReadPaperUpdate
from app.core.search.models import Paper
from app.core.user.models import User
from app.core.readpaper.models import ReadPaper
from sqlalchemy import func
from typing import List



async def get_readpaper(db: AsyncSession, readpaper_id: int):
    stmt = select(ReadPaper).options(selectinload(ReadPaper.user),selectinload(ReadPaper.paper)).where(ReadPaper.id == readpaper_id)
    result = await db.execute(stmt)
    return result.scalars().first()




async def get_mypaper(db: AsyncSession, user_id: int) -> List[Paper]:
    stmt = (
        select(Paper)
        .join(ReadPaper, ReadPaper.paper_id == Paper.id)
        .where(ReadPaper.user_id == user_id)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def create_readpaper(db: AsyncSession, readpaper_create: ReadPaperCreate, user: User):

    from sqlalchemy import select

    stmt = (
        select(ReadPaper)
        .where(
            (ReadPaper.user_id == user.id) &
            (ReadPaper.paper_id == readpaper_create.paper_id)
        )
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        
        return {"message": "이미 읽은 논문으로 등록되어 있습니다."}

    # 없으면 새로 추가
    db_readpaper = ReadPaper(
        user_id=user.id,
        paper_id=readpaper_create.paper_id,
        create_date=datetime.now(UTC)
    )
    user.readcount=user.readcount+1
    db.add(db_readpaper)
    await db.commit()
    await db.refresh(db_readpaper)
    return {"message": "리뷰가 성공적으로 작성되었습니다."}



async def update_readpaper(db: AsyncSession, db_readpaper: ReadPaper, readpaper_update: ReadPaperUpdate):
    db_readpaper.user_id = readpaper_update.user_id
    db_readpaper.paper_id = readpaper_update.paper_id
    db.add(db_readpaper)
    await db.commit()
    await db.refresh(db_readpaper)
    return db_readpaper





async def delete_readpaper(db: AsyncSession, db_readpaper: ReadPaper,user:User):
    user.readcount=max(0,user.readcount-1)   
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
from datetime import datetime,UTC
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from domain.readpaper.readpaper_schema import ReadPaperCreate, ReadPaperUpdate
from models import  User, ReadPaper, Paper
from sqlalchemy import func
from fastapi import HTTPException


async def get_readpaper(db: AsyncSession, readpaper_id: int):
        query_readpaper=select(ReadPaper).options(selectinload(ReadPaper.user)).where(ReadPaper.id == readpaper_id)
        result = await db.execute(query_readpaper)
        return result.scalars().first()
    
    
    
async def create_readpaper(db:AsyncSession, readpaper_create: ReadPaperCreate, user:User, paper: Paper) : 
    
    if paper is None:
       raise HTTPException(status_code=400, detail="Paper가 없습니다")
    
    db_readpaper=ReadPaper(
        user_id=user.id,
        paper_id=paper.id,
        rating=readpaper_create.rating,
        memo=readpaper_create.memo,
        create_date=datetime.now(UTC),
    )
    db.add(db_readpaper)
    await db.commit()
    await db.refresh(db_readpaper)
    return db_readpaper
    
    

async def update_readpaper(db:AsyncSession, db_readpaper:ReadPaper, readpaper_update: ReadPaperUpdate) : 
    db_readpaper.rating=readpaper_update.rating
    db_readpaper.memo=readpaper_update.memo
    db.add(db_readpaper)
    await db.commit()
    await db.refresh(db_readpaper)
    return db_readpaper


async def delete_readpaper(db: AsyncSession, db_readpaper: ReadPaper):
    await db.delete(db_readpaper)
    await db.commit()
    return {"detail": "삭제 완료"}















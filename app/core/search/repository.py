from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.search.models import Paper


async def get_paper_by_arxiv_id(db:AsyncSession, arxiv_id: str):
    return await db.get(Paper, arxiv_id)
    
    
async def save_paper(db: AsyncSession, paper_data: dict):
    paper = Paper(**paper_data)
    db.add(paper)
        
        
async def save_new_papers(db: AsyncSession, papers: list[dict]):
    for data in papers:
        existing_paper = await get_paper_by_arxiv_id(db, data["arxiv_id"])
        if not existing_paper:
            await save_paper(db, data)
    await db.commit()
    
async def get_paginated_papers(db:AsyncSession, page: int, page_size: int = 10):
    stmt = select(Paper).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    return result.scalars().all()
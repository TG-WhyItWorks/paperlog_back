from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.search.models import Paper
from datetime import datetime

def list_to_str(lst):
    if isinstance(lst, list):
        return ",".join(lst)
    return lst

async def get_paper_by_arxiv_id(db:AsyncSession, arxiv_id: str):
    stmt = select(Paper).filter(Paper.arxiv_id == arxiv_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
    
    
async def save_paper(db: AsyncSession, paper_data: dict):
    # list->str (db엔 list 저장 안되기 때문)
    paper_data["authors"] = list_to_str(paper_data.get("authors", ""))
    paper_data["categories"] = list_to_str(paper_data.get("categories", ""))
    
    paper = Paper(**paper_data)
    db.add(paper)
        
async def update_paper(db: AsyncSession, db_paper: Paper, paper_data: dict):
    
    if "authors" in paper_data:
        paper_data["authors"] = list_to_str(paper_data["authors"])
    if "categories" in paper_data:
        paper_data["categories"] = list_to_str(paper_data["categories"])
    
    # paper_data 내 필드를 db_paper에 업데이트
    for key, value in paper_data.items():
        setattr(db_paper, key, value)
    db_paper.updated_at = datetime.utcnow()
        
        
async def save_new_papers(db: AsyncSession, papers: list[dict]):
    for data in papers:
        existing_paper = await get_paper_by_arxiv_id(db, data["arxiv_id"])
        if not existing_paper:
            await save_paper(db, data)
        else:
            # publish_updated가 다르면 업데이트 처리
            if existing_paper.publish_updated != data["publish_updated"]:
                update_data = data.copy()
                update_data["publish_updated"] = update_data.pop("publish_updated")
                await update_paper(db, existing_paper, update_data)
    await db.commit()
    
    
    
async def get_paginated_papers(db:AsyncSession, page: int, page_size: int = 10):
    stmt = select(Paper).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    return result.scalars().all()
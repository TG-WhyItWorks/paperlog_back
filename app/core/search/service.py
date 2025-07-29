from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.core.search.models import Paper
from app.core.search import arxiv_parser, repository


async def search_and_store_papers(
    db:AsyncSession,
    query: str,
    sort_by: str = "relevance",
    sort_order: str = "descending",
    page: int = 1,
    page_size: int = 10
):
    papers = await arxiv_parser.fetch_arxiv_results(query=query, page=page, page_size=page_size, sort_by=sort_by, sort_order=sort_order)
    
    await repository.save_new_papers(db, papers)# DB에 중복 없이 저장
    
    return await repository.get_paginated_papers(db, page, page_size)


async def get_paper_with_reviews(db: AsyncSession, arxiv_id: str):
    result = await db.execute(
        select(Paper)
        .options(selectinload(Paper.reviews).selectinload("user"))
        .filter(Paper.arxiv_id == arxiv_id)
    )
    return result.scalar_one_or_none()
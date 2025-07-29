from sqlalchemy.ext.asyncio import AsyncSession
from app.core.search import arxiv_parser, repository

async def search_and_store_papers(
    db:AsyncSession,
    query: str,
    sort_by: str = "relevance",
    sort_order: str = "descending",
    page: int = 1,
    page_size: int = 10
):
    papers = arxiv_parser.fetch_arxiv_results(query=query, page=page, page_size=page_size, sort_by=sort_by, sort_order=sort_order)
    
    await repository.save_new_papers(db, papers)# DB에 중복 없이 저장
    
    return await repository.get_paginated_papers(db, page, page_size)


# 다음 : get_page_detail
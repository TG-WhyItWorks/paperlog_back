from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.common.dependencies import get_db
from app.core.search import service
from app.core.search.schemas import PaperOut

search_router = APIRouter()

@search_router.get("/", response_model=List[PaperOut])
async def search_papers(
    query: str = Query(..., description="검색어"),
    sort_by: str = Query("relevance", description="정렬 기준 : relevance, lastUpdatedDate, submittedDate"),
    sort_order: str = Query("descending", description="정렬 순서 : ascending 또는 descending"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    page_size: int = Query(10, le=50, description="페이지당 논문 수"),
    db: AsyncSession = Depends(get_db)
):
    """Arxiv 논문 검색->DB에 저장->해당 페이지에 논문 반환"""
    return await service.search_and_store_papers(
        db=db,
        query=query,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size
    )

@search_router.get("/{arxiv_id}", response_model=PaperOut)
async def get_paper_detail(arxiv_id: str, db: AsyncSession = Depends(get_db)):
    paper = await service.get_paper_with_reviews(db, arxiv_id=arxiv_id)
    if not paper:
        raise HTTPException(status_code=404, detail="논문을 찾을 수 없습니다.")
    return paper
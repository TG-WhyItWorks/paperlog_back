from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.common.dependencies import get_db, get_current_user, get_current_user_optional
from app.core.search import service
from app.core.search.schemas import PaperOut, PaperLikeOut, PaperLikeCreate

search_router = APIRouter()

@search_router.get("/", response_model=List[PaperOut])
async def search_papers(
    query: str = Query(..., description="검색어"),
    sort_by: str = Query("relevance", description="정렬 기준 : relevance, lastUpdatedDate, submittedDate"),
    sort_order: str = Query("descending", description="정렬 순서 : ascending 또는 descending"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    page_size: int = Query(10, le=50, description="페이지당 논문 수"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """Arxiv 논문 검색->DB에 저장->해당 페이지에 논문 반환"""
    user_id = current_user.id if current_user else None
    
    papers_data = await service.search_and_store_papers(
        db=db,
        query=query,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
        user_id=user_id
    )
    
    return [PaperOut(**paper_dict) for paper_dict in papers_data]


@search_router.get("/{arxiv_id}", response_model=PaperOut)
async def get_paper_detail(
    arxiv_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    user_id = current_user.id if current_user else None
    
    paper_data = await service.get_paper_with_reviews_and_likes(
        db,
        arxiv_id=arxiv_id,
        user_id=user_id
    )
    
    if not paper_data:
        raise HTTPException(status_code=404, detail="논문을 찾을 수 없습니다.")
    
    return PaperOut(**paper_data)
    

@search_router.post("/{arxiv_id}/like")
async def toggle_paper_like(
    arxiv_id: str,
    db:AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    
    paper = await service.get_paper_with_reviews(db, arxiv_id)
    if not paper:
        raise HTTPException(status_code=404, detail="논문을 찾을 수 없습니다.")
    
    paper_id = paper.id
    result = await service.toggle_paper_like(db, current_user.id, paper_id)
    return result


@search_router.get("/users/liked")
async def get_my_liked_papers(
    page: int = Query(1, ge=1, description="페이지 번호"),
    page_size: int = Query(20, le=50, description="페이지당 논문 수"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    
    papers = await service.get_user_liked_papers(
        db,
        current_user.id,
        page,
        page_size
    )
    
    return [PaperOut.model_validate(paper, from_attributes=True) for paper in papers]


@search_router.get("/{paper_id}/like-count")
async def get_paper_like_count(
    paper_id: int,
    db: AsyncSession = Depends(get_db)
):
    like_count = await service.get_paper_like_count(db, paper_id)
    return {"paper_id": paper_id, "like_count": like_count}
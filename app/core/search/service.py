from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import Optional, List
from app.core.search.models import Paper, PaperLike
from app.core.search.schemas import PaperLikeCreate, PaperOut
from app.core.search import arxiv_parser, repository
from app.core.blog.models import Review


async def search_and_store_papers(
    db:AsyncSession,
    query: str,
    sort_by: str = "relevance",
    sort_order: str = "descending",
    page: int = 1,
    page_size: int = 10,
    user_id: Optional[int] = None
):
    papers = await arxiv_parser.fetch_arxiv_results(query=query, page=page, page_size=page_size, sort_by=sort_by, sort_order=sort_order)
    
    await repository.save_new_papers(db, papers)# DB에 중복 없이 저장
    
    return await repository.get_paginated_papers_with_like_info(db, page, page_size, user_id)


async def get_paper_with_reviews(db: AsyncSession, arxiv_id: str):
    result = await db.execute(
        select(Paper)
        .options(selectinload(Paper.reviews).selectinload(Review.user))
        .filter(Paper.arxiv_id == arxiv_id)
    )
    return result.scalar_one_or_none()



async def get_paper_with_reviews_and_likes(db: AsyncSession, arxiv_id: str, user_id: Optional[int] = None):
    result = await db.execute(
        select(Paper)
        .options(selectinload(Paper.reviews).selectinload(Review.user))
        .filter(Paper.arxiv_id == arxiv_id)
    )
    
    paper = result.scalar_one_or_none()
    
    if not paper:
        return None
    
    paper_dict = await repository.get_paginated_papers_with_like_info(db, arxiv_id, user_id)
    
    if paper_dict:
        paper_dict["reviews"] = paper.reviews
        
    return paper_dict



async def toggle_paper_like(
    db: AsyncSession,
    user_id: int,
    paper_id: int
) -> dict:
    like_repo = repository.PaperLikeRepository(db)
    
    existing_like = await like_repo.get_like(user_id, paper_id)
    
    if existing_like:
        await like_repo.remove_like(user_id, paper_id)
        like_count = await like_repo.get_like_count(paper_id)
        return {
            "is_liked": False,
            "like_count": like_count,
            "message": "좋아요가 취소되었습니다."
        }
    else:
        paper_like = PaperLikeCreate(paper_id=paper_id)
        await like_repo.create_like(user_id, paper_like)
        like_count = await like_repo.get_like_count(paper_id)
        return {
            "is_liked": True,
            "like_count": like_count,
            "message": "좋아요가 추가되었습니다."
        }
        
        
async def get_user_liked_papers(
    db:AsyncSession,
    user_id: int,
    page: int = 1,
    page_size: int = 20
) -> List[Paper]:
    
    like_repo = repository.PaperLikeRepository(db)
    skip = (page - 1) * page_size
    return await like_repo.get_user_liked_papers(user_id, skip, page_size)

async def get_paper_like_count(db: AsyncSession, paper_id: int) -> int:
    like_repo = repository.PaperLikeRepository(db)
    return await like_repo.get_like_count(paper_id)
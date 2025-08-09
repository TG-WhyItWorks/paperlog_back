from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, exists
from sqlalchemy.orm import selectinload
from typing import Optional, List
from app.core.search.models import Paper, PaperLike
from app.core.search.schemas import PaperLikeCreate
from datetime import datetime, UTC

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
    db_paper.updated_at = datetime.now(UTC)
        
        
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


async def get_paginated_papers_with_like_info(
    db: AsyncSession,
    page: int,
    page_size: int = 10,
    user_id: Optional[int] = None
):
    like_count_subq = (
        select(func.count(PaperLike.id))
        .where(PaperLike.paper_id == Paper.id)
        .scalar_subquery()
        .label("like_count")
    )
    
    if user_id:
        is_liked_subq = (
            select(func.count(PaperLike.id))
            .where(
                and_(
                    PaperLike.paper_id == Paper.id,
                    PaperLike.user_id == user_id
                )
            )
            .scalar_subquery() > 0
        ).label("is_liked")
        
        stmt = (
            select(Paper, like_count_subq, is_liked_subq)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
    else:
        stmt = (
            select(Paper, like_count_subq)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        
    result = await db.execute(stmt)
    
    papers_data = []
    for row in result:
        paper = row[0] # Paper 객체
        like_count = row[1] # 좋아요 수
        
        
        paper_dict = {
            "id": paper.id,
            "arxiv_id": paper.arxiv_id,
            "title": paper.title,
            "authors": paper.authors,
            "summary": paper.summary,
            "link": paper.link,
            "published": paper.published,
            "publish_updated": paper.publish_updated,
            "categories": paper.categories,
            "doi": paper.doi,
            "created_at": paper.created_at,
            "updated_at": paper.updated_at,
            "reviews": paper.reviews,
            "like_count": like_count
        }
        
        if user_id:
            is_liked = row[2] # 사용자 좋아요 여부
            paper_dict["is_liked"] = is_liked
            
        papers_data.append(paper_dict)
        
    return papers_data

async def get_papers_with_like_info(db: AsyncSession, arxiv_id: str, user_id: Optional[int] = None):
    """좋아요 정보를 포함한 특정 논문 조회"""
    
    like_count_subq = (
        select(func.count(PaperLike.id))
        .where(PaperLike.paper_id == Paper.id)
        .scalar_subquery()
        .label("like_count")
    )
    # 로그인 했을 때만 유저가 좋아요 했는지 체크
    if user_id:
        is_liked_subq = (
            select(func.count(PaperLike.id))
            .where(
                and_(
                    PaperLike.paper_id == Paper.id,
                    PaperLike.user_id == user_id
                )
            )
            .scalar_subquery() > 0
        ).label("is_liked")
        
        stmt = (
            select(Paper, like_count_subq, is_liked_subq)
            .filter(Paper.arxiv_id == arxiv_id)
        )
    else:
        stmt = (
            select(Paper, like_count_subq)
            .filter(Paper.arxiv_id == arxiv_id)
        )
        
    result = await db.execute(stmt)
    row = result.first()
    
    if not row:
        return None
    
    paper = row[0] # Paper 객체
    like_count = row[1] # 좋아요 수
    
    paper_dict = {
            #"id": paper.id,
            "arxiv_id": paper.arxiv_id,
            "title": paper.title,
            "authors": paper.authors,
            "summary": paper.summary,
            "link": paper.link,
            "published": paper.published,
            "publish_updated": paper.publish_updated,
            "categories": paper.categories,
            "doi": paper.doi if paper.doi!=None else 'str',
            "created_at": paper.created_at,
            "updated_at": paper.updated_at,
            "reviews": paper.reviews,
            "like_count": like_count
        }
    
    if user_id:
            is_liked = row[2] # 사용자 좋아요 여부
            paper_dict["is_liked"] = is_liked
            
    return paper_dict



class PaperLikeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def create_like(self, user_id: int, paper_like: PaperLikeCreate) -> PaperLike:
        db_like = PaperLike(
            user_id=user_id,
            paper_id=paper_like.paper_id
            )
        self.db.add(db_like)
        await self.db.commit()
        await self.db.refresh(db_like)
        return db_like
    
    
    async def remove_like(self, user_id: int, paper_id: int) -> bool:
        stmt = select(PaperLike).filter(
            and_(
                PaperLike.user_id == user_id,
                PaperLike.paper_id == paper_id
            )
        )
        result = await self.db.execute(stmt)
        like = result.scalar_one_or_none()
        
        if like:
            await self.db.delete(like)
            await self.db.commit()
            return True
        return False
    
    async def get_like(self, user_id: int, paper_id: int) -> Optional[PaperLike]:
        stmt = select(PaperLike).filter(
            and_(
                PaperLike.user_id == user_id,
                PaperLike.paper_id == paper_id
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    
    async def is_liked_by_user(self, user_id: int, paper_id: int) -> bool:
        """사용자가 특정 논문 좋아요 했는지 확인"""
        stmt = select(PaperLike).filter(
            and_(
                PaperLike.user_id == user_id,
                PaperLike.paper_id == paper_id
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar()
    
    
    async def get_like_count(self, paper_id: int) -> int:
        stmt = select(func.count(PaperLike.id)).filter(
            PaperLike.paper_id == paper_id
        )
        result = await self.db.execute(stmt)
        return result.scalar() or 0
    
    async def get_user_liked_papers(self, user_id: int, skip: int = 0, limit: int = 20) -> List[Paper]:
        """사용자가 좋아요 누른 논문 목록 조회(좋아요 누른 시각 내림차순)"""
        stmt = (
            select(Paper)
            .join(PaperLike)
            .filter(PaperLike.user_id == user_id)
            .options(selectinload(Paper.paper_likes))
            .order_by(PaperLike.liked_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
    

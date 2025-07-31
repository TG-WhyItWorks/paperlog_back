from datetime import datetime,UTC
from sqlalchemy import select, and_,or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.blog.schemas import ReviewCreate, ReviewUpdate
from app.core.user.models import User
from app.core.blog.models import Review,review_voter
from app.core.search.models import Paper
from app.core.comment.models import Comment
from sqlalchemy import func,desc,asc,func
from typing import List
async def search_reviews(
    db: AsyncSession, keyword: str = '', skip: int = 0, limit: int = 10
):
    query = select(Review)
    
    if keyword:
        search = f"%{keyword}%"
        from sqlalchemy.orm import aliased
        UserAlias = aliased(User)
        PaperAlias = aliased(Paper)
        query = (
            query
            .join(UserAlias, Review.user_id == UserAlias.id, isouter=True)
            .join(PaperAlias, Review.paper_id == PaperAlias.arxiv_id, isouter=True)
            
            .where(
                or_(
                    Review.title.ilike(search),
                    Review.content.ilike(search),
                    UserAlias.username.ilike(search),
                    PaperAlias.title.ilike(search),
                    
                )
            )
        )

    query = (
        query
        .order_by(Review.create_date.desc())
        .offset(skip)
        .limit(limit)
        .options(
            selectinload(Review.user),
            selectinload(Review.paper),
            selectinload(Review.images),
            selectinload(Review.voter),
        )
    )

    result = await db.execute(query)
    reviews = result.scalars().all()
    return reviews

async def get_reviews_list_vote(db: AsyncSession, limit: int = 10):
    
    stmt = (
        select(
            Review,
            func.count(review_voter.c.user_id).label("vote_count")
        )
        .outerjoin(review_voter, Review.id == review_voter.c.review_id)
        .group_by(Review.id)
        .order_by(desc("vote_count"))
        .limit(limit)
        .options(
            selectinload(Review.user),
            selectinload(Review.images),
            selectinload(Review.voter),
            selectinload(Review.paper),
        )
    )
    result = await db.execute(stmt)
   
    rows = result.all()
    return rows  


async def get_reviews_list_date(db: AsyncSession, limit: int = 10):
    stmt = (
        select(Review)
        .order_by(Review.create_date.desc())
        .limit(limit)
        .options(
            selectinload(Review.user),
            selectinload(Review.images),
            selectinload(Review.voter),
            selectinload(Review.paper),
        )
    )
    result = await db.execute(stmt)
    reviews = result.scalars().all()
    return reviews




async def get_review(db: AsyncSession, review_id: int):
    stmt = select(Review).options(selectinload(Review.user), selectinload(Review.images)).where(Review.id == review_id)
    result = await db.execute(stmt)
    return result.scalars().first()



async def create_review(db: AsyncSession, review_create: ReviewCreate, user: User):
    db_review = Review(
        title=review_create.title,
        content=review_create.content,
        create_date=datetime.now(UTC),
        user_id=user.id  
    )
    db.add(db_review)
    await db.commit()
    await db.refresh(db_review)
    return db_review


async def update_review(db: AsyncSession, db_review: Review, review_update: ReviewUpdate):
    db_review.title = review_update.title
    db_review.content = review_update.content
    db_review.modify_date = datetime.now(UTC)
    db.add(db_review)
    await db.flush()
    await db.commit()
    return db_review





async def delete_review(db: AsyncSession, db_review: Review):
    await db.delete(db_review)
    await db.commit()







async def vote_review(db: AsyncSession, review_id: int, user: User):
    
    stmt = (
        select(Review)
        .options(selectinload(Review.voter))
        .where(Review.id == review_id)
    )
    result = await db.execute(stmt)
    db_review = result.scalars().first()
    if not db_review:
        raise Exception("리뷰를 찾을 수 없습니다.")

    
    if user not in db_review.voter:
        db_review.voter.append(user)
        await db.commit()
        await db.refresh(db_review)
    return db_review



async def get_review_vote_count(db: AsyncSession, review_id: int) -> int:
    
    stmt = select(func.count()).select_from(review_voter).where(
        review_voter.c.review_id == review_id
    )
    result = await db.execute(stmt)
    vote_count = result.scalar_one()
    return vote_count




async def get_liked_review(db:AsyncSession,user:User)->List[Review]:
    stmt = (
        select(Review)
        .join(review_voter, review_voter.c.review_id == Review.id)
        .where(review_voter.c.user_id == user.id)
        .options(selectinload(Review.user), selectinload(Review.images))
    )
    result = await db.execute(stmt)
    return result.scalars().all()











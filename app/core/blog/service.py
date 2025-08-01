from datetime import datetime,UTC
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.blog.schemas import ReviewCreate, ReviewUpdate
from app.core.user.models import User
from app.core.blog.models import Review
from app.core.comment.models import Comment
from sqlalchemy import func



async def get_review_list(db: AsyncSession, skip: int = 0, limit: int = 10, keyword: str = ''):
    base_query = select(Review).options(selectinload(Review.user)).order_by(Review.create_date.desc())

    if keyword:
        keyword_pattern = f"%{keyword}%"
        comment_subquery = (
            select(Comment.review_id, Comment.content, User.username)
            .join(User, Comment.user_id == User.id, isouter=True)
            .subquery()
        )

        base_query = (
            base_query
            .join(User, Review.user_id == User.id, isouter=True)
            .join(comment_subquery, comment_subquery.c.review_id == Review.id, isouter=True)
            .where(
                Review.title.ilike(keyword_pattern) |
                Review.content.ilike(keyword_pattern) |
                User.username.ilike(keyword_pattern) |
                comment_subquery.c.content.ilike(keyword_pattern) |
                comment_subquery.c.username.ilike(keyword_pattern)
            )
        )

    count_query = base_query.with_only_columns(Review.id).subquery()
    
    total_result = await db.execute(select(func.count()).select_from(count_query))

    total = total_result.scalar_one()

    result = await db.execute(base_query.offset(skip).limit(limit))
    review_list = result.unique().scalars().all()

    return total, review_list



async def get_review(db: AsyncSession, review_id: int):
    stmt = select(Review).options(selectinload(Review.user)).where(Review.id == review_id)
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
    await db.refresh(db_review)
    return db_review



async def delete_review(db: AsyncSession, db_review: Review):
    await db.delete(db_review)
    await db.commit()

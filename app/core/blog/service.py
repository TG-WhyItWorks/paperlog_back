from datetime import datetime,UTC
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.blog.schemas import ReviewCreate, ReviewUpdate
from app.core.user.models import User
from app.core.blog.models import Review
from app.core.comment.models import Comment
from sqlalchemy import func







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
    await db.refresh(db_review)
    return db_review



async def delete_review(db: AsyncSession, db_review: Review):
    await db.delete(db_review)
    await db.commit()



async def vote_review(db: AsyncSession, db_review: Review, db_user: User):
    db_review.voter.append(db_user)
    await db.commit()
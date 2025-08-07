from datetime import datetime
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound

from app.core.comment.schemas import CommentCreate, CommentUpdate
from app.core.user.models import User
from app.core.blog.models import Review
from app.core.comment.models import Comment


async def create_comment(db: AsyncSession, review: Review, comment_create: CommentCreate, user: User):
    db_comment = Comment(
        review=review,
        content=comment_create.content,
        create_date=datetime.now(),
        user=user
    )
    if review is None:
        return {"message": "리뷰가 없습니다."}
    db.add(db_comment)
    await db.commit()
    await db.refresh(db_comment)
    return db_comment





async def get_comment(db: AsyncSession, comment_id: int) -> Comment | None:
    result = await db.execute(select(Comment).options(selectinload(Comment.user)).where(Comment.id == comment_id))
    return result.scalar_one_or_none()



async def get_comments_by_review(db: AsyncSession, review_id: int):
    stmt = (
     select(Comment).options(
            selectinload(Comment.user)
     )
    .where(Comment.review_id == review_id)
    
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_my_comments(db: AsyncSession, user:User):
    stmt = (
     select(Comment)
    .where(Comment.user_id == user.id)
    
    )
    result = await db.execute(stmt)
    return result.scalars().all()



async def update_comment(db: AsyncSession, db_comment: Comment, comment_update: CommentUpdate):
    db_comment.content = comment_update.content
    db_comment.modify_date = datetime.now()
    await db.commit()
    await db.refresh(db_comment)

async def delete_comment(db: AsyncSession, db_comment: Comment):
    await db.delete(db_comment)
    await db.commit()
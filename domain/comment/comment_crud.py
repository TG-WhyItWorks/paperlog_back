from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound

from domain.comment.comment_schema import CommentCreate, CommentUpdate
from models import Review, Comment, User


async def create_comment(db: AsyncSession, review: Review, comment_create: CommentCreate, user: User):
    db_comment = Comment(
        review=review,
        content=comment_create.content,
        create_date=datetime.now(),
        user=user
    )
    db.add(db_comment)
    await db.commit()
    await db.refresh(db_comment)
    return db_comment

async def get_comment(db: AsyncSession, comment_id: int) -> Comment | None:
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    return result.scalar_one_or_none()

async def update_comment(db: AsyncSession, db_comment: Comment, comment_update: CommentUpdate):
    db_comment.content = comment_update.content
    db_comment.modify_date = datetime.now()
    await db.commit()
    await db.refresh(db_comment)

async def delete_comment(db: AsyncSession, db_comment: Comment):
    await db.delete(db_comment)
    await db.commit()
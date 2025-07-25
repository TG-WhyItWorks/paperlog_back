from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from database import get_db
from domain.comment import comment_schema, comment_crud
from domain.review import review_crud
from domain.user.user_router import get_current_user
from models import User

router = APIRouter(prefix="/api/comment",tags=["Comment"])




@router.post("/create/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def comment_create(
    review_id: int,
    _comment_create: comment_schema.CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    review = await review_crud.get_review(db, review_id=review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review is not found")
    
    await comment_crud.create_comment(
        db=db,
        review=review,
        comment_create=_comment_create,
        user=current_user
    )



@router.get("/detail/{comment_id}", response_model=comment_schema.Comment)
async def comment_detail(comment_id: int, db: AsyncSession = Depends(get_db)):
    comment = await comment_crud.get_comment(db, comment_id=comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="댓글이 존재하지 않습니다.")
    return comment


@router.put("/update", status_code=status.HTTP_204_NO_CONTENT)
async def comment_update(
    _comment_update: comment_schema.CommentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_comment = await comment_crud.get_comment(db, comment_id=_comment_update.comment_id)
    if not db_comment:
        raise HTTPException(status_code=400, detail="데이터를 찾을 수 없습니다.")
    if current_user.id != db_comment.user.id:
        raise HTTPException(status_code=400, detail="수정 권한이 없습니다.")
    
    await comment_crud.update_comment(
        db=db,
        db_comment=db_comment,
        comment_update=_comment_update
    )


@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
async def comment_delete(
    _comment_delete: comment_schema.CommentDelete,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_comment = await comment_crud.get_comment(db, comment_id=_comment_delete.comment_id)
    if not db_comment:
        raise HTTPException(status_code=400, detail="데이터를 찾을 수 없습니다.")
    if current_user.id != db_comment.user.id:
        raise HTTPException(status_code=400, detail="삭제 권한이 없습니다.")
    
    await comment_crud.delete_comment(db=db, db_comment=db_comment)





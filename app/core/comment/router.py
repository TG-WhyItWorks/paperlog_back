from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from typing import List
from app.common.dependencies import get_db
from app.core.comment import schemas as comment_schema
from app.core.comment import service as comment_crud
from app.core.blog import service as review_crud
from app.common.dependencies import get_current_user
from app.core.user.models import User

comment_router = APIRouter()


@comment_router.post("/create/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def comment_create(
    review_id: int,
    _comment_create: comment_schema.CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    review = await review_crud.get_review(db, review_id=review_id)
    if not review:
        return {"message": "리뷰가 없습니다"}
    
    await comment_crud.create_comment(
        db=db,
        review=review,
        comment_create=_comment_create,
        user=current_user
    )



@comment_router.get("/detail/{comment_id}", response_model=comment_schema.Comment)
async def comment_detail(comment_id: int, db: AsyncSession = Depends(get_db)):
    comment = await comment_crud.get_comment(db, comment_id=comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="댓글이 존재하지 않습니다.")
    return comment



@comment_router.get("/review/{review_id}/comments", response_model=List[comment_schema.Comment])
async def comments_by_review(
    review_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await comment_crud.get_comments_by_review(db, review_id)


@comment_router.get("/my/comments", response_model=List[comment_schema.Comment])
async def comments_by_review(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await comment_crud.get_my_comments(db,user) 





@comment_router.put("/update", status_code=status.HTTP_204_NO_CONTENT)
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


@comment_router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
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





from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from fastapi import Form, File, UploadFile
from typing import Optional
from app.common.dependencies import get_db
from app.core.blog import schemas, service
from app.common.dependencies import get_current_user
from app.core.user.models import User

review_router = APIRouter()


# ✅ 리뷰 목록 조회
@review_router.get("/list", response_model=schemas.ReviewList)
async def review_list(
    db: AsyncSession = Depends(get_db),
    page: int = 0,
    size: int = 10,
    keyword: str = ""
):
    total, _review_list = await service.get_review_list(
        db, skip=page * size, limit=size, keyword=keyword
    )
    return {
        "total": total,
        "review_list": _review_list
    }


# ✅ 리뷰 상세 조회
@review_router.get("/detail/{review_id}", response_model=schemas.Review)
async def review_detail(review_id: int, db: AsyncSession = Depends(get_db)):
    review = await service.get_review(db, review_id=review_id)
    if not review:
        raise HTTPException(status_code=404, detail="리뷰를 찾을 수 없습니다.")
    return review


# ✅ 리뷰 작성
@review_router.post("/create", status_code=201)
async def review_create(
    _review_create:schemas.ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await service.create_review(db=db, review_create=_review_create, user=current_user)
    return {"message": "리뷰가 성공적으로 작성되었습니다."}

# ✅ 리뷰 수정
@review_router.put("/update", status_code=200)
async def review_update(
    _review_update: schemas.ReviewUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_review = await service.get_review(db, review_id=_review_update.review_id)
    if not db_review:
        raise HTTPException(status_code=400, detail="데이터를 찾을 수 없습니다")
    if not db_review.user or current_user.id != db_review.user.id:
        raise HTTPException(status_code=403, detail="수정할 권한이 없습니다")
    await service.update_review(db=db, db_review=db_review, review_update=_review_update)
    return {"message": "리뷰가 성공적으로 수정되었습니다."}

# ✅ 리뷰 삭제
@review_router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
async def review_delete(
    _review_delete: schemas.ReviewDelete,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_review = await service.get_review(db, review_id=_review_delete.review_id)
    if not db_review:
        raise HTTPException(status_code=400, detail="데이터를 찾을 수 없습니다")
    if not db_review.user or current_user.id != db_review.user.id:
        raise HTTPException(status_code=403, detail="삭제 권한이 없습니다")
    await service.delete_review(db=db, db_review=db_review)
    return {"message": "삭제 완료"}
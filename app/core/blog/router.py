from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from fastapi import Form, File, UploadFile,Query
from typing import Optional,List
from app.common.dependencies import get_db
from app.core.blog import schemas, service
from app.common.dependencies import get_current_user
from app.core.user.models import User
from app.core.blog.models import Review
review_router = APIRouter()

#검색- 제목 내용 글쓴이
@review_router.get("/search", response_model=List[schemas.ReviewOutSimple])
async def search_review_list(
    keyword: str = Query('', description="검색어"),
    skip: int = Query(0, ge=0, description="건너뛸 개수(페이징)"),
    limit: int = Query(10, le=100, description="가져올 개수(페이징)"),
    db: AsyncSession = Depends(get_db)
):
 
    reviews = await service.search_reviews(db=db, keyword=keyword, skip=skip, limit=limit)
    return reviews

#검색- 제목 내용 글쓴이 + 좋아요 순으로 ... 
@review_router.get("/search_voteorder", response_model=List[schemas.ReviewOutSimple])
async def search_review_list(
    keyword: str = Query('', description="검색어"),
    skip: int = Query(0, ge=0, description="건너뛸 개수(페이징)"),
    limit: int = Query(10, le=100, description="가져올 개수(페이징)"),
    db: AsyncSession = Depends(get_db)
):
 
    reviews = await service.search_reviews_VoteOrder(db=db, keyword=keyword, skip=skip, limit=limit)
    return reviews


#제목 기준 리뷰검색
@review_router.get("/search/title", response_model=List[schemas.ReviewOutSimple])
async def search_review_list_title(
    keyword: str = Query('', description="검색어"),
    skip: int = Query(0, ge=0, description="건너뛸 개수(페이징)"),
    limit: int = Query(10, le=100, description="가져올 개수(페이징)"),
    db: AsyncSession = Depends(get_db)
):
 
    reviews = await service.search_reviews_title(db=db, keyword=keyword, skip=skip, limit=limit)
    return reviews

#내용 기준 리뷰검색
@review_router.get("/search/cotent", response_model=List[schemas.ReviewOutSimple])
async def search_review_list_content(
    keyword: str = Query('', description="검색어"),
    skip: int = Query(0, ge=0, description="건너뛸 개수(페이징)"),
    limit: int = Query(10, le=100, description="가져올 개수(페이징)"),
    db: AsyncSession = Depends(get_db)
):
 
    reviews = await service.search_reviews_content(db=db, keyword=keyword, skip=skip, limit=limit)
    return reviews

#user기준 리뷰 검색
@review_router.get("/search/review/user", response_model=List[schemas.ReviewOutSimple])
async def search_review_list_user(
    keyword: str = Query('', description="검색어"),
    skip: int = Query(0, ge=0, description="건너뛸 개수(페이징)"),
    limit: int = Query(10, le=100, description="가져올 개수(페이징)"),
    db: AsyncSession = Depends(get_db)
):
 
    reviews = await service.search_reviews_user(db=db, keyword=keyword, skip=skip, limit=limit)
    return reviews











#리뷰 날짜 최신부터
@review_router.get("/list/dates/desc", response_model=List[schemas.ReviewOutSimple])
async def get_reviews_list_date_desc(db: AsyncSession = Depends(get_db)):
    return await service.get_reviews_list_date_desc(db, limit=10)

#리뷰 날짜 옛날부터
@review_router.get("/list/dates/asc", response_model=List[schemas.ReviewOutSimple])
async def get_reviews_list_date_asc(db: AsyncSession = Depends(get_db)):
    return await service.get_reviews_list_date_asc(db, limit=10)



#리뷰 좋아요순으로
@review_router.get("/list/vote/desc", response_model=List[schemas.ReviewOutSimple])
async def get_reviews_list_vote(db: AsyncSession = Depends(get_db)):
    return await service.get_reviews_list_vote(db, limit=10)

#  리뷰 상세 조회
@review_router.get("/detail/{review_id}", response_model=schemas.Review)
async def review_detail(review_id: int, db: AsyncSession = Depends(get_db)):
    review = await service.get_review(db, review_id=review_id)
    if not review:
        raise HTTPException(status_code=404, detail="리뷰를 찾을 수 없습니다.")
    return review


#  리뷰 작성
@review_router.post("/create", status_code=201)
async def review_create(
    title: str = Form(...),
    content: str = Form(...),
    paper_id: Optional[int] = Form(None),
    images: Optional[List[UploadFile]] = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    review_data = schemas.ReviewCreate(title=title, content=content, paper_id=paper_id)
    await service.create_review(
        db=db,
        review_create=review_data,
        user=current_user,
        images=images,
    )
    return {"message": "리뷰가 성공적으로 작성되었습니다."}

#  리뷰 수정
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

# 리뷰 삭제
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



#좋아요
@review_router.post("/vote/{review_id}", status_code=204)
async def review_vote(
    review_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await service.vote_review(db, review_id, current_user)




#좋아요 삭제하기
@review_router.delete("/reviews/{review_id}/like")
async def like_delete(
    review_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await service.delte_vote(db, current_user.id, review_id)
    return result

#내가 쓴 리뷰
@review_router.get("/my/reviews", response_model=List[schemas.ReviewOutSimple])
async def get_my_reivews(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_my_reviews(db,user) 



#리뷰의 좋아요 수 세기
@review_router.get("/vote_count/{review_id}")
async def get_vote_count(
    review_id: int,
    db: AsyncSession = Depends(get_db)
):
    count = await service.get_review_vote_count(db, review_id)
    return {"review_id": review_id, "vote_count": count}

#좋아요 한 리뷰 불러오기
@review_router.get("/liked-reviews", response_model=List[schemas.ReviewOutSimple])
async def liked_reviews(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.get_liked_review(db, current_user)








from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.common.dependencies import get_db,get_current_user  


from app.core.user.models import User
from app.core.search.models import Paper
from app.core.readpaper import service, schemas




#readpaper_router = APIRouter()

''''

async def _load_readpaper_with_relations(
    db: AsyncSession, readpaper_id: int
) -> ReadPaperModel | None:
    stmt = (
        select(ReadPaperModel)
        .options(selectinload(ReadPaperModel.paper))
        .where(ReadPaperModel.id == readpaper_id)
    )
    result = await db.execute(stmt)
    return result.scalars().first()


    
# --- 내 ReadPaper 전체 조회 ---
@readpaper_router.get(
    "/me",
    response_model=List[schemas.ReadPaper],
    summary="내 ReadPaper 목록 조회",
)
async def list_my_readpapers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    records = await service.get_readpaper_records_by_user(db=db, user_id=current_user.id)
    return records


# --- 단건 조회 ---
@readpaper_router.get(
    "/{readpaper_id}",
    response_model=schemas.ReadPaper,
    summary="ReadPaper 단건 조회",
)
async def get_readpaper_detail(
    readpaper_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rp = await _load_readpaper_with_relations(db, readpaper_id)
    if not rp:
        raise HTTPException(status_code=404, detail="ReadPaper를 찾을 수 없습니다.")
    if rp.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="접근 권한이 없습니다.")
    return rp


# --- 생성 ---
@readpaper_router.post(
    "/{arxiv_id}",
    response_model=schemas.ReadPaper,
    status_code=status.HTTP_201_CREATED,
    summary="ReadPaper 생성",
)
async def create_readpaper(
    arxiv_id: str,  # arXiv ID를 경로 파라미터로 받습니다.
    readpaper_create: schemas.ReadPaperCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 논문 존재 확인
    result = await db.execute(select(Paper).where(Paper.arxiv_id == arxiv_id))
    paper = result.scalars().first()
    # service.create_readpaper 내부에서도 paper None 체크를 하지만, 빠른 피드백을 위해 여기서도 처리
    if paper is None:
        raise HTTPException(status_code=400, detail="Paper가 없습니다")

    created = await service.create_readpaper(
        db=db, readpaper_create=readpaper_create, user=current_user, paper=paper
    )
    # 방금 생성한 객체를 관계 포함해서 다시 로드하여 반환 (selectinload)
    reloaded = await _load_readpaper_with_relations(db, created.id)
    return reloaded


# --- 수정 ---
@readpaper_router.patch(
    "/{readpaper_id}",
    response_model=schemas.ReadPaper,
    summary="ReadPaper 수정",
)
async def update_readpaper(
    readpaper_id: int,
    readpaper_update: schemas.ReadPaperUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 소유권 및 존재 확인
    rp = await _load_readpaper_with_relations(db, readpaper_id)
    if not rp:
        raise HTTPException(status_code=404, detail="ReadPaper를 찾을 수 없습니다.")
    if rp.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="수정 권한이 없습니다.")

    updated = await service.update_readpaper(
        db=db, db_readpaper=rp, readpaper_update=readpaper_update
    )
    # 관계 포함하여 다시 로드
    reloaded = await _load_readpaper_with_relations(db, updated.id)
    return reloaded


# --- 삭제 ---
@readpaper_router.delete(
    "/{readpaper_id}",
    summary="ReadPaper 삭제",
)
async def delete_readpaper(
    readpaper_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rp = await _load_readpaper_with_relations(db, readpaper_id)
    if not rp:
        raise HTTPException(status_code=404, detail="ReadPaper를 찾을 수 없습니다.")
    if rp.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="삭제 권한이 없습니다.")

    result = await service.delete_readpaper(db=db, db_readpaper=rp)
    # service.delete_readpaper는 {"detail": "삭제 완료"} 를 반환
    return result



'''
















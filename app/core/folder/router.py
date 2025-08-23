from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, and_
from typing import List

from app.db.session import get_db
from app.core.user.models import User
from app.common.dependencies import get_current_user

from app.core.folder import schemas, repository, service
from app.core.folder.models import Folder, FolderPaper

folder_router = APIRouter()


def enrich_folder_schema(folder: Folder) -> schemas.FolderDetailResponse:
    # DB에서 미리 selectinload로 하위 폴더와 item 가져온 상태에서 동기 재귀로 모델 직렬화
    return schemas.FolderDetailResponse.from_orm_recursive(folder) # 동기 재귀


@folder_router.post("/", response_model=schemas.FolderResponse)
async def create_folder(folder_in: schemas.FolderCreate = Body(..., example={"folder_name":"My folder",  "parent_folder_id": None}),
                        db:AsyncSession = Depends(get_db),
                        user: User = Depends(get_current_user)):
    return await service.create_folder(db, folder_in, user)
    

@folder_router.put("/{folder_id}", response_model=schemas.FolderResponse)
async def update_folder(folder_id: int,
                        folder_in: schemas.FolderUpdate,
                        db: AsyncSession = Depends(get_db),
                        user: User = Depends(get_current_user)):
    folder = await repository.get_folder_by_id(db, folder_id)
    if not folder or folder.user_id != user.id:
        raise HTTPException(status_code=404, detail="Folder not found")
    return await service.update_folder(db, folder, folder_in, user)


@folder_router.delete("/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_folder(folder_id: int,
                        db: AsyncSession = Depends(get_db),
                        user: User = Depends(get_current_user)
):  
    await service.delete_folder(db, folder_id, user)
    
    
@folder_router.post("/{folder_id}/items")
async def add_item_to_folder(folder_id: int,
                             item: schemas.FolderPaperCreate,
                             db: AsyncSession = Depends(get_db),
                             user: User = Depends(get_current_user)):
    
    if folder_id != item.folder_id:
        raise HTTPException(status_code=400, detail="Folder ID mismatch")
    
    return await repository.create_folder_paper(db, folder_id=folder_id,
                                                folder_paper_name=item.folder_paper_name,
                                                user_id=user.id,
                                                paper_id=item.paper_id,
                                                review_id=item.review_id)
    

@folder_router.delete("/items/{folder_paper_id}")
async def remove_item_by_id(folder_paper_id: int,
                                  db: AsyncSession = Depends(get_db),
                                  user: User = Depends(get_current_user)):
    folder_paper = await repository.get_folder_paper_by_id(db, folder_paper_id)
    
    if not folder_paper:
        raise HTTPException(status_code=404, detail="Item not found in folder")
    
    if folder_paper.folder.user_id != user.id:
        raise HTTPException(status_code=403, detail="access denied")
    
    await repository.delete_folder_paper(db, folder_paper)
    return {"detail": "Deleted"}

@folder_router.delete("/{folder_id}/items")
async def remove_item_from_folder(
    folder_id: int,
    payload: schemas.FolderPaperDelete,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # URL ↔ payload 일치 확인
    if payload.folder_id != folder_id:
        raise HTTPException(status_code=400, detail="Folder ID mismatch")
    # 소유권 확인
    folder = await repository.get_folder_by_id(db, folder_id, user.id)
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found or access denied")
    # 항목 조회
    item = await repository.get_folder_paper(
        db,
        folder_id=folder_id,
        paper_id=payload.paper_id,
        review_id=payload.review_id,
        paper_arxiv_id=payload.paper_arxiv_id,
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item not found in folder")
    # 삭제
    await repository.delete_folder_paper(db, item)
    return {"detail": "Deleted"}



@folder_router.get("/root/{folder_id}", response_model=schemas.FolderDetailResponse)
async def get_folder_detail(folder_id: int,
                            db: AsyncSession = Depends(get_db),
                            user: User = Depends(get_current_user)):
    
    folder = await repository.get_folder_by_id_with_unlimited_tree(db, folder_id, user.id)
    
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found or access denied")
    
    return enrich_folder_schema(folder)



@folder_router.get("/root", response_model=List[schemas.FolderDetailResponse])
async def get_root_folder(db: AsyncSession = Depends(get_db),
                          user: User = Depends(get_current_user)):
    folders = await repository.get_root_folders_with_unlimited_tree(db, user.id)
    
    if not folders:
        raise HTTPException(status_code=404, detail="Root folder not found")
    
    return [enrich_folder_schema(f) for f in folders]
    

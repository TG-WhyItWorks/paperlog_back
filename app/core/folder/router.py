from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from typing import List

from app.db.session import get_db
from app.core.user.models import User
from app.common.dependencies import get_current_user

from app.core.folder import schemas, repository
from app.core.folder.models import Folder, FolderPaper

folder_router = APIRouter()


def enrich_folder_schema(folder: Folder) -> schemas.FolderDetailResponse:
    schema = schemas.FolderDetailResponse.model_validate(folder, from_attributes=True)
    
    for fp_schema, fp_model in zip(schema.folder_papers, folder.folder_papers):
            if fp_model.paper:
                fp_schema.paper_arxiv_id = fp_model.paper.arxiv_id
                fp_schema.paper_title = fp_model.paper.title
            else:
                fp_schema.paper_arxiv_id = None
                fp_schema.paper_title = None
            
            fp_schema.review_title = fp_model.review.title if fp_model.review else None
    
    return schema


@folder_router.post("/", response_model=schemas.FolderResponse)
async def create_folder(folder_in: schemas.FolderCreate = Body(..., example={"folder_name":"My folder",  "parent_folder_id": None}),
                        db:AsyncSession = Depends(get_db),
                        user: User = Depends(get_current_user)):
    return await repository.create_folder(db, user_id=user.id,
                                          folder_name=folder_in.folder_name,
                                          parent_folder_id=folder_in.parent_folder_id)
    

@folder_router.put("/{folder_id}", response_model=schemas.FolderResponse)
async def update_folder(folder_id: int,
                        folder_in: schemas.FolderUpdate,
                        db: AsyncSession = Depends(get_db),
                        user: User = Depends(get_current_user)):
    folder = await repository.get_folder_by_id(db, folder_id)
    if not folder or folder.user_id != user.id:
        raise HTTPException(status_code=404, detail="Folder not found")
    return await repository.update_folder(db, folder, folder_in.folder_name, folder_in.parent_folder_id)


@folder_router.delete("/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_folder(folder_id: int,
                        db: AsyncSession = Depends(get_db),
                        user: User = Depends(get_current_user)):
    folder = await repository.get_folder_by_id(db, folder_id)
    if not folder or folder.user_id != user.id:
        raise HTTPException(status_code=404, detail="Folder not found")
    await repository.delete_folder(db, folder_id)
    
    
@folder_router.post("/{folder_id}/items")
async def add_item_to_folder(folder_paper_name: str,
                             item: schemas.FolderPaperCreate,
                             db: AsyncSession = Depends(get_db),
                             user: User = Depends(get_current_user)):
    folder = await repository.get_folder_by_id(db, item.folder_id)
    if not folder or folder.user_id != user.id:
        raise HTTPException(status_code=404, detail="Folder not found")
    return await repository.create_folder_paper(db, folder_id=item.folder_id,
                                                folder_paper_name=folder_paper_name,
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
        raise HTTPException(status_code=403, detail="Forbidden")
    
    await repository.delete_folder_paper(db, folder_paper)
    return {"detail": "Deleted"}



@folder_router.get("/root/{folder_id}", response_model=schemas.FolderDetailResponse)
async def get_folder_detail(folder_id: int,
                            db: AsyncSession = Depends(get_db),
                            user: User = Depends(get_current_user)):
    result = await db.execute(
        select(Folder)
        .options(
            selectinload(Folder.subfolders).selectinload(Folder.subfolders),
            selectinload(Folder.folder_papers).selectinload(FolderPaper.paper),
            selectinload(Folder.folder_papers).selectinload(FolderPaper.review)
        )
        .where(Folder.id == folder_id)
    )
    folder = result.scalar_one_or_none()
    if not folder or folder.user_id != user.id:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    return enrich_folder_schema(folder)



@folder_router.get("/root", response_model=List[schemas.FolderDetailResponse])
async def get_root_folder(db: AsyncSession = Depends(get_db),
                          user: User = Depends(get_current_user)):
    result = await db.execute(
        select(Folder)
        .options(
            selectinload(Folder.subfolders).selectinload(Folder.subfolders),
            selectinload(Folder.folder_papers).selectinload(FolderPaper.paper),
            selectinload(Folder.folder_papers).selectinload(FolderPaper.review)
        ).where(Folder.user_id == user.id, Folder.parent_folder_id == None)
    )
    folders = result.scalars().all()
    if not folders:
        raise HTTPException(status_code=404, detail="Root folder not found")
    
    folder_schemas = []
    for folder in folders:
        
        folder_schemas.append(enrich_folder_schema(folder))
        
    return folder_schemas
    

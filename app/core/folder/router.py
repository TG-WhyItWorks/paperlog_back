from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.db.session import get_db
from app.core.user.models import User
from app.common.dependencies import get_current_user

from app.core.folder import schemas, repository
from app.core.folder.models import Folder, FolderPaper

folder_router = APIRouter()


@folder_router.post("/", response_model=schemas.FolderResponse)
async def create_folder(folder_in: schemas.FolderCreate,
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
async def add_item_to_folder(folder_id: int,
                             item: schemas.FolderPaperCreate,
                             db: AsyncSession = Depends(get_db),
                             user: User = Depends(get_current_user)):
    folder = await repository.get_folder_by_id(db, folder_id)
    if not folder or folder.user_id != user.id:
        raise HTTPException(status_code=404, detail="Folder not found")
    return await repository.create_folder_paper(db, folder_id=folder_id,
                                                paper_id=item.paper_id,
                                                review_id=item.review_id)
    

@folder_router.delete("/{folder_id}/items")
async def remove_item_from_folder(folder_id: int,
                                  item: schemas.FolderPaperDelete,
                                  db: AsyncSession = Depends(get_db),
                                  user: User = Depends(get_current_user)):
    folder = await repository.get_folder_by_id(db, folder_id)
    if not folder or folder.user_id != user.id:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    folder_paper = await repository.get_folder_paper(
        db, folder_id=folder_id,
        paper_id=item.paper_id,
        review_id=item.review_id
    )
    if not folder_paper:
        raise HTTPException(status_code=404, detail="Item not found in folder")
    
    await repository.delete_folder_paper(db, folder_paper)
    return {"detail": "Deleted"}


@folder_router.get("/{folder_id}", response_model=schemas.FolderDetailResponse)
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
    return folder
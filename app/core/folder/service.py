from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.folder import repository
from app.core.folder.models import Folder
from app.core.folder.schemas import FolderCreate, FolderUpdate
from app.core.user.models import User


async def create_folder(db: AsyncSession, folder_create: FolderCreate, user: User):
    return await repository.create_folder(
        db,user_id=user.id,
        folder_name=folder_create.folder_name,
        parent_folder_id=folder_create.parent_folder_id
    )
    

async def update_folder(
    db: AsyncSession,
    folder: Folder,
    folder_update: FolderUpdate
):
    return await repository.update_folder(
        db=db,
        folder=folder,
        new_name=folder_update.folder_name,
        parent_folder_id=folder_update.parent_folder_id
    )
    
    
async def delete_folder(db: AsyncSession, folder_id: int):
    folder = await repository.get_folder_by_id(db, folder_id)
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    await repository.delete_folder(db, folder_id)
    
async def add_paper_to_folder(db: AsyncSession, folder_id: int, paper_id: int):
    return await repository.create_folder_paper(db, folder_id=folder_id, paper_id=paper_id)

async def add_review_to_folder(db:AsyncSession, folder_id: int, review_id: int):
    return await repository.create_folder_paper(db, folder_id=folder_id, review_id=review_id)

async def remove_item_from_folder(db:AsyncSession, folder_id: int, paper_id: int = None, review_id: int = None):
    item = await repository.get_folder_paper(db, folder_id=folder_id, paper_id=paper_id, review_id=review_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found in folder")
    await repository.delete_folder_paper(db, item)
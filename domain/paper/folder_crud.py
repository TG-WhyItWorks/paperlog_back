# crud/folder.py
from sqlalchemy.ext.asyncio import AsyncSession
from models import Folder
from domain.paper.folder_schema import FolderCreate,FolderUpdate

async def create_folder(db: AsyncSession, folder_in: FolderCreate) -> Folder:
    folder = Folder(
        name=folder_in.name,
        user_id=folder_in.user_id,
        parent_id=folder_in.parent_id
    )
    db.add(folder)
    await db.commit()
    await db.refresh(folder)
    return folder

async def update_folder(db:AsyncSession,db_folder : Folder, folder_update : FolderUpdate):
	db_folder.name=folder_update.name
	db.add(db_folder)
	await db.flush()
	await db.commit()
	await db.refresh(db_folder)
	return db_folder

async def delete_folder(db:AsyncSession,db_folder:Folder):
    await db.delete(db_folder)
    await db.commit()
    
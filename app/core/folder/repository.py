from datetime import datetime, UTC
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.folder.models import Folder, FolderPaper


async def get_folder_by_id(db: AsyncSession, folder_id: int) -> Folder | None:
    result = await db.execute(
        select(Folder)
        .options(
            selectinload(Folder.subfolders),
            selectinload(Folder.folder_papers).selectinload(FolderPaper.paper),
            selectinload(Folder.folder_papers).selectinload(FolderPaper.review)
        )
        .where(Folder.id == folder_id)
    )
    return result.scalar_one_or_none()


async def create_folder(db: AsyncSession, user_id: int, folder_name: str, parent_folder_id: int | None = None):
    folder = Folder(
        folder_name=folder_name,
        user_id=user_id,
        parent_folder_id=parent_folder_id,
        created_at=datetime.now(UTC)
        )
    db.add(folder)
    await db.commit()
    await db.refresh(folder)
    return folder

async def update_folder(db: AsyncSession, folder: Folder, new_name: str, parent_folder_id: int | None):
    if new_name is not None:
        folder.folder_name = new_name
    folder.parent_folder_id = parent_folder_id
    folder.updated_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(folder)
    return folder

async def delete_folder(db: AsyncSession, folder_id: int):
    result = await db.execute(
        select(Folder)
        .options(
            selectinload(Folder.subfolders),
            selectinload(Folder.folder_papers)
        )
        .where(Folder.id == folder_id)
    )
    folder = result.scalar_one_or_none()
    
    if not folder:
        return
    
    # 재귀적으로 하위 폴더 제거
    subfolder_ids = [subfolder.id for subfolder in folder.subfolders]
    for subfolder_id in subfolder_ids:
        await delete_folder(db, subfolder_id)
    
    # 현재 폴더 FolderPaper 삭제
    for fp in folder.folder_papers:
        await db.delete(fp)
        
    # 현재 폴더 삭제
    await db.delete(folder)
    await db.commit()
    
    
async def create_folder_paper(db: AsyncSession, folder_id: int, paper_id: int = None, review_id: int = None):
    folder_paper = FolderPaper(folder_id=folder_id, paper_id=paper_id, review_id=review_id)
    db.add(folder_paper)
    await db.commit()
    await db.refresh(folder_paper)
    return folder_paper


async def get_folder_paper(db: AsyncSession, folder_id: int, paper_id: int = None, review_id: int = None):
    stmt = select(FolderPaper).where(FolderPaper.folder_id == folder_id)
    
    if paper_id:
        stmt = stmt.where(FolderPaper.paper_id == paper_id)
    if review_id:
        stmt = stmt.where(FolderPaper.review_id == review_id)
        
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def delete_folder_paper(db: AsyncSession, folder_paper: FolderPaper):
    await db.delete(folder_paper)
    await db.commit()
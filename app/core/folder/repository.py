from datetime import datetime, UTC
from fastapi import HTTPException
from sqlalchemy import and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.folder.models import Folder, FolderPaper


async def get_folder_by_id(db: AsyncSession, folder_id: int, user_id: int = None) -> Folder | None:
    # 폴더 조회 시 사용자 검증
    query = select(Folder).options(
        selectinload(Folder.subfolders),
        selectinload(Folder.folder_papers).selectinload(FolderPaper.paper),
        selectinload(Folder.folder_papers).selectinload(FolderPaper.review)
    ).where(Folder.id == folder_id)
    
    if user_id is not None:
        query = query.where(Folder.user_id == user_id)
    
    
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_folder(db: AsyncSession, user_id: int, folder_name: str, parent_folder_id: int | None = None):
    # parent_folder_id 있으면 해당 폴더가 같은 사용자의 폴더인지 확인
    if parent_folder_id:
        parent_check = await db.execute(
            select(Folder.id).where(
                and_(Folder.id == parent_folder_id, Folder.user_id == user_id)
            )
        )
        if not parent_check.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="parent folder not found or access denied")
    
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

async def update_folder(db: AsyncSession, folder: Folder, new_name: str, parent_folder_id: int | None, user_id: int):
    # parent_folder_id가 변경되는 경우 새 부모 폴더의 소유권 확인
    if parent_folder_id and parent_folder_id != folder.parent_folder_id:
        parent_check = await db.execute(
            select(Folder.id).where(
                and_(Folder.id == parent_folder_id, Folder.user_id == user_id)
            )
        )
        if not parent_check.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Parent folder not found or access denied")
        
    if new_name is not None:
        folder.folder_name = new_name
    folder.parent_folder_id = parent_folder_id
    folder.updated_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(folder)
    return folder

async def delete_folder(db: AsyncSession, folder_id: int, user_id: int):
    # 사용자 소유권 확인
    result = await db.execute(
        select(Folder)
        .options(
            selectinload(Folder.subfolders),
            selectinload(Folder.folder_papers)
        )
        .where(and_(Folder.id == folder_id, Folder.user_id == user_id))
    )
    folder = result.scalar_one_or_none()
    
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found or access denied")
    
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
    
    
async def create_folder_paper(db: AsyncSession, folder_id: int, folder_paper_name: str, user_id: int, paper_id: int = None, review_id: int = None):
    # 폴더 소유권 확인
    folder_check = await db.execute(
        select(Folder.id).where(
            and_(Folder.id == folder_id, Folder.user_id == user_id)
        )
    )
    if not folder_check.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Folder not found or access denied")
    
    # 중복 검사
    stmt = select(FolderPaper).where(
        and_(
            FolderPaper.folder_id == folder_id,
            or_(
                FolderPaper.paper_id == paper_id if paper_id is not None else False,
                FolderPaper.review_id == review_id if review_id is not None else False
            )
        )
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(status_code=400, detail="Duplicate paper or review in this folder.")
    
    folder_paper = FolderPaper(folder_paper_name = folder_paper_name, folder_id=folder_id, paper_id=paper_id, review_id=review_id)
    db.add(folder_paper)
    await db.commit()
    await db.refresh(folder_paper)
    return folder_paper


async def get_folder_paper_by_id(db: AsyncSession, folder_paper_id: int) -> FolderPaper | None:
   result = await db.execute(
       select(FolderPaper)
       .options(
           selectinload(FolderPaper.folder)
       ).where(FolderPaper.id == folder_paper_id)
   )
   return result.scalar_one_or_none()


async def delete_folder_paper(db: AsyncSession, folder_paper: FolderPaper):
    await db.delete(folder_paper)
    await db.commit()
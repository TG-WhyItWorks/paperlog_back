from datetime import datetime, UTC
from fastapi import HTTPException
from sqlalchemy import and_, or_, text
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

async def update_folder(db: AsyncSession, folder: Folder, new_name: str | None, parent_folder_id: int | None, user_id: int):
    
    # 부모폴더 바뀔 때
    if parent_folder_id is not None and parent_folder_id != folder.parent_folder_id:
        # 새 부모 폴더의 소유권 확인
        parent_check = await db.execute(
            select(Folder.id).where(
                and_(Folder.id == parent_folder_id, Folder.user_id == user_id)
            )
        )
        if not parent_check.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Parent folder not found or access denied")
        folder.parent_folder_id = parent_folder_id
   
    # 이름만 변경하는 경우엔 parent_folder_id 유지
    if new_name is not None:
        folder.folder_name = new_name    
        
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
         await delete_folder(db, subfolder_id, user_id)
    
    # 현재 폴더 FolderPaper 삭제
    for fp in folder.folder_papers:
        await db.delete(fp)
        
    # 현재 폴더 삭제
    await db.delete(folder)
    await db.commit()
    
async def get_folder_paper(
    db: AsyncSession,
    folder_id: int,
    paper_id: int | None = None,
    review_id: int | None = None,
    paper_arxiv_id: str | None = None,
) -> FolderPaper | None:
    if paper_id is None and review_id is None and paper_arxiv_id is None:
        return None
    stmt = select(FolderPaper).where(FolderPaper.folder_id == folder_id)
    conds = []
    if paper_id is not None:
        conds.append(FolderPaper.paper_id == paper_id)
    if review_id is not None:
        conds.append(FolderPaper.review_id == review_id)
    if paper_arxiv_id is not None:
        # Paper 클래스를 관계에서 동적으로 획득 → 별도 import 불필요
        paper_cls = FolderPaper.paper.property.mapper.class_
        stmt = stmt.join(paper_cls)  # .join(FolderPaper.paper)와 동일 효과
        conds.append(paper_cls.arxiv_id == paper_arxiv_id)
    stmt = stmt.where(or_(*conds))
    res = await db.execute(stmt)
    return res.scalar_one_or_none()
    
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
    
    

async def get_all_folder_ids(db: AsyncSession, user_id: int, root_folder_ids:list[int] = None) -> list[int]:
    # 사용자의 모든 하위 폴더 ID를 재귀적으로 조회
    
    if root_folder_ids is None:
         root_result = await db.execute(
             select(Folder.id).where(
                 and_(Folder.user_id == user_id, Folder.parent_folder_id == None)
            )
        )
   
    root_folder_ids = [row[0] for row in root_result.fetchall()]
    
    if not root_folder_ids:
        return []
    
    # 사용자 검증을 포함한 CTE 쿼리 -> CTE(Common Table Expression)
    placeholders = ", ".join(f":id{i}" for i in range(len(root_folder_ids)))
    params = {f"id{i}": fid for i, fid in enumerate(root_folder_ids)}
    params["user_id"] = user_id
    
    cte_query = text(f"""
                     WITH RECURSIVE folder_tree AS (
                         -- Base case: 시작 폴더들(사용자 소유권 확인)
                         SELECT id, parent_folder_id, user_id, 0 as depth
                         FROM folders
                         WHERE id IN ({placeholders}) AND user_id = :user_id
                         
                         UNION ALL
                         
                         -- Recursive case: 하위 폴더들 (사용자 소유권 유지)
                         SELECT f.id, f.parent_folder_id, f.user_id, ft.depth + 1
                         FROM folders f
                         INNER JOIN folder_tree ft ON f.parent_folder_id = ft.id
                         WHERE f.user_id = :user_id AND ft.depth < 100
                     )
                     SELECT id FROM folder_tree
                     ORDER BY depth, id
                """)

    result = await db.execute(cte_query, params)
    return [row[0] for row in result.fetchall()]

async def get_folders_with_all_data(db: AsyncSession, folder_ids: list[int]) -> list[Folder]:
    # 주어진 폴더 ID들의 모든 데이터 조회(관계 포함)
    if not folder_ids:
        return []
    
    result = await db.execute(
        select(Folder)
        .options(
            selectinload(Folder.subfolders),
            selectinload(Folder.folder_papers).selectinload(FolderPaper.paper),
            selectinload(Folder.folder_papers).selectinload(FolderPaper.review)
        )
        .where(Folder.id.in_(folder_ids))
        .order_by(Folder.id)
    )
    return result.scalars().all()

"""
# subfolder가 2개씩 생성, 삭제되는 문제가 직렬화 과정에서 계층 구조가 중복되어 생성되기 때문이라 판단. 계층구조는 Folder.subfolders의 relationship으로 구하고, build_folder_hierarchy를 사용하진 않겠음.

def build_folder_hierarchy(folders: list[Folder]) -> list[Folder]:
    # 플랫한 폴더 리스트를 계층 구조로 변환
    folder_dict = {folder.id: folder for folder in folders}
    root_folders = []
    
        
    # 계층 구조 구성
    for folder in folders:
        if folder.parent_folder_id is None:
            root_folders.append(folder)
        elif folder.parent_folder_id in folder_dict:
            parent = folder_dict[folder.parent_folder_id]
            parent.subfolders.append(folder)
    
    return root_folders

"""

async def get_folder_by_id_with_unlimited_tree(db: AsyncSession, folder_id: int, user_id: int = None ):
    # 특정 폴더와 모든 하위 폴더를 제한 없이 조회
    
    
    # 폴더 소유권 확인
    folder_check = await db.execute(
        select(Folder).where(
            and_(Folder.id == folder_id) if user_id is None
            else and_(Folder.id == folder_id, Folder.user_id == user_id)
        )
    )
    root_folder = folder_check.scalar_one_or_none()
    if not root_folder:
        return None
    
    # 모든 하위 폴더 ID 조회
    all_folder_ids = await get_all_folder_ids(db, user_id, [folder_id])
    
    # 모든 폴더 데이터 조회
    all_folders = await get_folders_with_all_data(db, all_folder_ids)
    
    return next((f for f in all_folders if f.id == folder_id), None)


async def get_root_folders_with_unlimited_tree(db: AsyncSession, user_id: int) -> list[Folder]:
    # 사용자의 모든 루트 폴더와 하위 폴더를 제한 없이 조회
    
    # 루트폴더부터 모든 하위 폴더 ID 조회
    all_folder_ids = await get_all_folder_ids(db, user_id)
    
    if not all_folder_ids:
        return []
    
    # 모든 폴더 데이터 조회
    all_folders = await get_folders_with_all_data(db, all_folder_ids)
    
    # 계층 구조 구성
    return [f for f in all_folders if f.parent_folder_id is None]
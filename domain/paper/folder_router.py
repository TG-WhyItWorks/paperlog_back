# routers/folder.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from domain.paper.folder_schema import FolderCreate,FolderResponse
from database import get_db
from domain.paper.folder_crud  import create_folder

router = APIRouter(prefix="/folders", tags=["Folders"])

@router.post("/", response_model=FolderResponse)
async def create_folder_endpoint(
    folder_in: FolderCreate,
    db: AsyncSession = Depends(get_db)
):
    return await create_folder(db, folder_in)

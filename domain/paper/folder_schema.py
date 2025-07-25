from pydantic import BaseModel,ConfigDict
from typing import Optional, List
from datetime import datetime

class FolderBase(BaseModel):
    name: str
    parent_id: Optional[int] = None



class FolderCreate(FolderBase):
    name:str
    user_id:int
    parent_id:Optional[int] = None

class Folder(BaseModel):
    id: int
    name:str
    user_id : int
    parent_id:Optional[int]

class FolderUpdate(FolderCreate):
    folder_id: int

class FolderResponse(FolderBase):
    id: int
    name:str
    user_id : int
    parent_id:Optional[int]
    
    model_config=ConfigDict(from_attributes=True)
    




# 기본적으로 사용할 Paper 요약 스키마
class PaperInFolder(BaseModel):
    id: int
    title: str
    author: str

    model_config=ConfigDict(from_attributes=True)


# 기본적으로 사용할 Folder 요약 스키마
class FolderSummary(BaseModel):
    id: int
    name: str
    parent_id: Optional[int]

    model_config=ConfigDict(from_attributes=True)

    
class SubfolderCreate(BaseModel):
    name: str 
    parent_id: int 
    user_id:int
    
class AddPaperToFolder(BaseModel):
    paper_id: int
    folder_id: int

# ✅ 4. 폴더 삭제 요청
class FolderDelete(BaseModel):
    folder_id: int


# ✅ 5. 폴더 상세 정보 조회 응답 (폴더 안의 하위 폴더, 페이퍼 포함)
class FolderDetail(BaseModel):
    id: int
    name: str
    parent_id: Optional[int]
    subfolders: List[FolderSummary] = []
    papers: List[PaperInFolder] = []

    model_config=ConfigDict(from_attributes=True)
    

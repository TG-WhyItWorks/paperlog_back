from __future__ import annotations
from pydantic import BaseModel, Field, model_validator
from typing import Optional, List
from datetime import datetime



class FolderBase(BaseModel):
    folder_name: str
    parent_folder_id: Optional[int] = Field(default=None, nullable=True)
    
    
class FolderCreate(FolderBase):
    pass
    
class FolderUpdate(BaseModel):
    id: int
    folder_name: str
    parent_folder_id: Optional[int] = Field(default=None)
    
class FolderDelete(BaseModel):
    id: int


class FolderResponse(FolderBase):
    id: int
    created_at: datetime
    user_id: int
    
    class Config:
        from_attributes = True



# 폴더에 논문/블로그 추가 요청용
class FolderPaperCreate(BaseModel):
    folder_paper_name: str
    folder_id: int
    paper_id: Optional[int] = None
    review_id: Optional[int] = None
    
    @model_validator(mode='after')
    def validate(cls, values):
        paper_id, review_id = values.paper_id, values.review_id
        if not paper_id and not review_id:
            raise ValueError("paper_id 또는 review_id 중 하나는 필요합니다.")
        return values
    
    
class FolderPaperDelete(BaseModel):
    folder_id: int
    paper_id: Optional[int] = None
    review_id: Optional[int] = None
    
    
    
class FolderPaperResponse(BaseModel):
    folder_paper_name: str
    id: int
    folder_id: int
    paper_arxiv_id: Optional[str] = None
    review_id: Optional[int] = None
    paper_title: Optional[str] = None
    review_title: Optional[str] = None
    
    class Config:
        from_attributes = True
        


class FolderDetailResponse(FolderResponse):
    subfolders: List["FolderDetailResponse"] = []
    folder_papers: List[FolderPaperResponse] = []
    
    class Config:
        from_attributes = True
        

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
    paper_arxiv_id: Optional[str] = None

    @model_validator(mode='after')
    def validate_one_of(cls, values):
        if not (values.paper_id or values.review_id or values.paper_arxiv_id):
            raise ValueError("paper_id, review_id 또는 paper_arxiv_id 중 하나는 필요합니다.")
        return values
    


class PaperResponse(BaseModel):
    id: int # arxiv_id
    title: str
    class Config:
        from_attributes = True
        
class ReviewResponse(BaseModel):
    id: int
    title: str
    class Config:
        from_attributes = True

    
class FolderPaperResponse(BaseModel):
    id: int
    folder_paper_name: str
    folder_id: int
    paper: Optional[PaperResponse] = None
    review: Optional[ReviewResponse] = None
    
    class Config:
        from_attributes = True
        


class FolderDetailResponse(FolderResponse):
    subfolders: List["FolderDetailResponse"] = []
    folder_papers: List[FolderPaperResponse] = []
    
    # depth 무제한 지원을 위한 재귀 직렬화 메서드(lazyload 무제한 -> MissingGreenlet 오류 해결)
    @classmethod
    def from_orm_recursive(cls, folder: "Folder"):
        return cls(
            id=folder.id,
            folder_name=folder.folder_name,
            user_id= folder.user_id,
            parent_folder_id=folder.parent_folder_id,
            created_at=folder.created_at,
            folder_papers=[
                FolderPaperResponse.model_validate(fp) for fp in folder.folder_papers
                ] if folder.folder_papers else [],
            subfolders=[
                cls.from_orm_recursive(sf) for sf in getattr(folder, "subfolders", [])
                ]
        )
    
    class Config:
        from_attributes = True
        
FolderDetailResponse.model_rebuild()
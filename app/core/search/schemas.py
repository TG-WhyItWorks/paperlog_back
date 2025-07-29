from pydantic import BaseModel, HttpUrl, field_validator
from datetime import datetime
from typing import List, Optional
from app.core.blog.schemas import ReviewOutSimple

class PaperCreate(BaseModel):
    arxiv_id: str
    title: str
    summary: str
    authors: List[str]
    published: datetime
    publish_updated: Optional[datetime] = None
    doi: Optional[str] = None
    categories: Optional[List[str]] = None
    link: Optional[HttpUrl] = None

class ArxivSearchRequest(BaseModel):
    query: str
    page: int = 0
    page_size: int = 10
    sort_by: str = "relevance"# relevance, LastUpdatedDate, submittedDate 중 택 1
    

class PaperOut(PaperCreate):
    id :int
    updated_at: datetime
    created_at: datetime
    
    reviews: List[ReviewOutSimple] = [] # review 간략화 리스트
    
    # authors와 categories를 str -> list
    @field_validator('authors', mode="before")
    @classmethod
    def parse_authors(cls, v):
        if isinstance(v, str):
            return [a.strip() for a in v.split(",")]
        return v
    
    
    @field_validator('categories', mode="before")
    @classmethod
    def parse_categories(cls, v):
        if isinstance(v, str):
            return [c.strip() for c in v.split(",")]
        return v
    
    class Config:
        from_attributes = True
        

class PaperUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    authors: Optional[List[str]] = None
    published: Optional[datetime] = None
    publish_updated: Optional[datetime] = None
    doi: Optional[str] = None
    categories: Optional[List[str]] = None
    link: Optional[HttpUrl] = None
    comment: Optional[str] = None
    arxiv_id: Optional[str] = None
from pydantic import BaseModel,ConfigDict
from typing import Optional
from datetime import datetime, date

class PaperBase(BaseModel):
    title: str
    authors: Optional[str] = None
    doi: Optional[str] = None
    published_at: Optional[date] = None
    abstract: Optional[str] = None
    source_url: Optional[str] = None

class PaperCreate(PaperBase):
    pass

class PaperResponse(PaperBase):
    id: int
    created_at: datetime

    model_config=ConfigDict(from_attributes=True)
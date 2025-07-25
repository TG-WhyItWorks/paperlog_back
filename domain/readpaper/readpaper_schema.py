import datetime

from pydantic import BaseModel,field_validator,ConfigDict
from domain.comment.comment_schema import Comment
from domain.user.user_schema import User
from fastapi import Form, File, UploadFile
from typing import Optional


class ReadPaper(BaseModel):
    
    user_id:int
    paper_id:int
    rating:Optional[int]=None
    memo:Optional[str] =None
    read_at:datetime.datetime
    create_date:datetime.datetime

class ReadPaperCreate(BaseModel):
    
    rating:Optional[int]=None
    memo:Optional[str] =None
    
    
class ReadPaperUpdate(ReadPaperCreate):
    
    ReadPaperid : int 
    
    
class ReadPaperDelete(BaseModel):
    
    ReadPaperid : int 
    
    
    
    
    
    
    
import datetime

from pydantic import BaseModel,field_validator,ConfigDict
from app.core.user.schemas import User
from fastapi import Form, File, UploadFile
from typing import Optional, List
from app.core.comment.schemas import Comment



class ReviewImageRead(BaseModel):
    id: int
    image_path: str
    upload_date: datetime.datetime

    model_config=ConfigDict(from_attributes=True)



class Review(BaseModel):
    id:int
    title:str
    content:str
    create_date:datetime.datetime
    comment:list[Comment]=[]
    user:User|None    
    modify_date: datetime.datetime | None = None
    paper_id: Optional[int]
    images:List[ReviewImageRead]
    
    model_config=ConfigDict(from_attributes=True)
        
        
class ReviewCreate(BaseModel): 
    title:str
    content:str
    paper_id:Optional[int] =None
    
    @field_validator('title', 'content')
    def not_empty(cls,v):
        if not v or not v.strip():
            raise ValueError('빈 값은 허용하지 않습니다')
        return v

class ReviewList(BaseModel):
    total : int =0
    review_list: list[Review]=[]
    
    
class ReviewUpdate(ReviewCreate):
    review_id:int
    
    

class ReviewDelete(BaseModel):
    review_id:int













def get_review_form(
    title: str = Form(...),
    content: str = Form(...),
    image: Optional[UploadFile] = File(None)
):
    return {
        "title": title,
        "content": content,
        "image": image
    }
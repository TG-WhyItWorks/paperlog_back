from datetime import datetime

from pydantic import BaseModel,field_validator,ConfigDict
from app.core.user.schemas import User
from fastapi import Form, File, UploadFile
from typing import Optional, List
from app.core.comment.schemas import Comment



class ReviewImageRead(BaseModel):
    id: int
    image_path: str
    upload_date: datetime

    model_config=ConfigDict(from_attributes=True)



class Review(BaseModel):
    id:int
    title:str
    content:str
    create_date:datetime
    comment:list[Comment] = []
    user:User|None    
    modify_date: Optional[datetime] | None = None
    paper_id: Optional[int]
    images:List[ReviewImageRead] = []
    
    model_config=ConfigDict(from_attributes=True)
       



   
class ReviewCreate(BaseModel): 
    title:str
    content:str
    paper_id:Optional[int] =None
    vote_count:int =0
    
    


class ReviewList(BaseModel):
    total : int =0
    review_list: list[Review]=[]
    
    
class ReviewUpdate(ReviewCreate):
    review_id:int
    
    

class ReviewDelete(BaseModel):
    review_id:int


class ReviewVote(BaseModel):
    review_id: int
    
    
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
    
    
    
"""아래는 논문과 리뷰 연결에 필요한 코드"""

class ReviewOutSimple(BaseModel):# 논문 상세정보와 함께 뜰 연관 리뷰 요약 리스트
    id: int
    title: str
    content: str
    modify_date: Optional[datetime]
    user: Optional[User]
    vote_count:int
    model_config = ConfigDict(from_attributes=True)


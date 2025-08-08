from pydantic import BaseModel ,EmailStr,ConfigDict
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    username:str
    password:str
    password_chk:str
    email:EmailStr
    phonenumber:str


    

class User(BaseModel):
    id:int
    username:str
    email:str
    phonenumber:str
    
    




class Token(BaseModel):
    access_token:str
    token_type:str
    username:str
    user_id:int
    

class UserProfile(BaseModel):
    username:str
    email:str
    nickname:Optional[str] = None
    phonenumber:Optional[str] = None
    bio: Optional[str] = None  
    intro: Optional[str] = None
    model_config=ConfigDict(from_attributes=True)

class UserRead(BaseModel):
    username: str
    email: EmailStr
    nickname:str
    model_config=ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    nickname:str
    phonenumber:str
    bio:str
    intro:str
    

class FolderRead(BaseModel):
    id: int
    folder_name: str
    parent_folder_id: Optional[int] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
    

class UserWithFolders(UserRead):
    folders: list[FolderRead] = []
from pydantic import BaseModel, field_validator, EmailStr,ConfigDict
from pydantic_core.core_schema import FieldValidationInfo

class UserCreate(BaseModel):
    username:str
    password:str
    password_chk:str
    email:EmailStr
    phonenumber:str


    
    ''''
    @field_validator('username', 'password', 'password_chk', 'email','phonenumber')
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('빈 값은 허용되지 않습니다.')
        return v

    @field_validator('password_chk')
    def passwords_match(cls, v, info: FieldValidationInfo):
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('비밀번호가 일치하지 않습니다')
        return v

    '''


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
    



class UserRead(BaseModel):
    username: str
    email: EmailStr

    model_config=ConfigDict(from_attributes=True)





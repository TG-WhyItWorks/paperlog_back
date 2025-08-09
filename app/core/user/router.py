

from datetime import timedelta
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse  # <- dict 반환으로도 충분, 남겨둠
from dotenv import load_dotenv
import os

from app.common.dependencies import get_db, get_current_user  # get_current_user 내부 oauth2_scheme 일관성 확인!
from app.core.user import service, schemas
from app.core.user.service import pwd_context, update_user
from app.common.security import create_access_token  # 내부에서 SECRET/ALGO 사용 일관화 권장

load_dotenv()

# 토큰 URL은 상대경로로: 라우터 prefix 변경에도 안전
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

user_router = APIRouter()  # 포함 시 prefix="/api/user"로 마운트한다고 가정


@user_router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=None)
async def user_create(
    _user_create: schemas.UserCreate,
    db: AsyncSession = Depends(get_db),
):
    user = await service.get_existing_user(db, user_create=_user_create)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 존재하는 사용자입니다.",
        )
    await service.create_user(db=db, user_create=_user_create)
    # 생성 후 바디 없이 201 반환 (필요하면 최소 필드 반환으로 바꿔도 됨)
    return


@user_router.post("/login")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    # OAuth2PasswordRequestForm.username 자리에 email을 받는 전략 유지
    user = await service.get_user_by_email(db, form_data.username)
    if not user or not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

   
    access_token = create_access_token(user_id=user.id, email=user.email)

    # response_model에 맞추어 dict(또는 schemas.Token) 그대로 리턴
    return {
        "access_token": access_token,
        "token_type": "bearer",
        
            "id": user.id,
            "email": user.email,
            "username": user.username,
        
    }


@user_router.put("/update", response_model=schemas.UserProfile)
async def user_update(
    _user_update: schemas.UserUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    updated = await update_user(db, user, _user_update)
    # 업데이트 후 현재 프로필 형태로 반환 (프론트 반영 편의)
    return schemas.UserProfile(
        username=updated.username,
        email=updated.email,
        nickname=updated.nickname,
        phonenumber=updated.phonenumber,
    )


@user_router.get("/myprofile", response_model=schemas.UserProfile)
async def user_profile(current_user=Depends(get_current_user)):
    return schemas.UserProfile(
        username=current_user.username,
        email=current_user.email,
        nickname=current_user.nickname,
        phonenumber=current_user.phonenumber,
    )



'''
from datetime import timedelta, datetime
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from starlette import status
from app.core.user.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from app.common.dependencies import get_db ,get_current_user
from app.core.user import service, schemas
from app.core.user.service import pwd_context,get_user_by_email,update_user
from datetime import datetime, UTC
import os
from dotenv import load_dotenv
from app.common.security import create_access_token
from fastapi.responses import JSONResponse



load_dotenv() 
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login")


if not SECRET_KEY:
    raise RuntimeError("Environment variable JWT_SECRET_KEY is not set.")


user_router = APIRouter()

@user_router.post("/signup", status_code=status.HTTP_204_NO_CONTENT)
async def user_create(
    _user_create: schemas.UserCreate,
    db: AsyncSession = Depends(get_db)
):
    user = await service.get_existing_user(db, user_create=_user_create)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 존재하는 사용자입니다."
        )
    await service.create_user(db=db, user_create=_user_create)


@user_router.post("/login", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    user = await service.get_user_by_email(db, form_data.username)#username필드에 user의 email이 있어야 한다.
    if not user or not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    email=user.email
    name=user.username
    access_token = create_access_token(user_id=user.id, email=user.email)
    

    return JSONResponse({
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id":user.id,
            "email": email,
            "username": name,
            
        }
    })


@user_router.put("/update",status_code=200)
async def user_update(
    _user_update:schemas.UserUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    await update_user(db,user,_user_update)
    return {"message":"수정 성공"}
    
    

@user_router.get("/myprofile")
async def user_profile(current_user:User=Depends(get_current_user)):
     return schemas.UserProfile(
        username=current_user.username,
        email=current_user.email,
        nickname=current_user.nickname,
        phonenumber=current_user.phonenumber
    )

'''
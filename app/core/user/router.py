from datetime import timedelta, datetime
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from starlette import status
from app.core.user.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from app.common.dependencies import get_db  
from app.core.user import service, schemas
from app.core.user.service import pwd_context,get_user_by_email
from datetime import datetime, UTC
import os

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login")



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

    data = {
        "sub": str(user.id),
        "email":user.email,
        "exp": datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                
    }
    access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        "user_id":user.id
    }

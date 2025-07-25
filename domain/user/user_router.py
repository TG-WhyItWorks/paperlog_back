from datetime import timedelta, datetime
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from starlette import status
from models import User
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db  
from domain.user import user_crud, user_schema
from domain.user.user_crud import pwd_context,get_user_by_email
from datetime import datetime, UTC
import os

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login")

router = APIRouter(prefix="/api/user",tags=["User"])


@router.post("/signup", status_code=status.HTTP_204_NO_CONTENT)
async def user_create(
    _user_create: user_schema.UserCreate,
    db: AsyncSession = Depends(get_db)
):
    user = await user_crud.get_existing_user(db, user_create=_user_create)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 존재하는 사용자입니다."
        )
    await user_crud.create_user(db=db, user_create=_user_create)


@router.post("/login", response_model=user_schema.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    user = await user_crud.get_user_by_email(db, form_data.username)#username필드에 user의 email이 있어야 한다.
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




async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="유효하지 않은 인증입니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await get_user_by_email(session, email=email)
    if user is None:
        raise credentials_exception

    return user

async def get_current_username(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await user_crud.get_user(db, username=username)
    if user is None:
        raise credentials_exception
    return user


@router.get("/me",response_model=user_schema.UserRead)
async def read_current_user(user: User = Depends(get_current_username)):
    return {
        "email": user.email,
        "username": user.username
    }


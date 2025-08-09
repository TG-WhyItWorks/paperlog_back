from app.db.session import SessionLocal
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from typing import Optional
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.user.service import get_user_by_email,get_user_by_userId
from app.core.user.models import User
import os
from dotenv import load_dotenv

load_dotenv() 
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24



        

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"





async def get_db():#비동기 방식임(get_async_session)
    async with SessionLocal() as session:
        yield session
        






oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login", auto_error=False)#JWT 토큰 없으면 None 반환
async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="유효하지 않은 인증입니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if token is None:
        raise credentials_exception

    try:
        # 1) 토큰 디코딩
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # 2) 필수 클레임 꺼내기
        user_id = payload.get("sub")
        email_in_token = payload.get("email")

        # 3) 클레임 유효성 검사
        if user_id is None or email_in_token is None:
            raise credentials_exception

        # 4) DB에서 유저 조회
        user = await get_user_by_userId(session, user_id=int(user_id))
        if user is None:
            raise credentials_exception

        # 5) (선택) 토큰의 이메일과 DB 이메일이 동일한지 검증
        if user.email != email_in_token:
            raise credentials_exception

    except JWTError:
        # 서명 오류, 만료 등 모든 JWT 오류는 여기로
        raise credentials_exception

    return user
        


        
async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db),
) -> Optional[User]:
    
    if not token:
        return None
    
    try:
        # 1) 토큰 디코딩
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # 2) 필수 클레임 꺼내기
        user_id = payload.get("sub")
        email_in_token = payload.get("email")

        # 3) 클레임 유효성 검사
        if user_id is None or email_in_token is None:
            raise None

        # db에 유저 있는지와 이메일 확인
        user = await get_user_by_userId(session, user_id=int(user_id))
        if not user or user.email != email_in_token:
            raise None

    except JWTError:
        # 서명 오류, 만료 등 모든 JWT 오류는 여기로
        raise None

    return user
        


        
        
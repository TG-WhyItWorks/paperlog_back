from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from starlette.config import Config
from sqlalchemy.ext.asyncio import AsyncSession
from app.common.dependencies import get_db
from .oauth import oauth
from app.common.security import create_access_token
from app.core.user import schemas,service


auth_router=APIRouter()
@auth_router.get('/google')
async def google_login(request: Request):
    redirect_uri = request.url_for('google_auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@auth_router.get('/google/callback', name="google_auth")
async def google_auth(request: Request, session: AsyncSession = Depends(get_db)):
    token = await oauth.google.authorize_access_token(request)

    id_token = token.get("id_token")
    if not id_token:
        raise HTTPException(status_code=400, detail="id_token not found")

    user_info = token.get("userinfo") or await oauth.google.parse_id_token(request, token)
    email = user_info.get("email")
    name = user_info.get("name")
    
    if not email:
        raise HTTPException(status_code=400, detail="No email provided by Google")

    # DB 사용자 확인 및 없으면 생성
    user = await service.get_or_create_google_user(session, email=email, username=name)

    # JWT 생성
   from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from starlette.config import Config
from sqlalchemy.ext.asyncio import AsyncSession
from app.common.dependencies import get_db
from .oauth import oauth
from app.common.security import create_access_token
from app.core.user import schemas,service


auth_router=APIRouter()
@auth_router.get('/google')
async def google_login(request: Request):
    redirect_uri = request.url_for('google_auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@auth_router.get('/google/callback', name="google_auth")
async def google_auth(request: Request, session: AsyncSession = Depends(get_db)):
    token = await oauth.google.authorize_access_token(request)

    id_token = token.get("id_token")
    if not id_token:
        raise HTTPException(status_code=400, detail="id_token not found")

    user_info = token.get("userinfo") or await oauth.google.parse_id_token(request, token)
    email = user_info.get("email")
    name = user_info.get("name")
    
    if not email:
        raise HTTPException(status_code=400, detail="No email provided by Google")

    # DB 사용자 확인 및 없으면 생성
    user = await service.get_or_create_google_user(session, email=email, username=name)

    # JWT 생성
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


    return JSONResponse({
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id":user.id,
            "email": email,
            "username": name,
            
        }
    })

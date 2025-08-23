import httpx
from fastapi import APIRouter, Request, Depends, HTTPException,Body
from fastapi.responses import RedirectResponse, JSONResponse
from starlette.config import Config
from sqlalchemy.ext.asyncio import AsyncSession
from app.common.dependencies import get_db
from .oauth import oauth
from app.common.security import create_access_token, create_refresh_token, decode_token
from app.core.user import schemas,service
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as grequests
from dotenv import load_dotenv
import os
from urllib.parse import unquote, quote
from datetime import datetime ,UTC,timezone

def enc(v):  # URL-encode (한글/공백 등 안전)
    return quote(str(v or ""), safe="")


load_dotenv() 
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
auth_router=APIRouter()
@auth_router.get('/google')
async def google_login(request: Request):
    redirect_uri = request.url_for('google_auth')
    app_redirect = request.query_params.get("redirect")
    if app_redirect:
        request.session["post_auth_redirect"] = app_redirect
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
    refresh_token = create_refresh_token(user_id=user.id, email=user.email)
    print("[callback] token keys:", list(token.keys()))
    print("[callback] session keys:", list(request.session.keys()))
    print("[callback] post_auth_redirect:", request.session.get("post_auth_redirect"))
   
    app_redirect = request.session.pop("post_auth_redirect", None)
    if app_redirect:
        app_redirect = unquote(app_redirect) 
        sep = '&' if '?' in app_redirect else '?'  
        url = (
        f"{app_redirect}{sep}"
        f"access_token={enc(access_token)}"
        f"&refresh_token={enc(refresh_token)}"
        f"&token_type={enc('bearer')}"
        f"&user_id={enc(user.id)}"
        f"&email={enc(user.email)}"
        f"&username={enc(user.username)}"
        )
        print("[callback] building redirect to:", url)
        return RedirectResponse(url)

    
    return JSONResponse({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": email,
            "username": name,
            
        }
    })
    
    
_ALLOWED_CLIENT_IDS = {"1045626017141-53ouu1tf82895ckrq7tsk4qkj6730f42.apps.googleusercontent.com"} 
def _verify_id_token_debug(idt: str):
    try:
        claims = google_id_token.verify_oauth2_token(
            idt, grequests.Request(), audience=None  # <- 여러 client_id 허용
        )
        now = int(datetime.now(timezone.utc).timestamp())
        print("[google] iss =", claims.get("iss"))
        print("[google] aud =", claims.get("aud"))
        print("[google] email =", claims.get("email"))
        print("[google] email_verified =", claims.get("email_verified"))
        print("[google] iat =", claims.get("iat"), "exp =", claims.get("exp"), "now =", now)
        print("여기서 확인해보기")

        if claims.get("iss") not in ("https://accounts.google.com", "accounts.google.com"):
            raise HTTPException(401, "Invalid issuer")

        if claims.get("aud") not in _ALLOWED_CLIENT_IDS:
            raise HTTPException(401, "Invalid audience")

        if not claims.get("email"):
            raise HTTPException(401, "No email in id_token")

        if not claims.get("email_verified", False):
            raise HTTPException(401, "Email not verified")

        if claims.get("exp") and claims["exp"] < now:
            raise HTTPException(401, "Token expired")

        return claims

    except HTTPException:
        raise
    except Exception as e:
        import traceback; traceback.print_exc()
        print("[google] verify_oauth2_token error:", e)  # <-- 실제 이유
        raise HTTPException(401, "Invalid Google token")


def _now_ts() -> int:
    return int(datetime.now(timezone.utc).timestamp())

@auth_router.post("/google")
async def google_login_mobile(payload: dict = Body(...), db: AsyncSession = Depends(get_db)):
    print("[/auth/google] payload keys:", list(payload.keys()))
    idt = payload.get("id_token") or payload.get("idToken")
    act = payload.get("access_token") or payload.get("accessToken")

    # 안정성: 허용 client_id가 비어있으면 경고(배포 전에 반드시 채워야 함)
    if not _ALLOWED_CLIENT_IDS:
        print("[/auth/google][WARN] _ALLOWED_CLIENT_IDS is EMPTY. Check env GOOGLE_CLIENT_IDS/GOOGLE_CLIENT_ID.")

    try:
        email = name = sub = None

        # ---------- 1) id_token 경로 ----------
        if idt:
            try:
                # audience=None으로 구글 서명/만료/iss 검증 → aud는 아래에서 수동 체크
                claims = google_id_token.verify_oauth2_token(
                    idt,
                    grequests.Request(),
                    audience=None,
                )
            except Exception as e:
                print("[/auth/google][id_token] verify_oauth2_token error:", e)
                raise HTTPException(status_code=401, detail="Invalid Google token")

            iss = claims.get("iss")
            aud = claims.get("aud")
            exp = claims.get("exp")
            evf = claims.get("email_verified")
            print(f"[/auth/google][id_token] iss={iss} aud={aud} exp={exp} now={_now_ts()} email_verified={evf}")

            if iss not in ("https://accounts.google.com", "accounts.google.com"):
                raise HTTPException(status_code=401, detail="Invalid issuer")
            if aud not in _ALLOWED_CLIENT_IDS:
                raise HTTPException(status_code=401, detail="Invalid audience")
            if not claims.get("email"):
                raise HTTPException(status_code=401, detail="No email in id_token")
            if evf is False:
                raise HTTPException(status_code=401, detail="Email not verified")
            if exp and exp < _now_ts():
                raise HTTPException(status_code=401, detail="Token expired")

            email = claims["email"]
            name = claims.get("name") or email.split("@")[0]
            sub = claims.get("sub")

        # ---------- 2) access_token 경로 ----------
        elif act:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # (a) tokeninfo로 audience 검증
                ti = await client.get(
                    "https://www.googleapis.com/oauth2/v1/tokeninfo",
                    params={"access_token": act},
                )
                if ti.status_code != 200:
                    print("[/auth/google][access_token] tokeninfo failed:", ti.text)
                    raise HTTPException(status_code=401, detail="Invalid access_token")
                tjson = ti.json()
                aud = tjson.get("audience") or tjson.get("issued_to")
                print(f"[/auth/google][access_token] tokeninfo.aud={aud}")
                if aud not in _ALLOWED_CLIENT_IDS:
                    raise HTTPException(status_code=401, detail="Invalid audience (access_token)")

                # (b) userinfo로 프로필/이메일 확인
                ui = await client.get(
                    "https://www.googleapis.com/oauth2/v3/userinfo",
                    headers={"Authorization": f"Bearer {act}"},
                )
                if ui.status_code != 200:
                    print("[/auth/google][access_token] userinfo failed:", ui.text)
                    raise HTTPException(status_code=401, detail="userinfo failed")
                uij = ui.json()
                email = uij.get("email")
                if not email:
                    raise HTTPException(status_code=401, detail="No email from userinfo")
                if uij.get("email_verified") is False:
                    raise HTTPException(status_code=401, detail="Email not verified")

                name = uij.get("name") or email.split("@")[0]
                sub = uij.get("sub")

        else:
            raise HTTPException(status_code=400, detail="id_token or access_token is required")

        # ---------- 유저 조회/생성 ----------
        user = await service.get_or_create_google_user(
            db, email=email, username=name
        )

        # ---------- 우리 서비스 JWT 발급 ----------
        access = create_access_token(user_id=user.id, email=user.email)
        refresh = create_refresh_token(user_id=user.id, email=user.email)
        print("[auth/google] access_token =", access, "...")  # 앞부분만 출력
        print("[auth/google] refresh_token =", refresh[:70], "...")
        print(user.id)
        print(user.email)
        print("확인용 글자")
        return {
            "accessToken": access,
            "refreshToken": refresh,
            "tokenType": "bearer",
            "user": {"id": user.id, "email": user.email, "username": user.username},
        }

    except HTTPException:
        raise
    except Exception as e:
        # 상세 원인은 서버 로그로만 출력
        import traceback; traceback.print_exc()
        print("[/auth/google][ERROR]", e)
        raise HTTPException(status_code=401, detail="Invalid Google token")    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
#
@auth_router.post("/refresh")
async def refresh_access_token(payload: dict = Body(...)):
    refresh_token = payload.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=400, detail="refresh_token is required")

    try:
        data = decode_token(refresh_token)
        if data.get("type") != "refresh":
            raise HTTPException(status_code=400, detail="Invalid token type")
        user_id = int(data["sub"])
        email = data["email"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh_token")

    new_access = create_access_token(user_id=user_id, email=email)
    return {"access_token": new_access, "token_type": "bearer"}



'''
@auth_router.post("/google", response_model=schemas.TokenBundle)  # [CHANGED] schemas.TokenOut → TokenBundle
async def google_login_mobile(payload: schemas.GoogleLoginIn, db: AsyncSession = Depends(get_db)):
    """
    Flutter/웹: google_sign_in으로 받은 ID 토큰(필수)을 전달하면,
    서버가 검증 후 서비스용 access/refresh 토큰과 user를 반환.
    """
    idt = payload.id_token
    try:
        info = google_id_token.verify_oauth2_token(
            idt,
            grequests.Request(),
            GOOGLE_CLIENT_ID,  # aud 검증
        )
        if info.get("iss") not in ("https://accounts.google.com", "accounts.google.com"):
            raise ValueError("Invalid issuer")
        if not info.get("email"):
            raise ValueError("No email from Google")
        if not info.get("email_verified", False):
            raise ValueError("Email not verified")

        email = info["email"]
        name = info.get("name") or email.split("@")[0]
        sub = info.get("sub")
        

        user = await service.get_or_create_google_user(
            db, email=email, username=name, google_sub=sub
        )

        access = create_access_token(user_id=user.id, email=user.email)
        refresh = create_refresh_token(user_id=user.id, email=user.email)

        # [CHANGED] 프론트가 바로 user 모델을 채울 수 있도록 user 포함
        return {
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                
            },
        }

    except Exception:
        # 너무 자세한 에러는 노출하지 않음
        raise HTTPException(status_code=401, detail="Invalid Google token")

'''







'''
# app/core/user/auth_router.py
import os
from urllib.parse import quote
from fastapi import APIRouter, Request, Depends, HTTPException, Body
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.dependencies import get_db
from .oauth import oauth
from app.common.security import create_access_token, create_refresh_token, decode_token
from app.core.user import schemas, service

from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as grequests
from dotenv import load_dotenv

load_dotenv()
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

auth_router = APIRouter()

# ---------------------------
# 1) 웹: 리다이렉트 시작
# ---------------------------
@auth_router.get("/google")
async def google_login(request: Request):
    """
    프론트(웹)에서 /auth/google?redirect=<프론트콜백URL>로 진입.
    구글 로그인 → /auth/google/callback 으로 돌아옴.
    """
    redirect_uri = request.url_for("google_auth")  # /auth/google/callback
    app_redirect = request.query_params.get("redirect")
    if app_redirect:
        # 콜백에서 사용할 프론트 콜백 URL 저장
        request.session["post_auth_redirect"] = app_redirect
    return await oauth.google.authorize_redirect(request, redirect_uri)

# ---------------------------
# 2) 웹: 구글 콜백 → 프론트 콜백 URL로 해시 리다이렉트
# ---------------------------
@auth_router.get("/google/callback", name="google_auth")
async def google_auth(request: Request, db: AsyncSession = Depends(get_db)):
    token = await oauth.google.authorize_access_token(request)

    # id_token 확보
    idt = token.get("id_token")
    if not idt:
        raise HTTPException(status_code=400, detail="id_token not found")

    # 구글 사용자 정보
    user_info = token.get("userinfo") or await oauth.google.parse_id_token(request, token)
    email = user_info.get("email")
    name = user_info.get("name") or (email.split("@")[0] if email else None)
    if not email:
        raise HTTPException(status_code=400, detail="No email provided by Google")

    # 유저 조회/생성
    user = await service.get_or_create_google_user(db, email=email, username=name)

    # 우리 서비스 토큰 발급
    access_token = create_access_token(user_id=user.id, email=user.email)
    refresh_token = create_refresh_token(user_id=user.id, email=user.email)

    # 프론트 콜백 URL (앱에서 넘긴 redirect)
    app_redirect = request.session.pop("post_auth_redirect", None)
    if app_redirect:
        # 해시에 태워서 프론트로 넘김 (공백/특수문자 대비 간단 인코딩)
        url = (
            f"{app_redirect}"
            f"#access_token={quote(access_token)}"
            f"&refresh_token={quote(refresh_token)}"
            f"&token_type=bearer"
            f"&user_id={user.id}"
            f"&email={quote(user.email)}"
            f"&username={quote(user.username or '')}"
        )
        return RedirectResponse(url)

    # redirect 파라미터를 안 넘긴 경우 JSON으로 동일 포맷 리턴
    return JSONResponse(
        {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
            },
        }
    )

# ---------------------------
# 3) 모바일/테스트: ID 토큰 교환
# ---------------------------
@auth_router.post("/google", response_model=schemas.TokenBundle)
async def google_login_mobile(payload: schemas.GoogleLoginIn, db: AsyncSession = Depends(get_db)):
    """
    Flutter(모바일/웹 테스트): google_sign_in 등으로 받은 ID 토큰을 전달하면,
    서버가 검증 후 access/refresh 토큰과 user를 JSON으로 반환.
    """
    idt = payload.id_token
    try:
        info = google_id_token.verify_oauth2_token(
            idt,
            grequests.Request(),
            GOOGLE_CLIENT_ID,  # aud 검증
        )
        if info.get("iss") not in ("https://accounts.google.com", "accounts.google.com"):
            raise ValueError("Invalid issuer")
        if not info.get("email"):
            raise ValueError("No email from Google")
        if not info.get("email_verified", False):
            raise ValueError("Email not verified")

        email = info["email"]
        name = info.get("name") or email.split("@")[0]
        sub = info.get("sub")  # 필요 시 DB에 google_sub로 저장

        user = await service.get_or_create_google_user(db, email=email, username=name, google_sub=sub)

        access = create_access_token(user_id=user.id, email=user.email)
        refresh = create_refresh_token(user_id=user.id, email=user.email)

        return {
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
            },
        }

    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Google token")

# ---------------------------
# 4) 토큰 갱신
# ---------------------------
@auth_router.post("/refresh")
async def refresh_access_token(payload: dict = Body(...)):
    refresh_token = payload.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=400, detail="refresh_token is required")

    try:
        data = decode_token(refresh_token)
        if data.get("type") != "refresh":
            raise HTTPException(status_code=400, detail="Invalid token type")
        user_id = int(data["sub"])
        email = data["email"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh_token")

    new_access = create_access_token(user_id=user_id, email=email)
    return {"access_token": new_access, "token_type": "bearer"}
'''


'''
@auth_router.post("/google", response_model=schemas.TokenBundle)
async def google_login_mobile(payload: dict = Body(...), db: AsyncSession = Depends(get_db)):
   
    print("[/auth/google] payload:", payload)           # 🔍 전체 바디
    print("[/auth/google] keys:", list(payload.keys())) # 🔍 키 목록
   
    idt = payload.get("id_token") or payload.get("idToken")
    act = payload.get("access_token") or payload.get("accessToken")

    try:
        # 1) id_token 경로 (기존 동작 그대로 유지)
        if idt:
            info = google_id_token.verify_oauth2_token(
                idt,
                grequests.Request(),
                GOOGLE_CLIENT_ID,  # aud 검증
            )
            if info.get("iss") not in ("https://accounts.google.com", "accounts.google.com"):
                raise ValueError("Invalid issuer")
            if not info.get("email"):
                raise ValueError("No email from Google")
            if not info.get("email_verified", False):
                raise ValueError("Email not verified")

            email = info["email"]
            name = info.get("name") or email.split("@")[0]
            sub = info.get("sub")

        # 2) access_token 경로 (신규 추가)
        elif act:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.get(
                    "https://www.googleapis.com/oauth2/v3/userinfo",
                    headers={"Authorization": f"Bearer {act}"},
                )
            if r.status_code != 200:
                raise HTTPException(status_code=401, detail=f"userinfo failed: {r.text}")

            ui = r.json()  # {'sub','email','name','picture',...}
            email = ui.get("email")
            if not email:
                raise ValueError("No email from Google userinfo")
            name = ui.get("name") or email.split("@")[0]
            sub = ui.get("sub")

        else:
            raise HTTPException(status_code=400, detail="id_token or access_token is required")

        # 유저 조회/생성 (기존 서비스 함수 그대로 사용)
        user = await service.get_or_create_google_user(
            db, email=email, username=name, google_sub=sub
        )

        # 우리 서비스 토큰 발급 (기존 로직 그대로)
        access = create_access_token(user_id=user.id, email=user.email)
        refresh = create_refresh_token(user_id=user.id, email=user.email)

        return {
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        
        raise HTTPException(status_code=401, detail="Invalid Google token")

'''
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import os

app = FastAPI()

origins = [
    
    #프론트엔드 주소 받아서 여기에 하면 되는데 일단은 그냥 * 하기
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:52133",
    "http://localhost:57027",
    "http://localhost:64723",
    "https://e173e74c5543.ngrok-free.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"^http://(localhost|127\.0\.0\.1):\d+$",
    allow_credentials=True,   # 프론트에서 쿠키/세션 필요 시 True
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("secret_key")
    
)
from app.api.v1.router import router as api_v1_router





@app.get("/")
async def tester():
    return{"message": "서버 정상적으로 작동중입니다"}


app.include_router(api_v1_router)































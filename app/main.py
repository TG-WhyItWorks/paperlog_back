from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import os
from app.api.v1.router import router as api_v1_router

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("secret_key")
)




@app.get("/")
async def tester():
    return{"message": "서버 정상적으로 작동중입니다"}


app.include_router(api_v1_router)































from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import os


app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("secret_key")
)

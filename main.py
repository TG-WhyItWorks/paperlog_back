from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from domain.auth import auth_router
from domain.comment import comment_router
from domain.review import review_router,review_image
from domain.user import user_router
from domain.paper import folder_router
from starlette.middleware.sessions import SessionMiddleware
import os


app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("secret_key")
)

@app.get("/")
async def tester():
    return{"message": "nothing page"}


app.include_router(user_router.router)
app.include_router(review_router.router)
app.include_router(comment_router.router)
app.include_router(auth_router.router)
app.include_router(review_image.router)
app.include_router(folder_router.router)

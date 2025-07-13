from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from domain.auth import auth_router
from domain.comment import comment_router
from domain.review import review_router,review_image
from domain.user import user_router
from starlette.middleware.sessions import SessionMiddleware



app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key="a8fD93jdLqp9*4Fv34534543J8hgr34s433443yuuihu87978gsw3345gvjhbhjgsxrwqeqazwzgjkxwg61sd969679686fVb239Dlkjfks"
)

@app.get("/")
async def tester():
    return{"message": "nothing page"}


app.include_router(user_router.router)
app.include_router(review_router.router)
app.include_router(comment_router.router)
app.include_router(auth_router.router)
app.include_router(review_image.router)





from fastapi import APIRouter
from app.core.user.router import user_router
from app.core.user.auth_router import auth_router
from app.core.blog.router import review_router
from app.core.comment.router import comment_router
from app.core.search.router import search_router

router = APIRouter()
router.include_router(user_router,prefix="/api/user",tags=["User"])
router.include_router(auth_router,prefix='/auth', tags=['auth'])
router.include_router(review_router,prefix='/api/review', tags=['Review'])
router.include_router(comment_router,prefix='/api/comment', tags=['Comment'])
router.include_router(search_router,prefix='/api/search', tags=['Search'])






















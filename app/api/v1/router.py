


from fastapi import APIRouter
from app.core.user.router import user_router
from app.core.user.auth_router import auth_router



router = APIRouter()
router.include_router(user_router,prefix="/api/user",tags=["User"])
router.include_router(auth_router,prefix='/auth', tags=['auth'])























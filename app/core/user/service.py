from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.user.schemas import UserCreate,UserUpdate
from app.core.user.models import User
from passlib.context import CryptContext
from datetime import datetime,UTC

pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")

async def create_user(db: AsyncSession, user_create: UserCreate):
    db_user = User(
        username=user_create.username,
        password=pwd_context.hash(user_create.password),
        email=user_create.email,
        phonenumber=user_create.phonenumber
    )
    db.add(db_user)
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise
    
    await db.refresh(db_user)
    return db_user
    
async def get_existing_user(db: AsyncSession, user_create: UserCreate):
    stmt = select(User).where(
        (User.username == user_create.username) |
        (User.email == user_create.email) 
        
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
    
    

async def get_user_by_userId(db: AsyncSession, user_id: int):
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def get_or_create_google_user(session: AsyncSession, email: str, username: str):
    try:
    
   
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if user:
            return user

        user = User(email=email, username=username, password=None, phonenumber=None)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
    except Exception:
        await session.rollback()
        raise


async def update_user(db: AsyncSession, db_user: User, user_update: UserUpdate):
    db_user.nickname = user_update.nickname
    db_user.phonenumber = user_update.phonenumber
    db_user.bio = user_update.bio
    db_user.intro = user_update.intro
    db_user.modify_date=datetime.now(UTC)
    db.add(db_user)
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise
    await db.refresh(db_user)
    return db_user


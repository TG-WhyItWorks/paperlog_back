from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from domain.user.user_schema import UserCreate
from models import User
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")

async def create_user(db: AsyncSession, user_create: UserCreate):
    db_user = User(
        username=user_create.username,
        password=pwd_context.hash(user_create.password),
        email=user_create.email,
        phonenumber=user_create.phonenumber
    )
    db.add(db_user)
    await db.commit()
    
    
async def get_existing_user(db: AsyncSession, user_create: UserCreate):
    stmt = select(User).where(
        (User.username == user_create.username) |
        (User.email == user_create.email) |
        (User.phonenumber == user_create.phonenumber)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
    
    
async def get_user(db: AsyncSession, username: str):
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()



async def get_or_create_google_user(session: AsyncSession, email: str, username: str):
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user:
        return user

    user = User(email=email, username=username, password="", phonenumber="")
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user



async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    result = await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()
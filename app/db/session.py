
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine,AsyncSession


SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./app.db"




engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)




async def get_db():
    async with SessionLocal() as session:
        yield session

























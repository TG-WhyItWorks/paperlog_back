from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine,AsyncSession
#import databases


SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./app.db"
#database = databases.Database(SQLALCHEMY_DATABASE_URL)



engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


Base = declarative_base()




async def get_db():
    async with SessionLocal() as session:
        yield session





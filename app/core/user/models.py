from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey,func,UniqueConstraint
from sqlalchemy.orm import relationship
from fastapi_users.db import SQLAlchemyBaseUserTable
from app.db.base import Base
from datetime import datetime,UTC

class User(Base):
    __tablename__ = "user"
    __table_args__ = {"sqlite_autoincrement": True}
    id=Column(Integer,primary_key=True)
    password=Column(String,nullable=True)
    username = Column(String, unique=False, nullable=False)
    email= Column(String, unique=True, nullable=False)
    phonenumber = Column(String, unique=True, nullable=True)
    nickname = Column(String, unique=True, nullable=True)
    bio = Column(String, unique=False, nullable=True)
    intro = Column(Text, unique=False, nullable=True)
    modify_date = Column(DateTime, nullable=True)
    readpapers= relationship("ReadPaper", back_populates="user",lazy="selectin")
    folders = relationship("Folder", back_populates="user", lazy="selectin")
    paper_likes = relationship("PaperLike", back_populates="user", cascade="all, delete-orphan", lazy="selectin")
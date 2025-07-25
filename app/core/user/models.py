from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey,func,UniqueConstraint
from sqlalchemy.orm import relationship
from fastapi_users.db import SQLAlchemyBaseUserTable
from app.db import Base
from datetime import datetime,UTC

class User(Base):
    __tablename__ = "user"

    id=Column(Integer,primary_key=True)
    password=Column(String,nullable=True)
    username = Column(String, unique=False, nullable=False)
    email= Column(String, unique=True, nullable=False)
    phonenumber = Column(String, unique=True, nullable=True)
    modify_date = Column(DateTime, nullable=True)

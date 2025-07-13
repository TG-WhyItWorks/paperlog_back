from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey,func
from sqlalchemy.orm import relationship
from fastapi_users.db import SQLAlchemyBaseUserTable
from database import Base


class User(Base):
    __tablename__ = "user"

    id=Column(Integer,primary_key=True)
    password=Column(String,nullable=False)
    username = Column(String, unique=False, nullable=False)
    email= Column(String, unique=False, nullable=False)
    phonenumber = Column(String, unique=True, nullable=False)
    modify_date = Column(DateTime, nullable=True)

class Review(Base):
    __tablename__="review"


    id=Column(Integer,primary_key=True, autoincrement=True)
    title=Column(String,nullable=False)
    content=Column(Text,nullable=False)
    create_date=Column(DateTime(timezone=True),
                       server_default=func.now(),
                       nullable=False)
    user_id=Column(Integer,ForeignKey("user.id"),nullable=True)
    user=relationship("User",backref="review_users")


class Comment(Base):
    __tablename__="comment"


    id=Column(Integer,primary_key=True, autoincrement=True)
    content=Column(Text,nullable=False)
    create_date=Column(DateTime(timezone=True),
                       server_default=func.now(),
                       nullable=False)
    review_id=Column(Integer,ForeignKey("review.id"))
    review=relationship("Review",backref="comments")
    user_id=Column(Integer,ForeignKey("user.id"),nullable=True)
    user=relationship("User",backref="comment_users")
    modify_date=Column(DateTime,nullable=True)
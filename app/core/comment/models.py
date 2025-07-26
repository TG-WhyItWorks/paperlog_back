from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey,func,UniqueConstraint
from sqlalchemy.orm import relationship
from fastapi_users.db import SQLAlchemyBaseUserTable
from app.db.base import Base
from datetime import datetime,UTC

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

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey,func,UniqueConstraint
from sqlalchemy.orm import relationship
from fastapi_users.db import SQLAlchemyBaseUserTable
from app.db import Base
from datetime import datetime,UTC





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
    paper_id=Column(Integer,ForeignKey("paper.id"),nullable=True)
    paper=relationship("Paper",backref="review_papers") 
    images = relationship("ReviewImage", back_populates="review", cascade="all, delete-orphan")
    
    
    
    
class ReviewImage(Base):
    __tablename__="review_image"
    
    id=Column(Integer,primary_key=True,autoincrement=True)
    review_id = Column(Integer, ForeignKey("review.id"), nullable=False)
    image_path = Column(String, nullable=False)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    
    review=relationship("Review",back_populates="images")


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
        
    
    
    
    
    
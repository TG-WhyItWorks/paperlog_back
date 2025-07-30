
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey,func,UniqueConstraint,Table
from sqlalchemy.orm import relationship
from fastapi_users.db import SQLAlchemyBaseUserTable
from app.db.base import Base
from datetime import datetime,UTC


review_voter = Table(
    'review_voter',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id'), primary_key=True),
    Column('review_id', Integer, ForeignKey('review.id'), primary_key=True)
)


class Review(Base):
    __tablename__="review"


    id=Column(Integer,primary_key=True, autoincrement=True)# 1부터 시작
    title=Column(String,nullable=False)
    content=Column(Text,nullable=False)
    create_date=Column(DateTime(timezone=True),
                       server_default=func.now(),
                       nullable=False)
    user_id=Column(Integer,ForeignKey("user.id"),nullable=True)
    user=relationship("User",backref="review_users")  
    paper_id=Column(Integer,ForeignKey("papers.arxiv_id"))
    paper = relationship("Paper", back_populates="reviews")
    images = relationship("ReviewImage", back_populates="review", cascade="all, delete-orphan")
    voter = relationship('User', secondary=review_voter, backref='review_voters')
    
    
    
    
class ReviewImage(Base):
    __tablename__="review_image"
    
    id=Column(Integer,primary_key=True,autoincrement=True)
    review_id = Column(Integer, ForeignKey("review.id"), nullable=False)
    image_path = Column(String, nullable=False)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    
    review=relationship("Review",back_populates="images")



        
    
    
    
    
    
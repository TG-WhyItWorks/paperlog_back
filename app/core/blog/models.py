
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
    __table_args__ = {"sqlite_autoincrement": True}#이거 안하니까 글 삭제하면 문제 생김

    id=Column(Integer,primary_key=True, autoincrement=True)
    title=Column(String,nullable=False)
    content=Column(Text,nullable=False)
    create_date=Column(DateTime, nullable=True)
    modify_date = Column(DateTime, nullable=True)
    user_id=Column(Integer,ForeignKey("user.id"),nullable=True)
    user=relationship("User",backref="review_users")  
    paper_id=Column(Integer,ForeignKey("papers.arxiv_id"))
    paper = relationship("Paper", back_populates="reviews")
    images = relationship("ReviewImage", back_populates="review", cascade="all, delete-orphan",lazy="selectin")
    voter = relationship('User', secondary=review_voter, backref='review_voters',lazy="selectin")
    
 

class ReviewImage(Base):
    __tablename__="review_image"
    
    id=Column(Integer,primary_key=True,autoincrement=True)
    review_id = Column(Integer, ForeignKey("review.id"), nullable=False)
    image_path = Column(String, nullable=True)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    
    review=relationship("Review",back_populates="images",lazy="selectin")



        
    
    
    
    
    
        
    
    
    
    
    
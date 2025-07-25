from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey,func,UniqueConstraint
from sqlalchemy.orm import relationship
from fastapi_users.db import SQLAlchemyBaseUserTable
from database import Base
from datetime import datetime,UTC

class User(Base):
    __tablename__ = "user"

    id=Column(Integer,primary_key=True)
    password=Column(String,nullable=True)
    username = Column(String, unique=False, nullable=False)
    email= Column(String, unique=True, nullable=False)
    phonenumber = Column(String, unique=True, nullable=True)
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
    
    
class Paper(Base):
    __tablename__="paper" 
    
    id=Column(Integer,primary_key=True, autoincrement=True)
    abstract=Column(Text,nullable=True)
    title=Column(String,nullable=False)
    author=Column(String,nullable=False)
    folder_papers = relationship("FolderPaper", back_populates="paper")



class ReadPaper(Base):
    __tablename__ = "read_paper"
    __table_args__ = (
        UniqueConstraint("user_id", "paper_id", name="unique_user_paper_read"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    paper_id = Column(Integer, ForeignKey("paper.id"), nullable=False)
    read_at = Column(DateTime, default=datetime.now(UTC))
    memo = Column(Text, nullable=True)
    rating = Column(Integer, nullable=True)  
    create_date=Column(DateTime(timezone=True),
                       server_default=func.now(),
                       nullable=False)
    user = relationship("User", back_populates="read_papers")
    paper = relationship("Paper", back_populates="read_by_users")
    
    
    
class Folder(Base):
    
    __tablename__="folder"
    id=Column(Integer,primary_key=True, autoincrement=True)
    parent_id=Column(Integer,nullable=True)
    user_id=Column(Integer,ForeignKey("user.id"),nullable=False)
    name=Column(String,nullable=False)
    parent_id = Column(Integer, ForeignKey("folder.id"), nullable=True)
    papers = relationship("FolderPaper", back_populates="folder")

class FolderPaper(Base):
    __tablename__ = "folder_paper"
    __table_args__ = (
        UniqueConstraint('folder_id', 'paper_id', name='unique_folder_paper'),
    )

    id = Column(Integer, primary_key=True, index=True)
    folder_id = Column(Integer, ForeignKey("folder.id"), nullable=False)
    paper_id = Column(Integer, ForeignKey("paper.id"), nullable=False)
    added_at = Column(DateTime, default=datetime.now(UTC))

    folder = relationship("Folder", back_populates="papers")
    paper = relationship("Paper", back_populates="folder_papers")
    
    
    
    

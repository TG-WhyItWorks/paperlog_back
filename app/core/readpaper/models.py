
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey,func,UniqueConstraint,Table
from sqlalchemy.orm import relationship
from fastapi_users.db import SQLAlchemyBaseUserTable
from app.db.base import Base
from datetime import datetime,UTC



    
class ReadPaper(Base):
    __tablename__ = "read_papers"
    __table_args__ = (
    UniqueConstraint("user_id", "paper_id", name="uq_user_paper"),
)
    id=Column(Integer,primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False, index=True)
    create_date=Column(DateTime,nullable=False)
    user  = relationship("User", back_populates="readpapers")
    paper = relationship("Paper", back_populates="readpapers")
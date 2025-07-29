from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.db.base import Base
from datetime import datetime


class Paper(Base):
    __tablename__ = "papers"
    
    arxiv_id = Column(Integer, primary_key=True, index=True)#arxiv 내 논문 고유 ID
    title = Column(String(300), nullable=False)
    authors = Column(String(300), nullable=False)
    summary = Column(Text, nullable=True)
    link = Column(String(500), nullable=False)
    published = Column(DateTime, nullable=False)
    publish_updated = Column(String(300), nullable=False)
    categories = Column(String(300), nullable=True) # arxiv에 개제된 후 업데이트 시
    doi = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    blogs = relationship("Review", back_populates="paper", cascade="all, delete-orphan")
    
    
    # 디버그용 로그 출력 -> print(paper) 하면 title, authors 출력됨.
    def __repr__(self):
        return f"<Paper(title={self.title[:30]}..., authors={self.authors})>"
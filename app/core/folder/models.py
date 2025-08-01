from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref
from datetime import datetime, UTC
from app.db.base import Base


class Folder(Base):
    __tablename__ = "folders"
    
    id = Column(Integer, primary_key=True, index=True)
    folder_name = Column(String(200), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    parent_folder_id = Column(Integer, ForeignKey("folders.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    
    user = relationship("User", back_populates="folders", lazy="selectin")
    parent_folder = relationship(
        "Folder",
        remote_side=lambda: [Folder.id],
        backref=backref("subfolders", cascade="all, delete-orphan", lazy="selectin"),
        lazy="selectin"
    )
    folder_papers = relationship("FolderPaper", back_populates="folder", cascade="all, delete-orphan", lazy="selectin")
    
    
class FolderPaper(Base):
    __tablename__ = "folder_papers"
        
    id = Column(Integer, primary_key=True, index=True)
    folder_id = Column(Integer, ForeignKey("folders.id", ondelete="CASCADE"), nullable=False)
    paper_id = Column(Integer, ForeignKey("papers.id", ondelete="CASCADE"), nullable=True)
    review_id = Column(Integer, ForeignKey("review.id", ondelete="CASCADE"), nullable=True)
        
    folder = relationship("Folder", back_populates="folder_papers", lazy="selectin")
    paper = relationship("Paper", lazy="selectin")
    review = relationship("Review", lazy="selectin")
        
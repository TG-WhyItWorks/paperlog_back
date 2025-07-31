from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, UTC
from app.db.base import Base


class Folder(Base):
    __tablename__ = "folders"
    
    id = Column(Integer, primary_key=True, index=True)
    folder_name = Column(String(200), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    parent_folder_id = Column(Integer, ForeignKey("folders.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    
    user = relationship("User", back_populates="folders", lazy="selectin")
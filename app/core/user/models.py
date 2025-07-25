from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey,func,UniqueConstraint
from sqlalchemy.orm import relationship
from fastapi_users.db import SQLAlchemyBaseUserTable
from app.db.base import Base
from datetime import datetime,UTC
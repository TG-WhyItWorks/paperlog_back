from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.common.dependencies import get_db
from app.core.search import service
from app.core.search.schemas import PaperDetail

router = APIRouter()
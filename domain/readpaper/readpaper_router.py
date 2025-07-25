from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from fastapi import Form, File, UploadFile
from typing import Optional
from database import get_db
from domain.readpaper import readpaper_schema, readpaper_crud
from domain.user.user_router import get_current_user
from models import User,Paper

router = APIRouter(prefix="/api/readpaper", tags=["ReadPaper"])




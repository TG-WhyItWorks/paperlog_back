import os
from dotenv import load_dotenv
from jose import jwt
from datetime import datetime, timedelta,UTC

load_dotenv(".env")

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not isinstance(SECRET_KEY, str):
    raise ValueError("JWT_SECRET_KEY must be a string.")

ALGORITHM = "HS256"
EXPIRE_MINUTES = 60

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=EXPIRE_MINUTES)
    to_encode.update({"exp": int(expire.timestamp())})  
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


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

'''
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=EXPIRE_MINUTES)
    to_encode.update({"exp": int(expire.timestamp())})  
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
'''




def create_access_token(user_id: int, email: str) -> str:
    now = datetime.now(UTC)
    expire = now + timedelta(minutes=EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),            # 표준 subject 클레임: 주로 ID
        "email": email,                 # 커스텀 클레임
        "exp": int(expire.timestamp())  # 만료 시간
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

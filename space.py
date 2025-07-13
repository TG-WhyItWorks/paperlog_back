from jose import jwt
import os

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
print("SECRET_KEY:", SECRET_KEY, type(SECRET_KEY))  # ⬅️ 타입까지 출력

data = {"sub": "test@example.com"}

if not isinstance(SECRET_KEY, str):
    raise ValueError("SECRET_KEY must be a string")

# 이 줄에서 오류가 난다면 진짜 문자열이 아닐 가능성이 있음
token = jwt.encode(data, SECRET_KEY, algorithm="HS256")
print("TOKEN:", token)
from datetime import datetime, timedelta, timezone
from jose import jwt
from dotenv import load_dotenv
import os

load_dotenv()
SECRET_KEY=os.getenv("SECRET_KEY")
ALGORITHM="HS256"

# for login auth
def create_access_token(data: dict):
    to_encode=data.copy()
    expire=datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp":expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# for password reset
def create_reset_token(username: str):
    payload = {
        "sub": username,
        "purpose": "reset_password",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=15)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
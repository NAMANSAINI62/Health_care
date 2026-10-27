import os    # it is a python built in module to read file, folders and secret variables.
from datetime import datetime, timedelta, timezone
from typing import Optional 
from jose import jwt, JWTError # it is used to encode and decode tokens and provide the valid errors.
from passlib.context import CryptContext # it is a class which manage password hashing

SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "fallback-dev-secret-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440 # 60min * 24hr = 1440 min
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # it automatically flags old algorithms as outdated if I add a new algorithms later.


def get_password_hash(password: str) -> str: 
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool: 
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires:
        expire = datetime.now(timezone.utc) + expires
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    try: 
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
    
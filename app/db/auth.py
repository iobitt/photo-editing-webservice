from datetime import datetime, timedelta
from typing import Union
from jose import jwt
from passlib.hash import pbkdf2_sha256

from app.models.user import User


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def decode_token(token, secret_key):
    return jwt.decode(token, secret_key, algorithms=[ALGORITHM])


def create_access_token(data: dict, secret_key: str, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)


def authenticate_user(user: User, password: str, salt: str):
    if not user:
        return False
    if not pbkdf2_sha256.verify(password + salt, user.password_digest):
        return False
    return user

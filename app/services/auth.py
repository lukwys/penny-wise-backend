import os

import bcrypt
import re
from typing import Annotated
from fastapi import Depends, Query, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt
from datetime import datetime, timezone, timedelta

SECRET_KEY = os.getenv("SECRET_KEY")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="sessions")

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not set")


def hash_password(password: str):
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password_bytes, salt).decode()

    return password_hash


def validate_password(password: Annotated[str, Query(min_length=8)]):
    if not (re.search(r"[A-Z]", password)):
        raise HTTPException(422, "Password must contain an uppercase letter")
    if not (re.search(r"\d", password)):
        raise HTTPException(422, "Password must contain a digit")
    if not re.search(r"[^a-zA-Z0-9]", password):
        raise HTTPException(422, "Password must contain a special character")
    return password


def create_access_token(data: dict):
    data_copy = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(weeks=1)
    data_copy.update({"exp": expire})
    encoded_jwt = jwt.encode(data_copy, SECRET_KEY, "HS256")

    return encoded_jwt


def validate_token(token: str = Depends(oauth2_scheme)):
    try:
        jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(401, "Invalid token")

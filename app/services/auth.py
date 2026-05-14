import bcrypt
import re
from typing import Annotated
from fastapi import Query, HTTPException


def hash_password(password: str):
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password_bytes, salt)

    return password_hash


def validate_password(password: Annotated[str, Query(min_length=8)]):
    if not (re.search(r"[A-Z]", password)):
        raise HTTPException(422, "Password must contain an uppercase letter")
    if not (re.search(r"\d", password)):
        raise HTTPException(422, "Password must contain a digit")
    if not re.search(r"[^a-zA-Z0-9]", password):
        raise HTTPException(422, "Password must contain a special character")
    return password

from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import EmailStr
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select
import bcrypt

from app.schemas.token import Token
from app.database import SessionDep
from app.models.user import User
from app.services.auth import (
    create_access_token,
    hash_password,
    validate_password,
)

auth_router = APIRouter(tags=["auth"])

@auth_router.post("/users")
async def create_user(
    email: EmailStr,
    password: Annotated[str, Depends(validate_password)],
    user_name: Annotated[str, Query(min_length=4)],
    session: SessionDep,
):
    password_hash = hash_password(password)
    user = User(email=email, password_hash=password_hash, user_name=user_name)
    session.add(user)
    session.commit()


@auth_router.post("/sessions")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep):
    statement = select(User).where(form_data.username == User.email)
    user = session.exec(statement).first()

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    verify_password = bcrypt.checkpw(
        form_data.password.encode(), user.password_hash.encode()
    )

    if not verify_password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": str(user.id)})

    return Token(access_token=access_token, token_type="bearer")


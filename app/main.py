from dotenv import load_dotenv

load_dotenv()
from app.services.expenses import scan_receipt_text
from fastapi import FastAPI, HTTPException, Query, Depends, Request, UploadFile
from typing import Annotated
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import EmailStr
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
import bcrypt
from pydantic import BaseModel

from app.services.auth import (
    create_access_token,
    hash_password,
    validate_password,
    validate_token,
)

from .database import create_db_and_tables, engine
from .models.user import User


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


class Token(BaseModel):
    access_token: str
    token_type: str


@app.exception_handler(IntegrityError)
def integrity_exepction_handler(_request: Request, _exc: IntegrityError):
    return JSONResponse(status_code=409, content={"message": "Email already used"})


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/users")
async def create_user(
    email: EmailStr,
    password: Annotated[str, Depends(validate_password)],
    user_name: Annotated[str, Query(min_length=4)],
):
    password_hash = hash_password(password)
    user = User(email=email, password_hash=password_hash, user_name=user_name)

    with Session(engine) as session:
        session.add(user)
        session.commit()


@app.post("/sessions")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    with Session(engine) as session:
        statement = select(User).where(form_data.username == User.email)
        user = session.exec(statement).first()

        if user is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        verify_password = bcrypt.checkpw(
            form_data.password.encode(), user.password_hash.encode()
        )

        if not verify_password:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        access_token = create_access_token({"sub": form_data.username})

        return Token(access_token=access_token, token_type="bearer")


@app.post("/expenses/scan", dependencies=[Depends(validate_token)])
async def scan_receipt(receipt: UploadFile):
    scanned_text = await scan_receipt_text(receipt)

    return scanned_text

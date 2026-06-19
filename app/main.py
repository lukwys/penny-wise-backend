from dotenv import load_dotenv

from app.exceptions import OcrError, ParsingError
from app.models.item import Item

load_dotenv()
from app.models.expense import Expense
from app.schemas.expense import ExpenseCreate, ExpenseRead
from app.services.ai_parser import get_parser
from app.services.receipt_scanner import scan_receipt_text
from app.schemas.token import Token
from fastapi import FastAPI, HTTPException, Query, Depends, Request, UploadFile
from typing import Annotated
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
import bcrypt

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


CONSTRAINT_MESSAGES = {
    "user_email_key": "Email already used",
    "fallback": "Database constraint violated",
}


@app.exception_handler(IntegrityError)
def integrity_exepction_handler(_request: Request, exc: IntegrityError):
    error_code = int(exc.orig.pgcode)
    if error_code == 23505:
        return JSONResponse(
            status_code=409,
            content={
                "message": CONSTRAINT_MESSAGES.get(
                    exc.orig.diag.constraint_name, CONSTRAINT_MESSAGES["fallback"]
                )
            },
        )
    if error_code == 23502:
        return JSONResponse(
            status_code=422, content={"message": "Missing required field"}
        )
    return JSONResponse(
        status_code=500, content={"message": CONSTRAINT_MESSAGES["fallback"]}
    )


@app.exception_handler(OcrError)
def ocr_exception_handler(_request: Request, exc: OcrError):
    return JSONResponse(status_code=422, content={"message": str(exc)})


@app.exception_handler(ParsingError)
def parsing_exception_handler(_request, exc: ParsingError):
    return JSONResponse(status_code=502, content={"message": str(exc)})


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

        access_token = create_access_token({"sub": str(user.id)})

        return Token(access_token=access_token, token_type="bearer")


@app.post("/expenses/scan", dependencies=[Depends(validate_token)])
async def scan_receipt(receipt: UploadFile):
    scanned_text = await scan_receipt_text(receipt)
    parser = get_parser()

    return parser.parse(scanned_text)


@app.post("/expenses")
async def create_expense(
    expense: ExpenseCreate, user_id: Annotated[int, Depends(validate_token)]
):
    exp = Expense(user_id=user_id, **expense.model_dump(exclude={"items"}))

    with Session(engine) as session:
        session.add(exp)
        session.flush()

        for item in expense.items:
            expense_item = Item(expense_id=exp.id, **item.model_dump())
            session.add(expense_item)

        session.add
        session.commit()


@app.get("/expenses/recent", response_model=list[ExpenseRead])
async def get_recent_expenses(user_id: Annotated[int, Depends(validate_token)]):
    with Session(engine) as session:
        statement = (
            select(Expense)
            .where(Expense.user_id == user_id)
            .order_by(Expense.date.desc())
            .limit(10)
        )
        expenses = session.exec(statement).all()

        return expenses

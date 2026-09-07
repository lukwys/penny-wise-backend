from app.exceptions import OcrError, ParsingError
from app.models.item import Item

from app.models.expense import Expense
from app.schemas.expense import ExpenseCreate, ExpenseRead
from app.services.ai_parser import get_parser
from app.services.receipt_scanner import scan_receipt_text
from fastapi import FastAPI, Depends, Request, UploadFile
from typing import Annotated
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError

from app.services.auth import (
    validate_token,
)

from .database import engine
from .routers.auth import auth_router

app = FastAPI()


CONSTRAINT_MESSAGES = {
    "user_email_key": "Email already used",
    "fallback": "Database constraint violated",
}

app.include_router(auth_router)


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

from fastapi import APIRouter, Depends, UploadFile
from typing import Annotated
from sqlmodel import Session, select

from app.database import engine
from app.models.item import Item
from app.models.expense import Expense
from app.schemas.expense import ExpenseCreate, ExpenseRead
from app.services.ai_parser import get_parser
from app.services.receipt_scanner import scan_receipt_text
from app.services.auth import (
    validate_token,
)

expenses_router = APIRouter()

@expenses_router.post("/expenses/scan", dependencies=[Depends(validate_token)])
async def scan_receipt(receipt: UploadFile):
    scanned_text = await scan_receipt_text(receipt)
    parser = get_parser()

    return parser.parse(scanned_text)


@expenses_router.post("/expenses")
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

        session.commit()

        return exp


@expenses_router.get("/expenses/recent", response_model=list[ExpenseRead])
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
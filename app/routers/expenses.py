from fastapi import APIRouter, Depends, UploadFile
from typing import Annotated
from sqlmodel import select

from app.database import SessionDep
from app.models.item import Item
from app.models.expense import Expense
from app.schemas.expense import ExpenseCreate, ExpenseRead, ExpenseWithItems
from app.services.ai_parser import get_parser
from app.services.receipt_scanner import scan_receipt_text
from app.services.auth import (
    validate_token,
)

expenses_router = APIRouter(prefix="/expenses", tags=["expenses"], dependencies=[Depends(validate_token)])

@expenses_router.post("/scan")
async def scan_receipt(receipt: UploadFile):
    scanned_text = await scan_receipt_text(receipt)
    parser = get_parser()

    return parser.parse(scanned_text)


@expenses_router.post("", response_model=ExpenseWithItems, status_code=201)
async def create_expense(
    expense: ExpenseCreate,
    user_id: Annotated[int, Depends(validate_token)],
    session: SessionDep,
):
    exp = Expense(
        user_id=user_id,
        **expense.model_dump(exclude={"items"}),
        items=[Item(**item.model_dump()) for item in expense.items],
    )

    session.add(exp)
    session.commit()

    return exp


@expenses_router.get("/recent", response_model=list[ExpenseRead])
async def get_recent_expenses(user_id: Annotated[int, Depends(validate_token)], session: SessionDep):
    statement = (
        select(Expense)
        .where(Expense.user_id == user_id)
        .order_by(Expense.date.desc())
        .limit(10)
    )
    expenses = session.exec(statement).all()

    return expenses
        
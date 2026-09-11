from pydantic import BaseModel, Field
from datetime import date
from decimal import Decimal

from app.schemas.item import ItemCreate, ItemRead


class ExpenseCreate(BaseModel):
    vendor: str
    date: date
    total_amount: Decimal = Field(max_digits=10, decimal_places=2)
    currency: str
    category: str
    items: list[ItemCreate]


class ExpenseRead(BaseModel):
    id: int
    vendor: str
    date: date
    total_amount: Decimal = Field(max_digits=10, decimal_places=2)
    currency: str
    category: str

class ExpenseWithItems(ExpenseRead):
    items: list[ItemRead]

from pydantic import BaseModel, Field
from datetime import date
from decimal import Decimal

from app.schemas.item import ItemCreate


class ExpenseCreate(BaseModel):
    vendor: str
    date: date
    total_amount: Decimal = Field(max_digits=10, decimal_places=2)
    currency: str
    category: str
    items: list[ItemCreate]


class ExpenseRead(BaseModel):
    vendor: str
    date: date
    total_amount: Decimal = Field(max_digits=10, decimal_places=2)
    currency: str
    category: str

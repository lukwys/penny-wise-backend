from sqlmodel import SQLModel, Field
from datetime import date
from decimal import Decimal


class Expense(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    vendor: str
    date: date
    total_amount: Decimal = Field(max_digits=10, decimal_places=2)
    currency: str
    category: str
    user_id: int = Field(foreign_key="user.id")

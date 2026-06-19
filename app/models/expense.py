from sqlmodel import SQLModel, Field
from datetime import date


class Expense(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    vendor: str
    date: date
    total_amount: float
    currency: str
    category: str
    user_id: int = Field(foreign_key="user.id")

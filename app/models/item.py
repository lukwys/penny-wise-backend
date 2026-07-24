from sqlmodel import SQLModel, Field
from decimal import Decimal


class Item(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    price: Decimal = Field(max_digits=10, decimal_places=2)
    expense_id: int = Field(foreign_key="expense.id")

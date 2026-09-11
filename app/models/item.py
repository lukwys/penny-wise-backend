from sqlmodel import Relationship, SQLModel, Field
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.expense import Expense


class Item(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    price: Decimal = Field(max_digits=10, decimal_places=2)
    expense_id: int = Field(foreign_key="expense.id")
    expense: "Expense" = Relationship(back_populates="items")

from pydantic import BaseModel
from datetime import date

from app.schemas.item import ItemCreate


class ExpenseCreate(BaseModel):
    vendor: str
    date: date
    total_amount: float
    currency: str
    category: str
    items: list[ItemCreate]

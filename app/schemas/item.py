from decimal import Decimal

from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    name: str
    price: Decimal = Field(max_digits=10, decimal_places=2)

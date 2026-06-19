from pydantic import BaseModel


class ItemCreate(BaseModel):
    name: str
    price: float

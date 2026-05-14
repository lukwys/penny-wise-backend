from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
  id: int | None = Field(default=None, primary_key=True)
  email: str
  password_hash: str
  user_name: str
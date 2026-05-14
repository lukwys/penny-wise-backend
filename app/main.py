from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlmodel import Session

from app.services.auth import hash_password

from .database import create_db_and_tables, engine
from .models.user import User

@asynccontextmanager
async def lifespan(app: FastAPI):
  create_db_and_tables()
  yield

app = FastAPI(lifespan=lifespan)

@app.get("/health")
async def health():
  return {"status": "healthy"}

@app.post("/users")
async def createUser(email: str, password: str, user_name: str):
  password_hash = hash_password(password)

  user = User(email=email, password_hash=password_hash, user_name=user_name)

  with Session(engine) as session:
    session.add(user)
    session.commit()

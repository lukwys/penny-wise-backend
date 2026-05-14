from fastapi import FastAPI
from contextlib import asynccontextmanager

from .database import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
  create_db_and_tables()
  yield

app = FastAPI(lifespan=lifespan)

@app.get("/health")
async def health():
  return {"status": "healthy"}

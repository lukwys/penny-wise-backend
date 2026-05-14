from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager

from .database import create_db_and_tables

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
  create_db_and_tables()
  yield

@app.get("/health")
async def health():
  return {"status": "healthy"}

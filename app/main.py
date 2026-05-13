from fastapi import FastAPI

from .database import create_db_and_tables

app = FastAPI()

@app.on_event("startup")
async def startup_event():
  create_db_and_tables()

@app.get("/health")
async def health():
  return {"status": "healthy"}

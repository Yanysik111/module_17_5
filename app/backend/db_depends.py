from sqlalchemy.orm import Session
from fastapi import Depends
from .db import SessionLocal

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
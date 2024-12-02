from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated
from sqlalchemy.sql import text

from app.models import User, Task
from app.schemas import CreateUser, UpdateUser
from app.backend.db import Base

from app.models import *
from sqlalchemy import insert, select, update, delete
from slugify import slugify


router = APIRouter(prefix="/user", tags=["user"])


@router.get("/")
async def all_users(db: Annotated[Session, Depends(get_db)]):
    users = db.execute(select(User)).scalars().all()
    return users


@router.get("/{user_id}")
async def user_by_id(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.execute(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User was not found")
    return user


@router.post("/create")
async def create_user(create_user: CreateUser, db: Annotated[Session, Depends(get_db)]):
    existing_user = db.execute(
        select(User).where(User.username == create_user.username)).first()

    if existing_user:
        raise HTTPException(status_code=409, detail="User with this username already exists.")

    try:
        new_user = User(
            username=create_user.username,
            firstname=create_user.firstname,
            lastname=create_user.lastname,
            age=create_user.age,
            slug=slugify(create_user.username),)
        db.add(new_user)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating user: {e}")

    return {"status_code": status.HTTP_201_CREATED, "message": "User created successfully"}


@router.put("/update/{user_id}")
async def update_user(user_id: int, update_user: UpdateUser, db: Annotated[Session, Depends(get_db)]):
    current_user = db.execute(select(User).where(User.id == user_id)).first()
    if not current_user:
        raise HTTPException(status_code=404, detail="User was not found")

    db.execute(
        update(User)
        .where(User.id == user_id)
        .values(
            firstname=update_user.firstname,
            lastname=update_user.lastname,
            age=update_user.age,))
    db.commit()

    return {"status_code": status.HTTP_200_OK,"message": "User updated successfully",}


@router.delete("/delete/{user_id}")
async def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.execute(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User was not found")

    db.execute(delete(Task).where(Task.user_id == user_id))
    db.execute(delete(User).where(User.id == user_id))
    db.commit()

    return { "status_code": status.HTTP_200_OK,"message": "User deleted successfully",}

@router.get("/user_id/tasks")
async def tasks_by_user_id(user_id: int, db: Annotated[Session, Depends(get_db)]):
    tasks = db.execute(select(Task).where(Task.user_id == user_id)).scalars().all()
    if not tasks:
        raise HTTPException(status_code=404, detail="User was not found")
    return tasks
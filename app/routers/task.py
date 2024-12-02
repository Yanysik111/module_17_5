from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated
from app.models import Task, User
from app.schemas import CreateTask, UpdateTask
from sqlalchemy import insert, select, update, delete
from slugify import slugify


router = APIRouter(prefix="/task", tags =["task"])


@router.get("/")
async def all_tasks(db: Annotated[Session, Depends(get_db)]):
    tasks = db.execute(select(Task)).scalars().all()
    return tasks
@router.get("/task_id")
async def task_by_id(task_id: int, db: Annotated[Session, Depends(get_db)]):
    task = db.execute(select(Task).where(Task.id == task_id)).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task was not found")
    return task

@router.post("/create")
async def create_task(user_id: int,create_task: CreateTask, db: Annotated[Session, Depends(get_db)]):
    current_user = db.execute(select(User).where(User.id == user_id)).first()
    if not current_user:
        raise HTTPException(status_code=404, detail="User was not found")

    new_task = Task(title=create_task.title,
                    content=create_task.content,
                    priority=create_task.priority,
                    slug=slugify(create_task.title),
                    user_id=user_id,)
    db.add(new_task)
    db.commit()

    return {'status_code': status.HTTP_201_CREATED, 'transaction': 'Successful'}

@router.put("/update")
async def update_task(task_id: int, update_task: UpdateTask, db: Annotated[Session, Depends(get_db)]):
    current_task = db.execute(select(Task).where(Task.id == task_id)).first()
    if not current_task:
        raise HTTPException(status_code=404, detail="User was not found")

    db.execute(
        update(Task)
        .where(Task.id == task_id)
        .values(
            title=update_task.title,
            content=update_task.content,
            priority=update_task.priority,))
    db.commit()

    return {"status_code": status.HTTP_200_OK,"message": "User updated successfully",}

@router.delete("/delete")
async def delete_task(task_id: int, db: Annotated[Session, Depends(get_db)]):
    task = db.execute(select(Task).where(Task.id == task_id)).first()
    if not task:
        raise HTTPException(status_code=404, detail="User was not found")

    db.execute(delete(Task).where(Task.id == task_id))
    db.commit()
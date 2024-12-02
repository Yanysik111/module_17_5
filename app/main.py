from fastapi import FastAPI

from app.routers import user
from app.routers import task

app= FastAPI(swagger_ui_parameters={'tryItOutEnabled': True})

@app.get('/')
async def welcome():
    return {"message": "Welcome to Taskmanager"}


app.include_router(user.router)
app.include_router(task.router)
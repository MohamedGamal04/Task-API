from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional


app = FastAPI()

@app.get("/")
async def read_root():
    return { "name": "Task API", "version": "1.0", "endpoints": ["/tasks"] }

@app.get("/health")
async def read_health():
    return { "status": "ok" }

from pydantic import BaseModel

class TaskCreate(BaseModel):
    title: Optional[str] = None
    
class Task(BaseModel):
    id: int
    title: str
    done: bool

tasks = [
    Task(id=1, title="Buy milk", done=False),
    Task(id=2, title="Walk the dog", done=False),
    Task(id=3, title="Finish assignment", done=True),
]

@app.get("/tasks")
async def get_tasks():
    return tasks

@app.post("/tasks", status_code=201)
async def create_task(task_in: TaskCreate):
    if not task_in.title or not task_in.title.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Title is required"}
        )
    task = Task(id=len(tasks) + 1, title=task_in.title, done=False)
    tasks.append(task)
    return task

@app.get("/tasks/{id}")
async def get_task(id: int):
    for task in tasks:
        if task.id == id:
            return task
    return JSONResponse(
        status_code=404,
        content={"error": f"Task {id} not found"}
    )


from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel



app = FastAPI()

@app.get("/")
async def read_root():
    return { "name": "Task API", "version": "1.0", "endpoints": ["/tasks"] }

@app.get("/health")
async def read_health():
    return { "status": "ok" }

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

@app.get("/tasks/{id}")
async def get_task(id: int):
    for task in tasks:
        if task.id == id:
            return task
    return JSONResponse(
        status_code=404,
        content={"error": f"Task {id} not found"}
    )


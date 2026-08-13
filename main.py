from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import storage
from storage import init_db

class TaskCreate(BaseModel):
    title: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

class Task(BaseModel):
    id: int
    title: str
    done: bool

app = FastAPI()

init_db()

@app.get("/", summary="Get API information")
async def read_root():
    return { "name": "Task API", "version": "1.0", "endpoints": ["/tasks"] }

@app.get("/health", summary="Check API health")
async def read_health():
    return { "status": "ok" }

def row_to_task(row):
    """Turn a database row into the same Task shape the API always returned."""
    id, title, done = row
    return Task(id=id, title=title, done=bool(done))

@app.get("/tasks", summary="List all tasks")
async def get_tasks():
    return [row_to_task(row) for row in storage.list_tasks()]

@app.post("/tasks", status_code=201, summary="Create a new task")
async def create_task(task_in: TaskCreate):
    if not task_in.title or not task_in.title.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Title is required"}
        )
    return row_to_task(storage.create_task(task_in.title))

@app.get("/tasks/{id}", summary="Get a specific task")
async def get_task(id: int):
    row = storage.get_task(id)
    if row is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {id} not found"}
        )
    return row_to_task(row)


@app.put("/tasks/{id}", summary="Update a specific task")
async def update_task(id: int, task_in: TaskUpdate):
    if task_in.title is not None and not task_in.title.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Title cannot be empty"}
        )

    current = storage.get_task(id)
    if current is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {id} not found"}
        )

    _, current_title, current_done = current
    title = task_in.title if task_in.title is not None else current_title
    done = task_in.done if task_in.done is not None else current_done
    return row_to_task(storage.update_task(id, title, done))


@app.delete("/tasks/{id}", status_code=204, summary="Delete a specific task")
async def delete_task(id: int):
    if not storage.delete_task(id):
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {id} not found"}
        )
    return Response(status_code=204)
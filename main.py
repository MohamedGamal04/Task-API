from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from database import init_db, get_connection

class TaskCreate(BaseModel):
    title: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

class Task(BaseModel):
    id: int
    title: str
    done: bool

tasks = [
    Task(id=1, title="Buy milk", done=False),
    Task(id=2, title="Walk the dog", done=False),
    Task(id=3, title="Finish assignment", done=True),
]

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
    return Task(id=row["id"], title=row["title"], done=bool(row["done"]))

@app.get("/tasks", summary="List all tasks")
async def get_tasks():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()
    return [row_to_task(row) for row in rows]

@app.post("/tasks", status_code=201, summary="Create a new task")
async def create_task(task_in: TaskCreate):
    if not task_in.title or not task_in.title.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Title is required"}
        )
    task = Task(id=len(tasks) + 1, title=task_in.title, done=False)
    tasks.append(task)
    return task

@app.get("/tasks/{id}", summary="Get a specific task")
async def get_task(id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (id,)).fetchone()
    conn.close()
    if row is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {id} not found"}
        )
    return row_to_task(row)


@app.put("/tasks/{id}", summary="Update a specific task")
async def update_task(id: int, task_in: TaskUpdate):
    for task in tasks:
        if task.id == id:
            if task_in.title is not None:
                if not task_in.title.strip():
                    return JSONResponse(
                        status_code=400,
                        content={"error": "Title cannot be empty"}
                    )
                task.title = task_in.title
            if task_in.done is not None:
                task.done = task_in.done
            return task
    return JSONResponse(
        status_code=404,
        content={"error": f"Task {id} not found"}
    )
    
@app.delete("/tasks/{id}", status_code=204, summary="Delete a specific task")
async def delete_task(id: int):
    for task in tasks:
        if task.id == id:
            tasks.remove(task)
            return Response(status_code=204)
    return JSONResponse(
        status_code=404,
        content={"error": f"Task {id} not found"}
    )
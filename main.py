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
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        (task_in.title, 0)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return Task(id=new_id, title=task_in.title, done=False)

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
    if task_in.title is not None and not task_in.title.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Title cannot be empty"}
        )

    conn = get_connection()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (id,)).fetchone()
    if row is None:
        conn.close()
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {id} not found"}
        )

    title = task_in.title if task_in.title is not None else row["title"]
    done = task_in.done if task_in.done is not None else bool(row["done"])
    conn.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (title, int(done), id)
    )
    conn.commit()
    conn.close()
    return Task(id=id, title=title, done=done)


@app.delete("/tasks/{id}", status_code=204, summary="Delete a specific task")
async def delete_task(id: int):
    conn = get_connection()
    cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (id,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    if deleted == 0:
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {id} not found"}
        )
    return Response(status_code=204)
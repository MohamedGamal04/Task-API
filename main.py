import json

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import storage
from storage import init_db
from auth import SUPABASE_URL, supabase

class Credentials(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None

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
print(f"Server running and connected to Supabase at {SUPABASE_URL}")

@app.get("/", summary="Get API information")
async def read_root():
    return { "name": "Task API", "version": "1.0", "endpoints": ["/tasks"] }

@app.get("/health", summary="Check API health")
async def read_health():
    return { "status": "ok" }

# --- Auth (A4) -------------------------------------------------------------
# Supabase is the Identity Provider: it stores the accounts, hashes the
# passwords and signs the tokens. This app never stores a password itself.

@app.post("/auth/signup", status_code=201, tags=["auth"], summary="Create a new user account")
async def signup(credentials: Credentials):
    if not credentials.email or not credentials.password:
        return JSONResponse(
            status_code=400,
            content={"error": "Email and password are required"}
        )
    try:
        response = supabase.auth.sign_up(
            {"email": credentials.email, "password": credentials.password}
        )
    except Exception as error:
        return JSONResponse(status_code=400, content={"error": str(error)})
    return {"user": json.loads(response.user.model_dump_json())}

@app.post("/auth/login", tags=["auth"], summary="Log in and receive an access token")
async def login(credentials: Credentials):
    if not credentials.email or not credentials.password:
        return JSONResponse(
            status_code=400,
            content={"error": "Email and password are required"}
        )
    try:
        response = supabase.auth.sign_in_with_password(
            {"email": credentials.email, "password": credentials.password}
        )
    except Exception:
        return JSONResponse(
            status_code=401,
            content={"error": "Invalid login credentials"}
        )
    return {
        "access_token": response.session.access_token,
        "refresh_token": response.session.refresh_token,
        "token_type": "bearer",
    }

# --- Public & protected routes (A4) ----------------------------------------

@app.get("/public/info", tags=["public"], summary="Public info, no auth needed")
async def public_info():
    return {"message": "Welcome stranger! This info is public."}

@app.get("/protected/profile", tags=["protected"], summary="Private profile data")
async def protected_profile(request: Request):
    header = request.headers.get("Authorization", "")
    scheme, _, token = header.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return JSONResponse(
            status_code=401,
            content={"error": "Access token required"}
        )
    # Stage 3 replaces this with real verification against Supabase.
    return {"message": "A token was presented", "token_received": True}

# --- Tasks (A1-A3) ---------------------------------------------------------

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
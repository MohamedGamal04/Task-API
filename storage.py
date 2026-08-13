"""The one module that talks to the database.

Storage swap #3: memory (A1) -> SQLite (A2) -> Postgres (A3). The routes in
main.py never learn which one is underneath.
"""
import os

import psycopg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgres://postgres:dev@localhost:5432/tasks")

SEED_TASKS = [
    ("Buy milk", False),
    ("Walk the dog", False),
    ("Finish assignment", False),
]


def get_connection():
    """Open a connection to Postgres using the connection string from .env."""
    return psycopg.connect(DATABASE_URL)


def init_db():
    """Create the tasks table if missing, and seed three examples only when empty."""
    with get_connection() as conn, conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                done BOOLEAN NOT NULL DEFAULT FALSE
            )
        """)
        cursor.execute("SELECT COUNT(*) FROM tasks")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO tasks (title, done) VALUES (%s, %s)",
                SEED_TASKS,
            )


def list_tasks():
    with get_connection() as conn, conn.cursor() as cursor:
        cursor.execute("SELECT id, title, done FROM tasks ORDER BY id")
        return cursor.fetchall()


def get_task(id: int):
    with get_connection() as conn, conn.cursor() as cursor:
        cursor.execute("SELECT id, title, done FROM tasks WHERE id = %s", (id,))
        return cursor.fetchone()


def create_task(title: str):
    with get_connection() as conn, conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id, title, done",
            (title, False),
        )
        return cursor.fetchone()


def update_task(id: int, title: str, done: bool):
    with get_connection() as conn, conn.cursor() as cursor:
        cursor.execute(
            "UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING id, title, done",
            (title, done, id),
        )
        return cursor.fetchone()


def delete_task(id: int) -> bool:
    """Return True if a row was actually deleted."""
    with get_connection() as conn, conn.cursor() as cursor:
        cursor.execute("DELETE FROM tasks WHERE id = %s", (id,))
        return cursor.rowcount > 0

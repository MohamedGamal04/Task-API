# Task API — FlyRank Backend Track W2 · A1 + W3 · A2

A small CRUD API for managing a to-do list, built with **Python** and **FastAPI**. Supports creating,
reading, updating, and deleting tasks — now backed by a real **SQLite** database instead of an
in-memory list, so the data survives a server restart. Includes interactive API docs via Swagger UI.

The endpoints did not change between A1 and A2; only the storage layer did.

## How to run it

**Requirements:** Python 3.10+

1. Install dependencies:
   ```bash
   pip install fastapi uvicorn
   ```

2. Start the server:
   ```bash
   uvicorn main:app --reload
   ```

3. The API is now running at `http://127.0.0.1:8000`. Interactive docs are available at `http://127.0.0.1:8000/docs`.

That is the one command you need. `tasks.db` is created automatically on first run, the `tasks`
table is created if missing, and three example tasks are seeded **only when the table is empty** —
restarting never duplicates them.

## Endpoints

| Method | Path | Description | Status codes |
|--------|------|-------------|--------------|
| GET | `/` | API info | 200 |
| GET | `/health` | Health check | 200 |
| GET | `/tasks` | List all tasks | 200 |
| POST | `/tasks` | Create a new task | 201, 400 empty/missing title |
| GET | `/tasks/{id}` | Get a specific task | 200, 404 unknown id |
| PUT | `/tasks/{id}` | Update a specific task (title and/or done) | 200, 400 empty title, 404 unknown id |
| DELETE | `/tasks/{id}` | Delete a specific task | 204, 404 unknown id |

## Example request

```bash
curl -i -X POST http://127.0.0.1:8000/tasks -H "Content-Type: application/json" -d '{"title":"Buy milk"}'
```

```
HTTP/1.1 201 Created
date: Thu, 13 Aug 2026 09:23:14 GMT
server: uvicorn
content-length: 40
content-type: application/json

{"id":4,"title":"Buy milk","done":false}
```

Create a task, stop the server, start it again, then `GET /tasks` — the task is still there.

## Swagger UI

Full CRUD cycle tested via `/docs` — create, list, update, and delete a task, all through the
"Try it out" interface.

## Why SQLite

- **One file, zero setup** — no server to install or run; the whole database is `tasks.db`.
- **Persistence** — tasks survive a restart, unlike the in-memory list of Assignment 1.
- **Standard library** — Python ships with `sqlite3`, so there is no extra dependency.

## Where the database lives

`tasks.db` in the project root, created automatically by `init_db()` in `database.py`.
It is **git-ignored**, so a clean clone starts fresh: run the command above and `GET /tasks`
returns the three seeded example tasks.

## SQL by hand (Stage 4)

Opened `tasks.db` in DB Browser for SQLite and ran queries directly against it. The same queries
live in `sql_playground.py` (`python sql_playground.py`).

Example query:

```sql
SELECT * FROM tasks WHERE done = 1;
```

It returned only the completed rows — after `UPDATE tasks SET done = 1 WHERE id = 1;` the row
`(1, 'Buy milk', 1)` appeared, and `GET /tasks` showed `"done": true` for that task immediately,
with no server restart: the API and DB Browser read the exact same file. There is no syncing;
there is one source of truth.

### DB Browser screenshot

![tasks.db open in DB Browser for SQLite](docs/db-browser.jpg)

## Notes

- Data now lives in `tasks.db` on disk — it survives server restarts.
- All CRUD operations use SQL with **parameterized placeholders** (`?`); no user input is ever
  glued into a SQL string.
- All error responses (`400`, `404`) return a JSON body in the form `{"error": "..."}`.

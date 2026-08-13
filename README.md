# Task API — FlyRank Backend Track W2 · A1

A small CRUD API for managing a to-do list, built with **Python** and **FastAPI**. Supports creating, reading, updating, and deleting tasks, backed by an in-memory list (no database yet). Includes interactive API docs via Swagger UI.

## How to run it

**Requirements:** Python 3.10+

1. Install dependencies:
   ```bash
   pip install fastapi uvicorn
   ```

2. Start the server:
   ```bash
   uvicorn to_do_list:app --reload
   ```

3. The API is now running at `http://127.0.0.1:8000`. Interactive docs are available at `http://127.0.0.1:8000/docs`.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | API info |
| GET | `/health` | Health check |
| GET | `/tasks` | List all tasks |
| POST | `/tasks` | Create a new task |
| GET | `/tasks/{id}` | Get a specific task |
| PUT | `/tasks/{id}` | Update a specific task (title and/or done) |
| DELETE | `/tasks/{id}` | Delete a specific task |

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

## Swagger UI

Full CRUD cycle tested via `/docs` — create, list, update, and delete a task, all through the "Try it out" interface.

![Swagger UI screenshot](./swagger-screenshot.png)

## Notes

- Data is stored in memory only — it resets whenever the server restarts. This is intentional for this stage; persistence with a database is coming in Week 3.
- All error responses (`400`, `404`) return a JSON body in the form `{"error": "..."}`.

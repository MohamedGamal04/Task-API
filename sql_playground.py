"""Stage 4 — running SQL by hand against tasks.db.

Same queries as the DB Browser "Execute SQL" tab, kept in the repo so the
results are reproducible. Run with: python sql_playground.py
"""
import sqlite3

conn = sqlite3.connect("tasks.db")
conn.row_factory = sqlite3.Row

QUERIES = [
    "SELECT * FROM tasks;",                 # list every task
    "SELECT * FROM tasks WHERE done = 1;",  # only completed tasks
    "SELECT COUNT(*) FROM tasks;",          # how many tasks are there?
]

for query in QUERIES:
    rows = conn.execute(query).fetchall()
    print(query)
    for row in rows:
        print("   ", tuple(row))
    print()

# A query that changes data — the API sees it instantly, no restart needed.
conn.execute("UPDATE tasks SET done = 1 WHERE id = 1;")
conn.commit()
print("after UPDATE tasks SET done = 1 WHERE id = 1;")
for row in conn.execute("SELECT * FROM tasks WHERE done = 1;"):
    print("   ", tuple(row))

conn.close()

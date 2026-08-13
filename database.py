import sqlite3
 
DB_NAME = "tasks.db"
 
def get_connection():
    """Open a connection to the SQLite database file (creates it if missing)."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # lets us access columns by name, e.g. row["title"]
    return conn
 
def init_db():
    """Create the tasks table if it doesn't exist, and seed 3 example tasks
    only if the table is currently empty."""
    conn = get_connection()
    cursor = conn.cursor()
 
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0
        )
    """)
 
    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]
 
    if count == 0:
        cursor.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            [
                ("Buy milk", 0),
                ("Walk the dog", 0),
                ("Finish assignment", 0),
            ],
        )
 
    conn.commit()
    conn.close()
                                                 
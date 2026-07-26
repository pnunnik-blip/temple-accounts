import sqlite3
from pathlib import Path

# Create data folder if it doesn't exist
Path("data").mkdir(exist_ok=True)

# Database file path
DB_NAME = "data/temple.db"


def get_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS test (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT
        )
        """)

        conn.commit()
        conn.close()

        print("Database created successfully!")

    except Exception as e:
        print("Database Error:", e)
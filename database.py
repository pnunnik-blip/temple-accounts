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
    """Create all required tables."""
    conn = get_connection()
    cursor = conn.cursor()

    # Vazhipadu Master Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vazhipadu_master (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        amount REAL NOT NULL,
        active INTEGER DEFAULT 1
    )
    """)

    # Income Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS income (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        receipt_no TEXT,
        date TEXT,
        devotee_name TEXT,
        star TEXT,
        offerings TEXT,
        amount REAL,
        payment_mode TEXT,
        remarks TEXT
    )
    """)

    # Expense Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        voucher_no TEXT,
        date TEXT,
        category TEXT,
        description TEXT,
        amount REAL,
        payment_mode TEXT
    )
    """)

    conn.commit()
    conn.close()
import sqlite3
from datetime import datetime

DB_PATH = "shanduko.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def save_message(phone_number: str, role: str, content: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO conversations (phone_number, role, content) VALUES (?, ?, ?)",
        (phone_number, role, content),
    )
    conn.commit()
    conn.close()


def get_history(phone_number: str, limit: int = 10) -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        SELECT role, content FROM conversations
        WHERE phone_number = ?
        ORDER BY timestamp DESC
        LIMIT ?
        """,
        (phone_number, limit),
    )
    rows = c.fetchall()
    conn.close()
    # Return in chronological order
    return [{"role": row[0], "content": row[1]} for row in reversed(rows)]


def clear_history(phone_number: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM conversations WHERE phone_number = ?", (phone_number,))
    conn.commit()
    conn.close()

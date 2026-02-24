import sqlite3
import os
from pathlib import Path

db_path = Path(os.path.expanduser("~/.flint/chat_history.db"))

def init_db():
    if not db_path.parent.exists():
        db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                role TEXT,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
            )
        """)

def create_session(title="New Chat"):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO sessions (title) VALUES (?)", (title,))
        return cursor.lastrowid

def add_message(session_id, role, content):
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
            (session_id, role, content)
        )

def get_sessions():
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, created_at FROM sessions ORDER BY id DESC")
        return [dict(row) for row in cursor.fetchall()]

def get_messages(session_id):
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT role, content FROM messages WHERE session_id = ? ORDER BY id ASC", (session_id,))
        return [dict(row) for row in cursor.fetchall()]

def rename_session(session_id, new_title):
    with sqlite3.connect(db_path) as conn:
        conn.execute("UPDATE sessions SET title = ? WHERE id = ?", (new_title, session_id))

def delete_session(session_id):
    with sqlite3.connect(db_path) as conn:
        conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))

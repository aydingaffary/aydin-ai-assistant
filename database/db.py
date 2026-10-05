import sqlite3

DATABASE_NAME = "aydin_ai.db"


def get_connection():
    """Create database connection."""

    return sqlite3.connect(DATABASE_NAME)


def init_database():
    """Create database tables."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            is_premium INTEGER DEFAULT 0,
            created_at TEXT
        )
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
        """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            feature TEXT NOT NULL,
            usage_date TEXT NOT NULL,
            count INTEGER DEFAULT 1,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
        """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS favorite_teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            team_id INTEGER NOT NULL,
            team_name TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    """)
    connection.commit()
    connection.close()

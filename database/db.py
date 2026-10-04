import sqlite3


DATABASE_NAME = "aydin_ai.db"


def get_connection():
    """Create database connection."""

    return sqlite3.connect(DATABASE_NAME)


def init_database():
    """Create database tables."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            is_premium INTEGER DEFAULT 0,
            created_at TEXT
        )
        """
    )

    connection.commit()
    connection.close()
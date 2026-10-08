
"""Database configuration and connection management."""

import sqlite3
from contextlib import contextmanager
from typing import Iterator


DATABASE_NAME = "aydin_ai.db"


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """Create and safely manage a database connection."""

    connection = sqlite3.connect(
        DATABASE_NAME,
        timeout=10,
    )

    try:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 10000")

        yield connection

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def init_database() -> None:
    """Create database tables."""

    with get_connection() as connection:

        connection.execute("PRAGMA journal_mode = WAL")

        # Users
        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                is_premium INTEGER DEFAULT 0,
                premium_until TEXT,
                created_at TEXT
            )
        """)

        # AI requests
        connection.execute("""
            CREATE TABLE IF NOT EXISTS ai_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'allowed',
                provider TEXT DEFAULT 'unknown',
                response_time REAL,
                prompt_length INTEGER,
                response_length INTEGER,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id)
                REFERENCES users(user_id)
            )
        """)

        # Migrate existing ai_requests table
        columns = {
            row[1]
            for row in connection.execute(
                "PRAGMA table_info(ai_requests)"
            ).fetchall()
        }

        if "provider" not in columns:
            connection.execute(
                """
                ALTER TABLE ai_requests
                ADD COLUMN provider TEXT DEFAULT 'unknown'
                """
            )

        if "response_time" not in columns:
            connection.execute(
                """
                ALTER TABLE ai_requests
                ADD COLUMN response_time REAL
                """
            )

        if "prompt_length" not in columns:
            connection.execute(
                """
                ALTER TABLE ai_requests
                ADD COLUMN prompt_length INTEGER
                """
            )

        if "response_length" not in columns:
            connection.execute(
                """
                ALTER TABLE ai_requests
                ADD COLUMN response_length INTEGER
                """
            )

        # Messages
        connection.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id)
                REFERENCES users(user_id)
            )
        """)

        # AI usage
        connection.execute("""
            CREATE TABLE IF NOT EXISTS ai_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                feature TEXT NOT NULL,
                usage_date TEXT NOT NULL,
                count INTEGER DEFAULT 1,
                FOREIGN KEY(user_id)
                REFERENCES users(user_id)
            )
        """)

        # User activity
        connection.execute("""
            CREATE TABLE IF NOT EXISTS user_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                feature TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id)
                REFERENCES users(user_id)
            )
        """)

        # Favorite teams
        connection.execute("""
            CREATE TABLE IF NOT EXISTS favorite_teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                team_id INTEGER NOT NULL,
                team_name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id)
                REFERENCES users(user_id)
            )
        """)

        connection.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_favorite_teams_user_team
            ON favorite_teams(user_id, team_id)
        """)

        # Conversation memory
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS conversation_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                summary TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        # Payments
        connection.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                plan TEXT NOT NULL,
                amount INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id)
                REFERENCES users(user_id)
            )
        """)

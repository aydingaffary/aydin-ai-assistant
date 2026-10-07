"""AI security service."""

from datetime import datetime

from database.db import get_connection


class AISecurityService:
    """Handle AI request monitoring."""

    def log_request(
        self,
        user_id: int,
        content: str,
        status: str = "allowed",
    ):

        with get_connection() as connection:

            connection.execute(
                """
                INSERT INTO ai_requests
                (
                    user_id,
                    content,
                    status,
                    created_at
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    user_id,
                    content,
                    status,
                    datetime.now().isoformat(),
                ),
            )


    def get_recent_requests(
        self,
        limit=20,
    ):

        with get_connection() as connection:

            return connection.execute(
                """
                SELECT
                    user_id,
                    content,
                    status,
                    created_at
                FROM ai_requests
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
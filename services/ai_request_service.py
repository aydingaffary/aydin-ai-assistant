from datetime import datetime

from database.db import get_connection


class AIRequestService:
    """Track AI requests."""

    def log_request(
        self,
        user_id: int,
        content: str,
        status: str = "allowed",
        provider: str = "unknown",
        response_time: float = 0,
        prompt_length: int = 0,
        response_length: int = 0,
    ) -> None:
        """Save AI request log."""

        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO ai_requests
                (
                    user_id,
                    content,
                    status,
                    provider,
                    response_time,
                    prompt_length,
                    response_length,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    content,
                    status,
                    provider,
                    response_time,
                    prompt_length,
                    response_length,
                    datetime.now().isoformat(),
                ),
            )

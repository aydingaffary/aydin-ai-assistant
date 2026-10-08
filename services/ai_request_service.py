
"""AI request logging service."""

from datetime import datetime

from database.db import get_connection


class AIRequestService:
    """Track AI requests."""

    MAX_CONTENT_LENGTH = 4000

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

        if user_id <= 0:
            return

        if not isinstance(content, str):
            return

        content = content[: self.MAX_CONTENT_LENGTH]

        prompt_length = max(0, int(prompt_length))
        response_length = max(0, int(response_length))
        response_time = max(0.0, float(response_time))

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

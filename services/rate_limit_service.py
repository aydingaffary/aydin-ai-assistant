"""AI rate limiting service."""

from datetime import datetime, timedelta

from database.db import get_connection


class RateLimitService:
    """Prevent AI spam requests."""

    MAX_REQUESTS = 5
    WINDOW_SECONDS = 60

    def is_allowed(
        self,
        user_id: int,
    ) -> bool:
        """Check user request rate."""

        limit_time = (
            datetime.now() - timedelta(seconds=self.WINDOW_SECONDS)
        ).isoformat()

        with get_connection() as connection:

            count = connection.execute(
                """
                SELECT COUNT(*)
                FROM ai_requests
                WHERE user_id = ?
                AND created_at >= ?
                """,
                (
                    user_id,
                    limit_time,
                ),
            ).fetchone()[0]

        return count < self.MAX_REQUESTS

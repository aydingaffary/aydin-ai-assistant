
"""AI performance statistics service."""

from database.db import get_connection


class AIStatsService:
    """AI performance statistics."""

    def get_stats(self):
        """Return AI performance statistics."""

        with get_connection() as connection:

            total = connection.execute(
                """
                SELECT COUNT(*)
                FROM ai_requests
                """
            ).fetchone()[0]

            providers = connection.execute(
                """
                SELECT
                    provider,
                    COUNT(*),
                    AVG(response_time),
                    AVG(response_length)
                FROM ai_requests
                WHERE provider != 'unknown'
                GROUP BY provider
                ORDER BY COUNT(*) DESC
                """
            ).fetchall()

            security = connection.execute(
                """
                SELECT
                    status,
                    COUNT(*)
                FROM ai_requests
                GROUP BY status
                ORDER BY COUNT(*) DESC
                """
            ).fetchall()

        return {
            "total": total,
            "providers": providers,
            "security": security,
        }

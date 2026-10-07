from database.db import get_connection


class AIStatsService:
    """AI performance statistics."""

    def get_stats(self):

        with get_connection() as connection:

            total = connection.execute("""
                SELECT COUNT(*)
                FROM ai_requests
                """).fetchone()[0]

            providers = connection.execute("""
                SELECT
                    provider,
                    COUNT(*),
                    AVG(response_time),
                    AVG(response_length)
                FROM ai_requests
                WHERE provider != 'unknown'
                GROUP BY provider
                """).fetchall()

            security = connection.execute("""
                SELECT
                    status,
                    COUNT(*)
                FROM ai_requests
                GROUP BY status
                """).fetchall()

        return {
            "total": total,
            "providers": providers,
            "security": security,
        }

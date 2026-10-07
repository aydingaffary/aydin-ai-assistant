"""User activity tracking service."""

from datetime import datetime

from database.db import get_connection


class ActivityService:
    """Handle user activity logs."""

    def log_activity(
        self,
        user_id: int,
        feature: str,
    ) -> None:
        """Save user activity."""

        with get_connection() as connection:

            connection.execute(
                """
                INSERT INTO user_activity (
                    user_id,
                    feature,
                    created_at
                )
                VALUES (?, ?, ?)
                """,
                (
                    user_id,
                    feature,
                    datetime.now().isoformat(),
                ),
            )

    def get_user_activity(
        self,
        user_id: int,
    ):
        """Return user activity history."""

        with get_connection() as connection:

            cursor = connection.execute(
                """
                SELECT
                    feature,
                    created_at
                FROM user_activity
                WHERE user_id = ?
                ORDER BY id DESC
                """,
                (user_id,),
            )

            return cursor.fetchall()

    def get_feature_stats(self):
        """Return usage count by feature."""

        with get_connection() as connection:

            cursor = connection.execute("""
                SELECT
                    feature,
                    COUNT(*)
                FROM user_activity
                GROUP BY feature
                ORDER BY COUNT(*) DESC
                """)

            return cursor.fetchall()

from datetime import datetime

from database.db import get_connection


class BanService:
    """Manage banned users."""

    def ban_user(
        self,
        user_id: int,
        reason: str = "No reason",
    ):
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO banned_users
                (user_id, reason, created_at)
                VALUES (?, ?, ?)
                """,
                (
                    user_id,
                    reason,
                    datetime.now().isoformat(),
                ),
            )

    def unban_user(self, user_id: int):
        with get_connection() as connection:
            connection.execute(
                """
                DELETE FROM banned_users
                WHERE user_id = ?
                """,
                (user_id,),
            )

    def is_banned(self, user_id: int) -> bool:
        with get_connection() as connection:
            result = connection.execute(
                """
                SELECT 1
                FROM banned_users
                WHERE user_id = ?
                """,
                (user_id,),
            ).fetchone()

            return result is not None

    def get_banned_users(self):
        with get_connection() as connection:
            return connection.execute("""
                SELECT user_id, created_at
                FROM banned_users
                ORDER BY created_at DESC
                """).fetchall()

    def is_banned(self, user_id: int) -> bool:
        with get_connection() as connection:
            result = connection.execute(
                """
                SELECT 1
                FROM banned_users
                WHERE user_id = ?
                """,
                (user_id,),
            ).fetchone()

        return result is not None

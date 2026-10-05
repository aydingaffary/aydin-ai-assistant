"""User AI usage limits."""

from datetime import date

from database.db import get_connection


class UserLimitManager:
    """Manage free and premium AI limits."""

    FREE_LIMIT = 10

    def can_use_ai(self, user_id: int) -> bool:
        """Check if user can use AI."""

        today = date.today().isoformat()

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT is_premium
            FROM users
            WHERE user_id = ?
            """,
            (user_id,),
        )

        user = cursor.fetchone()

        if not user:
            cursor.execute(
                """
                INSERT INTO users
                (user_id, username, is_premium, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    user_id,
                    "",
                    0,
                    today,
                ),
            )

            connection.commit()
            connection.close()
            return True

        if user[0]:
            connection.close()
            return True

        cursor.execute(
            """
            SELECT count
            FROM ai_usage
            WHERE user_id = ?
            AND feature = ?
            AND usage_date = ?
            """,
            (
                user_id,
                "smart_assistant",
                today,
            ),
        )

        usage = cursor.fetchone()

        connection.close()

        if not usage:
            return True

        return usage[0] < self.FREE_LIMIT

    def record_request(self, user_id: int) -> None:
        """Record AI request."""

        today = date.today().isoformat()

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT count
            FROM ai_usage
            WHERE user_id = ?
            AND feature = ?
            AND usage_date = ?
            """,
            (
                user_id,
                "smart_assistant",
                today,
            ),
        )

        usage = cursor.fetchone()

        if usage:
            cursor.execute(
                """
                UPDATE ai_usage
                SET count = count + 1
                WHERE user_id = ?
                AND feature = ?
                AND usage_date = ?
                """,
                (
                    user_id,
                    "smart_assistant",
                    today,
                ),
            )
        else:
            cursor.execute(
                """
                INSERT INTO ai_usage
                (user_id, feature, usage_date, count)
                VALUES (?, ?, ?, ?)
                """,
                (
                    user_id,
                    "smart_assistant",
                    today,
                    1,
                ),
            )

        connection.commit()
        connection.close()

    def remaining_requests(self, user_id: int) -> int:
        """Return remaining requests."""

        today = date.today().isoformat()

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT is_premium
            FROM users
            WHERE user_id = ?
            """,
            (user_id,),
        )

        user = cursor.fetchone()

        if user and user[0]:
            connection.close()
            return -1

        cursor.execute(
            """
            SELECT count
            FROM ai_usage
            WHERE user_id = ?
            AND feature = ?
            AND usage_date = ?
            """,
            (
                user_id,
                "smart_assistant",
                today,
            ),
        )

        usage = cursor.fetchone()

        connection.close()

        count = usage[0] if usage else 0

        return max(0, self.FREE_LIMIT - count)

    def set_premium(self, user_id: int) -> None:
        """Upgrade user."""

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE users
            SET is_premium = 1
            WHERE user_id = ?
            """,
            (user_id,),
        )

        connection.commit()
        connection.close()
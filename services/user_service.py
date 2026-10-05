
"""User management service."""

from datetime import datetime

from database.db import get_connection


class UserService:
    """Manage users and premium status."""

    def create_user(
        self,
        user_id: int,
        username: str | None = None,
    ) -> None:
        """Create user if not exists."""

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT OR IGNORE INTO users
            (user_id, username, is_premium, created_at)
            VALUES (?, ?, 0, ?)
            """,
            (
                user_id,
                username,
                datetime.now().isoformat(),
            ),
        )

        connection.commit()
        connection.close()
    def get_or_create_user(
        self,
        user_id: int,
        username: str | None = None,
    ) -> None:
        """Get existing user or create a new one."""

        self.create_user(
            user_id=user_id,
            username=username,
        )

    def is_premium(
        self,
        user_id: int,
    ) -> bool:
        """Check if user has premium access."""

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

        result = cursor.fetchone()

        connection.close()

        if not result:
            return False

        return result[0] == 1

    def set_premium(
        self,
        user_id: int,
    ) -> None:
        """Upgrade user to premium."""

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
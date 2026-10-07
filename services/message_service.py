from datetime import datetime

from database.db import get_connection


class MessageService:
    """Manage conversation messages."""

    def save_message(
        self,
        user_id: int,
        role: str,
        content: str,
    ) -> None:
        """Save a message."""

        with get_connection() as connection:

            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO messages
                (user_id, role, content, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    user_id,
                    role,
                    content,
                    datetime.now().isoformat(),
                ),
            )

    def get_messages(
        self,
        user_id: int,
    ) -> list[tuple]:
        """Get user messages."""

        with get_connection() as connection:

            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT role, content, created_at
                FROM messages
                WHERE user_id = ?
                ORDER BY id
                """,
                (user_id,),
            )

            messages = cursor.fetchall()

        return messages

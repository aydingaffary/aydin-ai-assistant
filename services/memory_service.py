"""Conversation memory service."""

from datetime import datetime

from database.db import get_connection


class MemoryService:
    """Manage AI conversation summaries."""

    def save_memory(
        self,
        user_id: int,
        summary: str,
    ) -> None:
        """Create or update user memory."""

        with get_connection() as connection:

            connection.execute(
                """
                INSERT INTO conversation_memory
                (
                    user_id,
                    summary,
                    updated_at
                )
                VALUES (?, ?, ?)

                ON CONFLICT(user_id)
                DO UPDATE SET
                    summary = excluded.summary,
                    updated_at = excluded.updated_at
                """,
                (
                    user_id,
                    summary,
                    datetime.now().isoformat(),
                ),
            )


    def get_memory(
        self,
        user_id: int,
    ) -> str:
        """Return stored memory."""

        with get_connection() as connection:

            result = connection.execute(
                """
                SELECT summary
                FROM conversation_memory
                WHERE user_id = ?
                """,
                (user_id,),
            ).fetchone()

        if result:
            return result[0]

        return ""


    def delete_memory(
        self,
        user_id: int,
    ) -> None:
        """Remove user memory."""

        with get_connection() as connection:

            connection.execute(
                """
                DELETE FROM conversation_memory
                WHERE user_id = ?
                """,
                (user_id,),
            )
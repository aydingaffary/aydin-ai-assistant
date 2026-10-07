"""AI security service."""

from datetime import datetime

from database.db import get_connection


class AISecurityService:
    """Handle AI request security and monitoring."""

    BLOCKED_WORDS = [
        "steal",
        "hack",
        "malware",
        "virus",
        "ransomware",
        "keylogger",
        "phishing",
        "password",
        "api key",
        "token",
        "دزدی",
        "هک",
        "رمز عبور",
        "کلید api",
        "ساخت بدافزار",
        "سرقت رمز",
        "فیشینگ",
    ]

    def check_request(
        self,
        content: str,
    ) -> bool:
        """Return True if request is allowed."""

        text = content.lower()

        for word in self.BLOCKED_WORDS:
            if word.lower() in text:
                return False

        return True

    def log_request(
        self,
        user_id: int,
        content: str,
        status: str = "allowed",
    ) -> None:
        """Save AI request log."""

        with get_connection() as connection:

            connection.execute(
                """
                INSERT INTO ai_requests
                (
                    user_id,
                    content,
                    status,
                    created_at
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    user_id,
                    content,
                    status,
                    datetime.now().isoformat(),
                ),
            )

    def get_recent_requests(
        self,
        limit: int = 20,
    ):
        """Return recent AI requests."""

        with get_connection() as connection:

            return connection.execute(
                """
                SELECT
                    user_id,
                    content,
                    status,
                    created_at
                FROM ai_requests
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

    def get_blocked_attempts(
        self,
        limit: int = 20,
    ):
        """Return blocked AI attempts."""

        with get_connection() as connection:

            return connection.execute(
                """
                    SELECT
                        user_id,
                        content,
                        created_at
                    FROM ai_requests
                    WHERE status = ?
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                (
                    "banned",
                    limit,
                ),
            ).fetchall()

    def get_stats(self):

        with get_connection() as connection:

            total = connection.execute("""
                SELECT COUNT(*)
                FROM ai_requests
                """).fetchone()[0]

            allowed = connection.execute(
                """
                SELECT COUNT(*)
                FROM ai_requests
                WHERE status = ?
                """,
                ("allowed",),
            ).fetchone()[0]

            banned = connection.execute(
                """
                SELECT COUNT(*)
                FROM ai_requests
                WHERE status = ?
                """,
                ("banned",),
            ).fetchone()[0]

            rate_limited = connection.execute(
                """
                SELECT COUNT(*)
                FROM ai_requests
                WHERE status = ?
                """,
                ("rate_limited",),
            ).fetchone()[0]

            users = connection.execute("""
                SELECT COUNT(DISTINCT user_id)
                FROM ai_requests
                """).fetchone()[0]

        return {
            "total": total,
            "allowed": allowed,
            "banned": banned,
            "rate_limited": rate_limited,
            "users": users,
        }

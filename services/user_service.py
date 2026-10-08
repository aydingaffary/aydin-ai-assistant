"""User service."""

from dataclasses import dataclass
from datetime import datetime

from database.db import get_connection


@dataclass
class User:
    """Represent a user."""

    user_id: int
    username: str | None
    is_premium: bool
    created_at: str


class UserService:
    """Handle user database operations."""

    def create_user(
        self,
        user_id: int,
        username: str | None = None,
    ) -> None:
        """Create user if not exists."""

        with get_connection() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO users (
                    user_id,
                    username,
                    created_at
                )
                VALUES (?, ?, ?)
                """,
                (
                    user_id,
                    username,
                    datetime.now().isoformat(),
                ),
            )

    def get_user(
        self,
        user_id: int,
    ) -> User | None:
        """Get user by ID."""

        with get_connection() as connection:
            cursor = connection.execute(
                """
                SELECT
                    user_id,
                    username,
                    is_premium,
                    created_at
                FROM users
                WHERE user_id = ?
                """,
                (user_id,),
            )

            row = cursor.fetchone()

        if row is None:
            return None

        return User(
            user_id=row[0],
            username=row[1],
            is_premium=bool(row[2]),
            created_at=row[3],
        )

    def get_or_create_user(
        self,
        user_id: int,
        username: str | None = None,
    ) -> User:
        """Get existing user or create a new one."""

        user = self.get_user(user_id)

        if user is None:
            self.create_user(
                user_id,
                username,
            )
            return self.get_user(user_id)

        if user.username != username:
            with get_connection() as connection:
                connection.execute(
                    """
                    UPDATE users
                    SET username = ?
                    WHERE user_id = ?
                    """,
                    (
                        username,
                        user_id,
                    ),
                )

            user = self.get_user(user_id)

        return user
    
    
    def is_premium(
        self,
        user_id: int,
    ) -> bool:
        """Check if user has premium access."""

        user = self.get_user(user_id)

        if user is None:
            return False

        return user.is_premium

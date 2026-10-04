from datetime import datetime

from database.db import get_connection
from models.user import User


class UserService:
    """Manage application users."""

    def get_or_create_user(
        self,
        user_id: int,
        username: str | None = None,
    ) -> User:
        """Return existing user or create a new one."""

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT user_id, username, is_premium, created_at "
            "FROM users WHERE user_id = ?",
            (user_id,),
        )

        row = cursor.fetchone()

        if row:
            user = User(
                user_id=row[0],
                username=row[1],
                is_premium=bool(row[2]),
                created_at=datetime.fromisoformat(row[3]),
            )

            if username != row[1]:
                cursor.execute(
                    "UPDATE users SET username = ? WHERE user_id = ?",
                    (username, user_id),
                )
                connection.commit()
                user.username = username

            connection.close()
            return user

        created_at = datetime.now()

        cursor.execute(
            """
            INSERT INTO users
            (user_id, username, is_premium, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                user_id,
                username,
                0,
                created_at.isoformat(),
            ),
        )

        connection.commit()
        connection.close()

        return User(
            user_id=user_id,
            username=username,
            created_at=created_at,
        )

    def get_user(self, user_id: int) -> User | None:
        """Get user by id."""

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT user_id, username, is_premium, created_at "
            "FROM users WHERE user_id = ?",
            (user_id,),
        )

        row = cursor.fetchone()
        connection.close()

        if not row:
            return None

        return User(
            user_id=row[0],
            username=row[1],
            is_premium=bool(row[2]),
            created_at=datetime.fromisoformat(row[3]),
        )
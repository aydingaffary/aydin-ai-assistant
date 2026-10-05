"""Favorite team management service."""

from datetime import datetime

from database.db import get_connection


class TeamService:
    """Manage user's favorite football teams."""

    def add_team(
        self,
        user_id: int,
        team_id: int,
        team_name: str,
    ) -> None:
        """Add a favorite team."""

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO favorite_teams
            (user_id, team_id, team_name, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                user_id,
                team_id,
                team_name,
                datetime.now().isoformat(),
            ),
        )

        connection.commit()
        connection.close()

    def get_teams(
        self,
        user_id: int,
    ) -> list[dict]:
        """Get user's favorite teams."""

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT team_id, team_name
            FROM favorite_teams
            WHERE user_id = ?
            """,
            (user_id,),
        )

        rows = cursor.fetchall()

        connection.close()

        return [
            {
                "team_id": row[0],
                "team_name": row[1],
            }
            for row in rows
        ]

    def remove_team(
        self,
        user_id: int,
        team_id: int,
    ) -> None:
        """Remove favorite team."""

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM favorite_teams
            WHERE user_id = ?
            AND team_id = ?
            """,
            (
                user_id,
                team_id,
            ),
        )

        connection.commit()
        connection.close()
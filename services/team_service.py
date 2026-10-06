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

        with get_connection() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO favorite_teams
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

    def get_teams(
        self,
        user_id: int,
    ) -> list[dict]:
        """Get user's favorite teams."""

        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT team_id, team_name
                FROM favorite_teams
                WHERE user_id = ?
                """,
                (user_id,),
            ).fetchall()

        return [
            {
                "team_id": row[0],
                "team_name": row[1],
            }
            for row in rows
        ]

    def get_subscribers(
        self,
        team_id: int,
    ) -> list[int]:
        """Get users who follow a team."""

        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT user_id
                FROM favorite_teams
                WHERE team_id = ?
                ORDER BY user_id
                """,
                (team_id,),
            ).fetchall()

        return [
            row[0]
            for row in rows
        ]

    def remove_team(
        self,
        user_id: int,
        team_id: int,
    ) -> None:
        """Remove favorite team."""

        with get_connection() as connection:
            connection.execute(
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

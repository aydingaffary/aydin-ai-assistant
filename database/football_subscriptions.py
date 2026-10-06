"""Football team subscriptions storage."""

from database.db import get_connection


class FootballSubscriptionRepository:
    """Store football team subscriptions."""

    def _create_table(self, connection) -> None:
        """Create the subscriptions table if needed."""

        connection.execute("""
            CREATE TABLE IF NOT EXISTS football_subscriptions (
                user_id INTEGER NOT NULL,
                team_id INTEGER NOT NULL,
                PRIMARY KEY (user_id, team_id)
            )
            """)

    def subscribe(
        self,
        user_id: int,
        team_id: int,
    ) -> None:
        """Subscribe a user to a team."""

        with get_connection() as connection:
            self._create_table(connection)

            connection.execute(
                """
                INSERT OR IGNORE INTO football_subscriptions (
                    user_id,
                    team_id
                )
                VALUES (?, ?)
                """,
                (
                    user_id,
                    team_id,
                ),
            )

    def unsubscribe(
        self,
        user_id: int,
        team_id: int,
    ) -> None:
        """Remove a user's team subscription."""

        with get_connection() as connection:
            self._create_table(connection)

            connection.execute(
                """
                DELETE FROM football_subscriptions
                WHERE user_id = ?
                AND team_id = ?
                """,
                (
                    user_id,
                    team_id,
                ),
            )

    def get_subscribers(
        self,
        team_id: int,
    ) -> list[int]:
        """Return users subscribed to a team."""

        with get_connection() as connection:
            self._create_table(connection)

            rows = connection.execute(
                """
                SELECT user_id
                FROM football_subscriptions
                WHERE team_id = ?
                ORDER BY user_id
                """,
                (team_id,),
            ).fetchall()

            return [row[0] for row in rows]

    def get_user_teams(
        self,
        user_id: int,
    ) -> list[int]:
        """Return teams followed by a user."""

        with get_connection() as connection:
            self._create_table(connection)

            rows = connection.execute(
                """
                SELECT team_id
                FROM football_subscriptions
                WHERE user_id = ?
                ORDER BY team_id
                """,
                (user_id,),
            ).fetchall()

            return [row[0] for row in rows]

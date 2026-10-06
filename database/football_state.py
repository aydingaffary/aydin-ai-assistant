"""Football match state storage."""

import json

from database.db import get_connection


class FootballStateRepository:
    """Store and retrieve the latest state of football matches."""

    def save(
        self,
        match_id: str,
        state: dict,
    ) -> None:
        """Save the latest match state."""

        with get_connection() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS football_match_states (
                    match_id TEXT PRIMARY KEY,
                    state TEXT NOT NULL
                )
                """)

            connection.execute(
                """
                INSERT INTO football_match_states (
                    match_id,
                    state
                )
                VALUES (?, ?)
                ON CONFLICT(match_id)
                DO UPDATE SET state = excluded.state
                """,
                (
                    match_id,
                    json.dumps(
                        state,
                        ensure_ascii=False,
                    ),
                ),
            )

    def get(
        self,
        match_id: str,
    ) -> dict | None:
        """Get the latest match state."""

        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT state
                FROM football_match_states
                WHERE match_id = ?
                """,
                (match_id,),
            ).fetchone()

            if row is None:
                return None

            return json.loads(row[0])

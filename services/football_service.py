"""Football service."""

from data.football_teams import TEAMS


class FootballService:
    """Handle football data."""

    def search_team(
        self,
        query: str,
    ) -> list[dict]:
        """Search teams by name and aliases."""

        results = []

        query = query.lower().strip()

        for team_id, team_data in TEAMS.items():
            names = [
                team_data["name"].lower(),
                *[
                    alias.lower()
                    for alias in team_data.get(
                        "aliases",
                        [],
                    )
                ],
            ]

            if any(
                query in name
                for name in names
            ):
                results.append(
                    {
                        "id": team_id,
                        "name": team_data["name"],
                        "country": "",
                    }
                )

        return results

    def get_team(
        self,
        team_id: int,
    ) -> dict | None:
        """Get team information."""

        team_data = TEAMS.get(team_id)

        if not team_data:
            return None

        return {
            "id": team_id,
            "name": team_data["name"],
            "country": "",
        }
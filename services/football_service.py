"""Football service."""

from data.football_teams import TEAMS
from services.football_provider_manager import FootballProviderManager


class FootballService:
    """Handle football data."""

    def __init__(
        self,
        provider_manager: FootballProviderManager | None = None,
    ) -> None:
        self.provider_manager = provider_manager or FootballProviderManager()

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

            if any(query in name for name in names):
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

    def get_live_matches(self) -> list[dict]:
        """Get live matches from available providers."""

        return self.provider_manager.get_live_matches()

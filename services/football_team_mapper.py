"""Map football provider teams to internal team IDs."""

from data.football_teams import TEAMS


class FootballTeamMapper:
    """Map provider-specific team identities to internal IDs."""

    @staticmethod
    def get_internal_id(
        provider: str,
        provider_team_id: int | None,
        team_name: str = "",
    ) -> int | None:
        """Return the internal team ID."""

        if provider_team_id is not None:
            for team_id, team in TEAMS.items():
                provider_ids = team.get(
                    "provider_ids",
                    {},
                )

                if (
                    provider_ids.get(provider)
                    == provider_team_id
                ):
                    return team_id

        normalized_name = team_name.lower().strip()

        if not normalized_name:
            return None

        for team_id, team in TEAMS.items():
            names = [
                team["name"].lower(),
                *[
                    alias.lower()
                    for alias in team.get(
                        "aliases",
                        [],
                    )
                ],
            ]

            if normalized_name in names:
                return team_id

        return None
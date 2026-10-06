"""Normalize football provider data."""

from dataclasses import dataclass

from services.football_team_mapper import FootballTeamMapper


@dataclass
class NormalizedEvent:
    """Standard football event."""

    minute: str
    type: str
    player: str | None = None


@dataclass
class NormalizedMatch:
    """Standard football match."""

    match_id: str
    home_team_id: int | None
    home_team: str
    away_team_id: int | None
    away_team: str
    home_score: int | None
    away_score: int | None
    status: str
    events: list[NormalizedEvent]


class FootballNormalizer:
    """Convert provider-specific football data to a common format."""

    @staticmethod
    def normalize_match(
        match: dict,
    ) -> NormalizedMatch:
        """Normalize a football match."""

        provider = match.get("provider", "")

        home_team_id = FootballTeamMapper.get_internal_id(
            provider=provider,
            provider_team_id=match.get("home_team_id"),
            team_name=match.get("home_team", ""),
        )

        away_team_id = FootballTeamMapper.get_internal_id(
            provider=provider,
            provider_team_id=match.get("away_team_id"),
            team_name=match.get("away_team", ""),
        )

        events = []

        for event in match.get("events", []):
            event_type = event.get("type")

            if event_type in {
                "goal",
                "penalty_goal",
                "own_goal",
            }:
                event_type = "goal"

            elif event_type == "red_card":
                event_type = "red_card"

            else:
                continue

            events.append(
                NormalizedEvent(
                    minute=str(event.get("minute", "")),
                    type=event_type,
                    player=event.get("player"),
                )
            )

        return NormalizedMatch(
            match_id=str(match.get("match_id", "")),
            home_team_id=home_team_id,
            home_team=match.get(
                "home_team",
                "",
            ),
            away_team_id=away_team_id,
            away_team=match.get(
                "away_team",
                "",
            ),
            home_score=match.get("home_score"),
            away_score=match.get("away_score"),
            status=match.get(
                "status",
                "unknown",
            ),
            events=events,
        )

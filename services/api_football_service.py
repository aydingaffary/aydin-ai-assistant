"""API-Football provider."""

import requests

from config import FOOTBALL_API_KEY
from services.football_provider import FootballProvider


class APIFootballProvider(FootballProvider):
    """Provide football data using API-Football."""

    BASE_URL = "https://v3.football.api-sports.io"

    def __init__(self) -> None:
        if not FOOTBALL_API_KEY:
            raise ValueError("FOOTBALL_API_KEY is not set.")

        self.headers = {
            "x-apisports-key": FOOTBALL_API_KEY
        }

    def get_live_matches(self) -> list[dict]:
        """Get live matches with events."""

        response = requests.get(
            f"{self.BASE_URL}/fixtures",
            headers=self.headers,
            params={"live": "all"},
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        matches = []

        for fixture in data.get("response", []):
            teams = fixture.get("teams", {})
            home = teams.get("home", {})
            away = teams.get("away", {})
            goals = fixture.get("goals", {})
            fixture_data = fixture.get(
                "fixture",
                {},
            )

            matches.append(
                {
                    "provider": "api_football",
                    "match_id": str(
                        fixture_data.get("id", "")
                    ),
                    "home_team_id": home.get("id"),
                    "home_team": home.get(
                        "name",
                        "",
                    ),
                    "away_team_id": away.get(
                        "id"
                    ),
                    "away_team": away.get(
                        "name",
                        "",
                    ),
                    "home_score": goals.get("home"),
                    "away_score": goals.get("away"),
                    "status": self._normalize_status(
                        fixture_data.get(
                            "status",
                            {},
                        ).get("short")
                    ),
                    "time": fixture_data.get(
                        "date"
                    ),
                    "url": "",
                    "events": [],
                }
            )

        if not matches:
            return matches

        events_by_match = self._get_events(
            [
                match["match_id"]
                for match in matches
            ]
        )

        for match in matches:
            match["events"] = events_by_match.get(
                match["match_id"],
                [],
            )

        return matches

    def _get_events(
        self,
        match_ids: list[str],
    ) -> dict[str, list[dict]]:
        """Get events for multiple fixtures."""

        if not match_ids:
            return {}

        response = requests.get(
            f"{self.BASE_URL}/fixtures",
            headers=self.headers,
            params={
                "ids": "-".join(match_ids[:20]),
            },
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        events_by_match = {}

        for fixture in data.get("response", []):
            fixture_data = fixture.get(
                "fixture",
                {}
            )

            match_id = str(
                fixture_data.get("id", "")
            )

            events_by_match[match_id] = (
                self._parse_events(
                    fixture.get("events", [])
                )
            )

        return events_by_match

    @staticmethod
    def _parse_events(
        events: list[dict],
    ) -> list[dict]:
        """Parse API-Football events."""

        parsed_events = []

        for event in events:
            event_type = event.get("type")
            detail = event.get("detail")

            if event_type == "Goal":
                if detail in {
                    "Normal Goal",
                    "Penalty",
                    "Own Goal",
                }:
                    normalized_type = "goal"
                else:
                    continue

            elif event_type == "Card":
                if detail in {
                    "Red Card",
                    "Yellow-Red Card",
                }:
                    normalized_type = "red_card"
                else:
                    continue

            else:
                continue

            time_data = event.get(
                "time",
                {},
            )

            minute = time_data.get("elapsed")

            extra = time_data.get("extra")

            if minute is None:
                minute_text = ""
            elif extra:
                minute_text = (
                    f"{minute}+{extra}"
                )
            else:
                minute_text = str(minute)

            player = event.get(
                "player",
                {}
            ).get("name")

            parsed_events.append(
                {
                    "minute": minute_text,
                    "type": normalized_type,
                    "player": player,
                }
            )

        return parsed_events

    @staticmethod
    def _normalize_status(
        status: str | None,
    ) -> str:
        """Normalize API-Football match status."""

        if status in {
            "1H",
            "HT",
            "2H",
            "ET",
            "BT",
            "P",
        }:
            return "live"

        if status in {
            "FT",
            "AET",
            "PEN",
        }:
            return "finished"

        return "scheduled"
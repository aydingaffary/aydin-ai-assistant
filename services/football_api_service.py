"""Football API service."""

import requests

from config import FOOTBALL_API_KEY


class FootballAPIService:
    """Communicate with football API."""

    BASE_URL = "https://v3.football.api-sports.io"

    def __init__(self) -> None:
        self.api_key = FOOTBALL_API_KEY

        if not self.api_key:
            raise ValueError("FOOTBALL_API_KEY is not set.")

        self.headers = {
            "x-apisports-key": self.api_key,
        }

    def get_live_matches(self):
        """Get live football matches."""

        response = requests.get(
            f"{self.BASE_URL}/fixtures",
            headers=self.headers,
            params={
                "live": "all",
            },
            timeout=10,
        )

        response.raise_for_status()

        return response.json()
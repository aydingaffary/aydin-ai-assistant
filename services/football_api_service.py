"""Football API service."""

import os
import requests


class FootballAPIService:
    """Communicate with football API."""

    BASE_URL = "https://v3.football.api-sports.io"

    def __init__(self):
        self.api_key = os.getenv("FOOTBALL_API_KEY")

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
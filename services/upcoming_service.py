"""Upcoming movies and TV service using XMDb API."""

from datetime import date, timedelta

import requests

from config import XMDB_API_KEY


class UpcomingService:
    """Fetch upcoming movies and TV shows."""

    BASE_URL = "https://xmdbapi.com/api/v1/upcoming"

    def get_upcoming(
        self,
        content_type: str = "movie",
        days: int = 30,
    ) -> list[dict]:
        """Return upcoming content."""

        start = date.today()
        end = start + timedelta(days=days)

        response = requests.get(
            f"{self.BASE_URL}/{content_type}",
            headers={
                "x-api-key": XMDB_API_KEY,
            },
            params={
                "start": start.isoformat(),
                "end": end.isoformat(),
                "region": "US",
                "first": 10,
            },
            timeout=15,
        )

        response.raise_for_status()

        results = response.json().get("results", [])

        items = []

        for item in results:
            release_date = item.get("release_date")

            if not release_date:
                continue

            items.append(
                {
                    "title": item.get("title", "Unknown"),
                    "date": release_date,
                    "rating": item.get("rating"),
                    "imdb_url": item.get("imdb_url"),
                    "type": content_type,
                }
            )

        items.sort(
            key=lambda x: x["date"]
        )

        return items

    def get_movies(self, days: int = 30) -> list[dict]:
        """Return upcoming movies."""
        return self.get_upcoming(
            content_type="movie",
            days=days,
        )

    def get_tv(self, days: int = 30) -> list[dict]:
        """Return upcoming TV shows."""
        return self.get_upcoming(
            content_type="tv",
            days=days,
        )
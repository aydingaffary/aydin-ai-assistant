"""Movie release service using TMDB API."""

from datetime import date, timedelta

import requests

from config import TMDB_API_KEY


class ReleaseService:
    """Fetch upcoming US movie releases."""

    BASE_URL = "https://api.themoviedb.org/3"

    def get_releases(
        self,
        start_date: date,
        days: int = 7,
    ) -> list[dict]:
        """Return movies released in US during date range."""

        if not TMDB_API_KEY:
            return []

        end_date = start_date + timedelta(
            days=days - 1
        )

        response = requests.get(
            f"{self.BASE_URL}/discover/movie",
            params={
                "api_key": TMDB_API_KEY,
                "region": "US",
                "primary_release_date.gte": (
                    start_date.isoformat()
                ),
                "primary_release_date.lte": (
                    end_date.isoformat()
                ),
                "sort_by": (
                    "primary_release_date.asc"
                ),
            },
            timeout=15,
        )

        response.raise_for_status()

        results = response.json().get(
            "results",
            []
        )

        return [
            {
                "title": movie["title"],
                "release_date": date.fromisoformat(
                    movie["release_date"]
                ),
                "type": "movie",
                "url": (
                    "https://www.themoviedb.org/movie/"
                    f"{movie['id']}"
                ),
            }
            for movie in results
            if movie.get("release_date")
        ]
"""Movie service using OMDb API."""

import requests

from config import OMDB_API_KEY


class ReleaseService:
    """Fetch movie information from OMDb."""

    BASE_URL = "https://www.omdbapi.com/"

    def get_movie(self, title: str) -> dict | None:
        """Return movie information by title."""

        if not OMDB_API_KEY:
            return None

        response = requests.get(
            self.BASE_URL,
            params={
                "apikey": OMDB_API_KEY,
                "t": title,
                "plot": "full",
            },
            timeout=15,
        )

        response.raise_for_status()

        data = response.json()

        if data.get("Response") != "True":
            return None

        return {
            "title": data.get("Title"),
            "year": data.get("Year"),
            "genre": data.get("Genre"),
            "director": data.get("Director"),
            "actors": data.get("Actors"),
            "plot": data.get("Plot"),
            "imdb_rating": data.get("imdbRating"),
            "imdb_votes": data.get("imdbVotes"),
            "poster": data.get("Poster"),
            "imdb_id": data.get("imdbID"),
            "type": data.get("Type"),
        }
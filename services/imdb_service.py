"""IMDb release calendar service."""

from datetime import date, datetime

import requests
from bs4 import BeautifulSoup


class IMDbService:
    BASE_URL = "https://www.imdb.com/calendar/"

    def get_releases(
        self,
        start_date: date,
        days: int = 7,
    ) -> list[dict]:
        """Get IMDb US releases for the requested date range."""

        end_date = start_date.fromordinal(
            start_date.toordinal() + days - 1
        )

        releases = []

        for release_type in ("movie", "tv"):
            url = self._build_url(release_type)

            response = requests.get(
                url,
                headers=self._headers(),
                timeout=15,
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            releases.extend(
                self._parse_releases(
                    soup,
                    start_date,
                    end_date,
                    release_type,
                )
            )

        return self._remove_duplicates(releases)

    def _build_url(self, release_type: str) -> str:
        """Build IMDb US calendar URL."""

        if release_type == "tv":
            return f"{self.BASE_URL}?region=US&type=TV"

        return f"{self.BASE_URL}?region=US"

    @staticmethod
    def _headers() -> dict[str, str]:
        return {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "Chrome/154.0.0.0 Safari/537.36"
            )
        }

    def _parse_releases(
        self,
        soup: BeautifulSoup,
        start_date: date,
        end_date: date,
        release_type: str,
    ) -> list[dict]:
        """Parse releases grouped by IMDb release date."""

        releases = []

        current_date = None

        for element in soup.find_all(["h4", "a"]):
            text = element.get_text(" ", strip=True)

            parsed_date = self._parse_date(text)

            if parsed_date is not None:
                current_date = parsed_date
                continue

            if current_date is None:
                continue

            if not start_date <= current_date <= end_date:
                continue

            if element.name != "a":
                continue

            href = element.get("href")

            if not href or "/title/tt" not in href:
                continue

            title = text.strip()

            if not title:
                continue

            if href.startswith("/"):
                href = f"https://www.imdb.com{href}"

            releases.append(
                {
                    "title": title,
                    "url": href,
                    "release_date": current_date,
                    "type": release_type,
                }
            )

        return releases

    @staticmethod
    def _parse_date(text: str) -> date | None:
        """Parse IMDb date heading."""

        try:
            return datetime.strptime(
                text,
                "%b %d, %Y",
            ).date()
        except ValueError:
            return None

    @staticmethod
    def _remove_duplicates(
        releases: list[dict],
    ) -> list[dict]:
        """Remove duplicate IMDb titles."""

        unique = {}

        for release in releases:
            key = (
                release["url"],
                release["release_date"],
            )

            unique[key] = release

        return list(unique.values())
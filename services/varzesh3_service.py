"""Varzesh3 football provider."""

import logging
import re

import requests
from bs4 import BeautifulSoup

from services.football_provider import FootballProvider


logger = logging.getLogger(__name__)


class Varzesh3Provider(FootballProvider):
    """Provide football data using Varzesh3."""

    BASE_URL = "https://www.varzesh3.com"

    EVENT_TYPES = {
        "تعویض": "substitution",
        "کارت زرد": "yellow_card",
        "کارت قرمز": "red_card",
        "گل": "goal",
        "گل به خودی": "own_goal",
        "گل پنالتی": "penalty_goal",
    }

    def get_live_matches(self) -> list[dict]:
        """Get live football matches from Varzesh3."""

        response = requests.get(
            f"{self.BASE_URL}/livescore",
            timeout=10,
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        matches = []

        for link in soup.select(
            'a[href*="/football/match/"]'
        ):
            match = self._parse_match_link(link)

            if match is None:
                continue

            if match["status"] != "live":
                continue

            matches.append(match)

        logger.info(
            "Varzesh3 returned %d live matches.",
            len(matches),
        )

        return matches

    def _parse_match_link(
        self,
        link,
    ) -> dict | None:
        """Parse a football match card."""

        href = link.get("href")

        if not href:
            return None

        match_id = self._extract_match_id(href)

        if match_id is None:
            return None

        card = link.parent

        if card is None:
            return None

        time_element = card.find("time")

        if time_element is None:
            return None

        match_time = time_element.get_text(
            " ",
            strip=True,
        )

        status_element = card.find(
            string=lambda text: (
                text
                and "نتیجه نهایی" in text
            )
        )

        is_finished = status_element is not None

        teams = self._parse_teams(link)

        if teams is None:
            return None

        home_team, away_team = teams

        score = self._parse_score(link)

        if is_finished:
            status = "finished"
        elif score is not None:
            status = "live"
        else:
            status = "scheduled"

        return {
            "provider": "varzesh3",
            "match_id": match_id,
            "home_team": home_team,
            "away_team": away_team,
            "home_score": (
                score[0]
                if score
                else None
            ),
            "away_score": (
                score[1]
                if score
                else None
            ),
            "status": status,
            "time": match_time,
            "url": f"{self.BASE_URL}{href}",
            "events": [],
        }

    @staticmethod
    def _extract_match_id(
        href: str,
    ) -> str | None:
        """Extract match ID from URL."""

        match = re.search(
            r"/football/match/(\d+)",
            href,
        )

        if not match:
            return None

        return match.group(1)

    @staticmethod
    def _parse_teams(
        link,
    ) -> tuple[str, str] | None:
        """Extract home and away team names."""

        team_images = link.find_all(
            "img",
            alt=True,
        )

        team_names = [
            image.get("alt", "").strip()
            for image in team_images
            if image.get("alt", "").strip()
        ]

        if len(team_names) != 2:
            return None

        return team_names[0], team_names[1]

    @staticmethod
    def _parse_score(
        link,
    ) -> tuple[int, int] | None:
        """Extract score from a match link."""

        score_spans = link.find_all("span")

        scores = []

        for span in score_spans:
            text = span.get_text(
                " ",
                strip=True,
            )

            if text.isdigit():
                scores.append(int(text))

        if len(scores) < 2:
            return None

        return scores[0], scores[1]

    def _parse_events(
        self,
        soup,
    ) -> list[dict]:
        """Parse match events from a Varzesh3 match page."""

        events = []

        for image in soup.find_all(
            "img",
            alt=True,
        ):
            event_type = self.EVENT_TYPES.get(
                image.get("alt", "").strip()
            )

            if event_type is None:
                continue

            event_container = image.find_parent(
                "div",
                style=True,
            )

            if event_container is None:
                continue

            minute_element = event_container.find(
                "span"
            )

            if minute_element is None:
                continue

            minute = minute_element.get_text(
                " ",
                strip=True,
            ).replace("'", "")

            text_elements = event_container.find_all(
                "span"
            )

            texts = [
                element.get_text(
                    " ",
                    strip=True,
                )
                for element in text_elements
                if element.get_text(
                    " ",
                    strip=True,
                )
            ]

            player = None

            if event_type in {
                "yellow_card",
                "red_card",
            }:
                if len(texts) >= 2:
                    player = texts[-1]

            elif event_type in {
                "goal",
                "penalty_goal",
                "own_goal",
            }:
                candidates = []

                for text in texts:
                    if not text:
                        continue

                    if text == "-":
                        continue

                    if text == minute_element.get_text(
                        " ",
                        strip=True,
                    ):
                        continue

                    if text in {
                        "گل",
                        "گل پنالتی",
                        "گل به خودی",
                    }:
                        continue

                    if re.fullmatch(
                        r"\d+\s*-\s*\d+",
                        text,
                    ):
                        continue

                    if text.isdigit():
                        continue

                    candidates.append(text)

                if candidates:
                    player = candidates[-1]

            elif event_type == "substitution":
                if len(texts) >= 3:
                    player = texts[-2]

            events.append(
                {
                    "minute": minute,
                    "type": event_type,
                    "player": player,
                }
            )

        return events
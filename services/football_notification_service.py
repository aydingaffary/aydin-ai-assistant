"""Football notification service."""

from services.football_event_detector import DetectedEvent
from services.football_normalizer import NormalizedMatch


class FootballNotificationService:
    """Build Telegram-ready notifications for football events."""

    def build_message(
        self,
        event: DetectedEvent,
        match: NormalizedMatch,
    ) -> str | None:
        """Build a notification message."""

        if event.type == "goal":
            return self._build_goal_message(
                event,
                match,
            )

        if event.type == "red_card":
            return self._build_red_card_message(
                event,
                match,
            )

        if event.type == "match_started":
            return self._build_started_message(
                match,
            )

        if event.type == "match_finished":
            return self._build_finished_message(
                match,
            )

        return None

    @staticmethod
    def _build_goal_message(
        event: DetectedEvent,
        match: NormalizedMatch,
    ) -> str:
        """Build goal notification."""

        player = event.player or "Unknown player"

        return (
            f"⚽ GOAL!\n"
            f"{match.home_team} "
            f"{match.home_score} - "
            f"{match.away_score} "
            f"{match.away_team}\n"
            f"⏱ {event.minute}'\n"
            f"👤 {player}"
        )

    @staticmethod
    def _build_red_card_message(
        event: DetectedEvent,
        match: NormalizedMatch,
    ) -> str:
        """Build red-card notification."""

        player = event.player or "Unknown player"

        return (
            f"🔴 RED CARD\n"
            f"{match.home_team} "
            f"{match.home_score} - "
            f"{match.away_score} "
            f"{match.away_team}\n"
            f"⏱ {event.minute}'\n"
            f"👤 {player}"
        )

    @staticmethod
    def _build_started_message(
        match: NormalizedMatch,
    ) -> str:
        """Build match-start notification."""

        return f"🏁 MATCH STARTED\n" f"{match.home_team} vs " f"{match.away_team}"

    @staticmethod
    def _build_finished_message(
        match: NormalizedMatch,
    ) -> str:
        """Build match-finished notification."""

        return (
            f"🏁 MATCH FINISHED\n"
            f"{match.home_team} "
            f"{match.home_score} - "
            f"{match.away_score} "
            f"{match.away_team}"
        )

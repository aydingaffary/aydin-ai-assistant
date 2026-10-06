"""Football match monitoring."""

from services.football_event_detector import (
    DetectedEvent,
    FootballEventDetector,
)
from services.football_normalizer import (
    FootballNormalizer,
)
from database.football_state import (
    FootballStateRepository,
)


class FootballMonitor:
    """Monitor football matches for new events."""

    def __init__(
        self,
        provider_manager,
        state_repository=None,
        event_detector=None,
    ):
        self.provider_manager = provider_manager

        self.state_repository = (
            state_repository
            or FootballStateRepository()
        )

        self.event_detector = (
            event_detector
            or FootballEventDetector()
        )

    def check(self) -> list[DetectedEvent]:
        """Check live matches and detect new events."""

        matches = (
            self.provider_manager.get_live_matches()
        )

        detected_events = []

        for raw_match in matches:
            current = (
                FootballNormalizer.normalize_match(
                    raw_match
                )
            )

            previous_state = (
                self.state_repository.get(
                    current.match_id
                )
            )

            previous = None

            if previous_state is not None:
                previous = (
                    FootballNormalizer.normalize_match(
                        previous_state
                    )
                )

            events = self.event_detector.detect(
                previous,
                current,
            )

            detected_events.extend(events)

            self.state_repository.save(
                current.match_id,
                {
                    "match_id": current.match_id,
                    "home_team_id": current.home_team_id,
                    "home_team": current.home_team,
                    "away_team_id": current.away_team_id,
                    "away_team": current.away_team,
                    "home_score": current.home_score,
                    "away_score": current.away_score,
                    "status": current.status,
                    "events": [
                        {
                            "minute": event.minute,
                            "type": event.type,
                            "player": event.player,
                        }
                        for event in current.events
                    ],
                },
            )

        return detected_events
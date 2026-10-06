"""Football notification pipeline."""

from dataclasses import dataclass

from services.football_event_detector import (
    DetectedEvent,
)
from services.football_monitor import (
    FootballMonitor,
)
from services.football_notification_service import (
    FootballNotificationService,
)
from services.football_normalizer import (
    NormalizedMatch,
    FootballNormalizer,
)


@dataclass
class FootballNotification:
    """A football event with its notification message."""

    event: DetectedEvent
    match: NormalizedMatch
    message: str


class FootballNotificationPipeline:
    """Detect football events and build notifications."""

    def __init__(
        self,
        monitor: FootballMonitor,
        notification_service: FootballNotificationService | None = None,
    ):
        self.monitor = monitor
        self.notification_service = (
            notification_service or FootballNotificationService()
        )

    def check(self) -> list[FootballNotification]:
        """Check matches and build notifications."""

        matches = self.monitor.provider_manager.get_live_matches()

        notifications = []

        for raw_match in matches:
            current = FootballNormalizer.normalize_match(raw_match)

            previous_state = self.monitor.state_repository.get(current.match_id)

            previous = None

            if previous_state is not None:
                previous = FootballNormalizer.normalize_match(previous_state)

            events = self.monitor.event_detector.detect(
                previous,
                current,
            )

            self.monitor.state_repository.save(
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

            for event in events:
                message = self.notification_service.build_message(
                    event,
                    current,
                )

                if message is None:
                    continue

                notifications.append(
                    FootballNotification(
                        event=event,
                        match=current,
                        message=message,
                    )
                )

        return notifications

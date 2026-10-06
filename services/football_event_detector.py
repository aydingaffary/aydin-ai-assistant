"""Detect football events from match state changes."""

from dataclasses import dataclass

from services.football_normalizer import NormalizedMatch


@dataclass
class DetectedEvent:
    """A detected football notification event."""

    type: str
    match_id: str
    minute: str | None = None
    player: str | None = None


class FootballEventDetector:
    """Detect meaningful changes between match states."""

    def detect(
        self,
        previous: NormalizedMatch | None,
        current: NormalizedMatch,
    ) -> list[DetectedEvent]:
        """Detect notification-worthy events."""

        if previous is None:
            return []

        events = []

        if (
            previous.status != "live"
            and current.status == "live"
        ):
            events.append(
                DetectedEvent(
                    type="match_started",
                    match_id=current.match_id,
                )
            )

        if (
            previous.status == "live"
            and current.status == "finished"
        ):
            events.append(
                DetectedEvent(
                    type="match_finished",
                    match_id=current.match_id,
                )
            )

        events.extend(
            self._detect_new_events(
                previous,
                current,
            )
        )

        return events

    @staticmethod
    def _detect_new_events(
        previous: NormalizedMatch,
        current: NormalizedMatch,
    ) -> list[DetectedEvent]:
        """Detect new goal and red-card events."""

        previous_events = {
            (
                event.minute,
                event.type,
                event.player,
            )
            for event in previous.events
        }

        detected = []

        for event in current.events:
            identity = (
                event.minute,
                event.type,
                event.player,
            )

            if identity in previous_events:
                continue

            if event.type not in {
                "goal",
                "red_card",
            }:
                continue

            detected.append(
                DetectedEvent(
                    type=event.type,
                    match_id=current.match_id,
                    minute=event.minute,
                    player=event.player,
                )
            )

        return detected
"""Route football notifications to subscribed users."""

from dataclasses import dataclass

from services.football_notification_pipeline import (
    FootballNotification,
)
from services.team_service import TeamService


@dataclass
class RoutedFootballNotification:
    """A football notification ready for delivery to a user."""

    user_id: int
    message: str


class FootballNotificationRouter:
    """Find users who should receive football notifications."""

    def __init__(
        self,
        team_service=None,
    ):
        self.team_service = team_service or TeamService()

    def route(
        self,
        notification: FootballNotification,
    ) -> list[RoutedFootballNotification]:
        """Route a notification to subscribed users."""

        team_ids = self._get_team_ids(notification)

        user_ids = set()

        for team_id in team_ids:
            subscribers = self.team_service.get_subscribers(team_id)

            user_ids.update(subscribers)

        return [
            RoutedFootballNotification(
                user_id=user_id,
                message=notification.message,
            )
            for user_id in sorted(user_ids)
        ]

    @staticmethod
    def _get_team_ids(
        notification: FootballNotification,
    ) -> list[int]:
        """Get team IDs related to the match."""

        team_ids = []

        if notification.match.home_team_id is not None:
            team_ids.append(notification.match.home_team_id)

        if notification.match.away_team_id is not None:
            team_ids.append(notification.match.away_team_id)

        return team_ids

from services.football_event_detector import (
    DetectedEvent,
)
from services.football_notification_pipeline import (
    FootballNotification,
)
from services.football_notification_router import (
    FootballNotificationRouter,
)
from services.football_normalizer import (
    NormalizedMatch,
)


class FakeSubscriptionRepository:
    def __init__(self):
        self.subscribers = {}

    def get_subscribers(self, team_id):
        return self.subscribers.get(
            team_id,
            [],
        )


def create_notification(
    home_team,
    away_team,
):
    match = NormalizedMatch(
        match_id="router-123",
        home_team_id=home_team,
        home_team=f"Team {home_team}",
        away_team_id=away_team,
        away_team=f"Team {away_team}",
        home_score=2,
        away_score=1,
        status="live",
        events=[],
    )

    event = DetectedEvent(
        type="goal",
        match_id="router-123",
        minute="70",
        player="Player A",
    )

    return FootballNotification(
        event=event,
        match=match,
        message="⚽ GOAL!",
    )


def test_route_to_home_team_subscribers():
    repository = FakeSubscriptionRepository()

    repository.subscribers[10] = [
        1001,
        1002,
    ]

    router = FootballNotificationRouter(
        subscription_repository=repository,
    )

    notification = create_notification(
        10,
        20,
    )

    routed = router.route(notification)

    assert [
        item.user_id
        for item in routed
    ] == [1001, 1002]

    assert all(
        item.message == "⚽ GOAL!"
        for item in routed
    )


def test_route_to_away_team_subscribers():
    repository = FakeSubscriptionRepository()

    repository.subscribers[20] = [
        2001,
        2002,
    ]

    router = FootballNotificationRouter(
        subscription_repository=repository,
    )

    notification = create_notification(
        10,
        20,
    )

    routed = router.route(notification)

    assert [
        item.user_id
        for item in routed
    ] == [2001, 2002]


def test_user_subscribed_to_both_teams_receives_one_message():
    repository = FakeSubscriptionRepository()

    repository.subscribers[10] = [
        3001,
        3002,
    ]

    repository.subscribers[20] = [
        3001,
        3003,
    ]

    router = FootballNotificationRouter(
        subscription_repository=repository,
    )

    notification = create_notification(
        10,
        20,
    )

    routed = router.route(notification)

    assert [
        item.user_id
        for item in routed
    ] == [
        3001,
        3002,
        3003,
    ]


def test_no_subscribers_returns_empty_list():
    repository = FakeSubscriptionRepository()

    router = FootballNotificationRouter(
        subscription_repository=repository,
    )

    notification = create_notification(
        10,
        20,
    )

    routed = router.route(notification)

    assert routed == []
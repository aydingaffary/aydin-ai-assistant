from services.football_event_detector import (
    DetectedEvent,
)
from services.football_notification_service import (
    FootballNotificationService,
)
from services.football_normalizer import (
    NormalizedMatch,
)


def create_match():
    return NormalizedMatch(
        match_id="123",
        home_team_id=10,
        home_team="Team A",
        away_team_id=20,
        away_team="Team B",
        home_score=2,
        away_score=1,
        status="live",
        events=[],
    )


def test_goal_notification():
    service = FootballNotificationService()

    event = DetectedEvent(
        type="goal",
        match_id="123",
        minute="70",
        player="Player A",
    )

    message = service.build_message(
        event,
        create_match(),
    )

    assert "⚽ GOAL!" in message
    assert "Team A 2 - 1 Team B" in message
    assert "70'" in message
    assert "Player A" in message


def test_red_card_notification():
    service = FootballNotificationService()

    event = DetectedEvent(
        type="red_card",
        match_id="123",
        minute="82",
        player="Player B",
    )

    message = service.build_message(
        event,
        create_match(),
    )

    assert "🔴 RED CARD" in message
    assert "82'" in message
    assert "Player B" in message


def test_match_started_notification():
    service = FootballNotificationService()

    event = DetectedEvent(
        type="match_started",
        match_id="123",
    )

    message = service.build_message(
        event,
        create_match(),
    )

    assert "🏁 MATCH STARTED" in message
    assert "Team A vs Team B" in message


def test_match_finished_notification():
    service = FootballNotificationService()

    event = DetectedEvent(
        type="match_finished",
        match_id="123",
    )

    message = service.build_message(
        event,
        create_match(),
    )

    assert "🏁 MATCH FINISHED" in message
    assert "Team A 2 - 1 Team B" in message


def test_yellow_card_has_no_notification():
    service = FootballNotificationService()

    event = DetectedEvent(
        type="yellow_card",
        match_id="123",
        minute="30",
        player="Player A",
    )

    message = service.build_message(
        event,
        create_match(),
    )

    assert message is None


def test_substitution_has_no_notification():
    service = FootballNotificationService()

    event = DetectedEvent(
        type="substitution",
        match_id="123",
        minute="60",
        player="Player A",
    )

    message = service.build_message(
        event,
        create_match(),
    )

    assert message is None

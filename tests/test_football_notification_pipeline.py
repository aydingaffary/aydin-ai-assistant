from services.football_monitor import (
    FootballMonitor,
)
from services.football_notification_pipeline import (
    FootballNotificationPipeline,
)


class FakeProviderManager:
    def __init__(self, matches):
        self.matches = matches

    def get_live_matches(self):
        return self.matches


class FakeStateRepository:
    def __init__(self):
        self.states = {}

    def get(self, match_id):
        return self.states.get(match_id)

    def save(self, match_id, state):
        self.states[match_id] = state


def test_pipeline_builds_goal_notification():
    match = {
        "match_id": "pipeline-123",
        "home_team": "Team A",
        "away_team": "Team B",
        "home_score": 1,
        "away_score": 0,
        "status": "live",
        "events": [
            {
                "minute": "50",
                "type": "goal",
                "player": "Player A",
            }
        ],
    }

    provider_manager = FakeProviderManager([match])

    repository = FakeStateRepository()

    monitor = FootballMonitor(
        provider_manager=provider_manager,
        state_repository=repository,
    )

    pipeline = FootballNotificationPipeline(
        monitor=monitor,
    )

    # Establish initial state.
    assert pipeline.check() == []

    # New goal.
    match["home_score"] = 2

    match["events"].append(
        {
            "minute": "75",
            "type": "goal",
            "player": "Player B",
        }
    )

    notifications = pipeline.check()

    assert len(notifications) == 1

    notification = notifications[0]

    assert notification.event.type == "goal"
    assert notification.event.player == "Player B"
    assert notification.match.home_score == 2
    assert "⚽ GOAL!" in notification.message
    assert "Player B" in notification.message


def test_pipeline_does_not_duplicate_goal():
    match = {
        "match_id": "pipeline-456",
        "home_team": "Team A",
        "away_team": "Team B",
        "home_score": 1,
        "away_score": 0,
        "status": "live",
        "events": [
            {
                "minute": "40",
                "type": "goal",
                "player": "Player A",
            }
        ],
    }

    provider_manager = FakeProviderManager([match])

    repository = FakeStateRepository()

    monitor = FootballMonitor(
        provider_manager=provider_manager,
        state_repository=repository,
    )

    pipeline = FootballNotificationPipeline(
        monitor=monitor,
    )

    assert pipeline.check() == []

    match["home_score"] = 2

    match["events"].append(
        {
            "minute": "65",
            "type": "goal",
            "player": "Player B",
        }
    )

    first_notifications = pipeline.check()

    assert len(first_notifications) == 1

    second_notifications = pipeline.check()

    assert second_notifications == []


def test_pipeline_ignores_yellow_card():
    match = {
        "match_id": "pipeline-789",
        "home_team": "Team A",
        "away_team": "Team B",
        "home_score": 0,
        "away_score": 0,
        "status": "live",
        "events": [
            {
                "minute": "30",
                "type": "yellow_card",
                "player": "Player A",
            }
        ],
    }

    provider_manager = FakeProviderManager([match])

    repository = FakeStateRepository()

    monitor = FootballMonitor(
        provider_manager=provider_manager,
        state_repository=repository,
    )

    pipeline = FootballNotificationPipeline(
        monitor=monitor,
    )

    assert pipeline.check() == []

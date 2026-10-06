from services.football_monitor import (
    FootballMonitor,
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


def test_monitor_detects_new_goal():
    provider_manager = FakeProviderManager(
        [
            {
                "match_id": "123",
                "home_team": "Team A",
                "away_team": "Team B",
                "home_score": 1,
                "away_score": 0,
                "status": "live",
                "events": [
                    {
                        "minute": "55",
                        "type": "goal",
                        "player": "Player A",
                    }
                ],
            }
        ]
    )

    repository = FakeStateRepository()

    monitor = FootballMonitor(
        provider_manager=provider_manager,
        state_repository=repository,
    )

    # First check establishes the state.
    events = monitor.check()

    assert events == []

    # Simulate a new goal.
    provider_manager.matches[0]["home_score"] = 2
    provider_manager.matches[0]["events"].append(
        {
            "minute": "70",
            "type": "goal",
            "player": "Player B",
        }
    )

    events = monitor.check()

    assert len(events) == 1
    assert events[0].type == "goal"
    assert events[0].player == "Player B"


def test_monitor_does_not_duplicate_events():
    match = {
        "match_id": "456",
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

    provider_manager = FakeProviderManager(
        [match]
    )

    repository = FakeStateRepository()

    monitor = FootballMonitor(
        provider_manager=provider_manager,
        state_repository=repository,
    )

    assert monitor.check() == []
    assert monitor.check() == []
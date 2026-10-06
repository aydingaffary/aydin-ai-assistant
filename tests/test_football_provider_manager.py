from services.football_provider_manager import (
    FootballProviderManager,
)


class SuccessfulProvider:
    def get_live_matches(self):
        return [
            {
                "match_id": "match-1",
            }
        ]


class EmptyProvider:
    def get_live_matches(self):
        return []


class FailingProvider:
    def get_live_matches(self):
        raise RuntimeError("Provider unavailable")


def test_manager_uses_first_successful_provider():
    manager = FootballProviderManager(
        providers=[
            SuccessfulProvider(),
        ]
    )

    matches = manager.get_live_matches()

    assert matches == [
        {
            "match_id": "match-1",
        }
    ]


def test_manager_falls_back_when_first_provider_is_empty():
    manager = FootballProviderManager(
        providers=[
            EmptyProvider(),
            SuccessfulProvider(),
        ]
    )

    matches = manager.get_live_matches()

    assert matches == [
        {
            "match_id": "match-1",
        }
    ]


def test_manager_falls_back_when_first_provider_fails():
    manager = FootballProviderManager(
        providers=[
            FailingProvider(),
            SuccessfulProvider(),
        ]
    )

    matches = manager.get_live_matches()

    assert matches == [
        {
            "match_id": "match-1",
        }
    ]


def test_manager_returns_empty_when_all_providers_fail():
    manager = FootballProviderManager(
        providers=[
            FailingProvider(),
            EmptyProvider(),
        ]
    )

    matches = manager.get_live_matches()

    assert matches == []

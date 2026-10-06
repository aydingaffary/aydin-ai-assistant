from services.football_provider_manager import FootballProviderManager


class FakeProvider:
    def __init__(self, matches=None, error=None):
        self.matches = matches or []
        self.error = error

    def get_live_matches(self):
        if self.error:
            raise self.error

        return self.matches


def test_manager_returns_matches_from_first_provider():
    provider = FakeProvider(
        matches=[{"id": 1}]
    )

    manager = FootballProviderManager(
        providers=[provider]
    )

    matches = manager.get_live_matches()

    assert matches == [{"id": 1}]


def test_manager_uses_fallback_provider():
    failing_provider = FakeProvider(
        error=RuntimeError("Provider failed")
    )

    fallback_provider = FakeProvider(
        matches=[{"id": 2}]
    )

    manager = FootballProviderManager(
        providers=[
            failing_provider,
            fallback_provider,
        ]
    )

    matches = manager.get_live_matches()

    assert matches == [{"id": 2}]


def test_manager_returns_empty_when_all_providers_fail():
    provider_one = FakeProvider(
        error=RuntimeError("Provider one failed")
    )

    provider_two = FakeProvider(
        error=RuntimeError("Provider two failed")
    )

    manager = FootballProviderManager(
        providers=[
            provider_one,
            provider_two,
        ]
    )

    matches = manager.get_live_matches()

    assert matches == []
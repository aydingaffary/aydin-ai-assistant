"""Tests for AI provider routing and fallback behavior."""

from ai_router import AIRouter


class FakeProvider:
    """Simulate an AI provider for isolated router tests."""

    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error

    def generate_response(self, prompt):
        """Return a fake response or raise a configured error."""
        del prompt
        if self.error:
            raise self.error
        return self.result


def test_ai_router_initializes():
    """Verify that the router exposes its ask method."""
    router = AIRouter()
    assert router is not None
    assert hasattr(router, "ask")


def test_router_returns_response_from_first_successful_provider():
    """Return the first successful provider's response."""
    router = AIRouter()
    router.providers = [
        FakeProvider(result="پاسخ آزمایشی"),
        FakeProvider(result="نباید اجرا شود"),
    ]

    assert router.ask("سلام") == "پاسخ آزمایشی"
    assert router.last_provider == "FakeProvider"


def test_router_falls_back_when_provider_fails():
    """Try the next provider after a provider raises an error."""
    router = AIRouter()
    router.providers = [
        FakeProvider(error=RuntimeError("provider failed")),
        FakeProvider(result="پاسخ جایگزین"),
    ]

    assert router.ask("سلام") == "پاسخ جایگزین"


def test_router_returns_unavailable_message_when_all_providers_fail():
    """Return the unavailable message when all providers fail."""
    router = AIRouter()
    router.providers = [
        FakeProvider(error=RuntimeError("provider failed")),
        FakeProvider(error=RuntimeError("another failure")),
    ]

    assert router.ask("سلام") == "❌ هیچ سرویس هوش مصنوعی در دسترس نیست."


def test_router_handles_empty_provider_list():
    """Return the unavailable message when no providers exist."""
    router = AIRouter()
    router.providers = []

    assert router.ask("سلام") == "❌ هیچ سرویس هوش مصنوعی در دسترس نیست."

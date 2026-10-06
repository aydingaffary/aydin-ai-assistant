from ai_router import AIRouter


def test_ai_router_initializes():
    """AI router should initialize successfully."""

    router = AIRouter()

    assert router is not None
    assert hasattr(router, "ask")
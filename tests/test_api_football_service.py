from services.api_football_service import (
    APIFootballProvider,
)


def test_get_live_matches_normalizes_api_football_response(
    monkeypatch,
):
    provider = object.__new__(
        APIFootballProvider
    )

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "response": [
                    {
                        "fixture": {
                            "id": 12345,
                            "date": "2026-10-06T18:00:00+00:00",
                            "status": {
                                "short": "2H"
                            },
                        },
                        "teams": {
                            "home": {
                                "id": 529,
                                "name": "Barcelona",
                            },
                            "away": {
                                "id": 541,
                                "name": "Real Madrid",
                            },
                        },
                        "goals": {
                            "home": 2,
                            "away": 1,
                        },
                    }
                ]
            }

    def fake_get(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(
        "services.api_football_service.requests.get",
        fake_get,
    )

    provider.headers = {
        "x-apisports-key": "test-key"
    }

    matches = provider.get_live_matches()

    assert len(matches) == 1

    match = matches[0]

    assert match["match_id"] == "12345"

    assert match["home_team_id"] == 529
    assert match["home_team"] == "Barcelona"

    assert match["away_team_id"] == 541
    assert match["away_team"] == "Real Madrid"

    assert match["home_score"] == 2
    assert match["away_score"] == 1

    assert match["status"] == "live"
def test_normalize_status():
    assert (
        APIFootballProvider._normalize_status("1H")
        == "live"
    )

    assert (
        APIFootballProvider._normalize_status("2H")
        == "live"
    )

    assert (
        APIFootballProvider._normalize_status("HT")
        == "live"
    )

    assert (
        APIFootballProvider._normalize_status("FT")
        == "finished"
    )

    assert (
        APIFootballProvider._normalize_status("NS")
        == "scheduled"
    )

def test_parse_events():
    events = [
        {
            "time": {
                "elapsed": 23,
                "extra": None,
            },
            "type": "Goal",
            "detail": "Normal Goal",
            "player": {
                "name": "Lamine Yamal",
            },
        },
        {
            "time": {
                "elapsed": 67,
                "extra": None,
            },
            "type": "Goal",
            "detail": "Penalty",
            "player": {
                "name": "Robert Lewandowski",
            },
        },
        {
            "time": {
                "elapsed": 90,
                "extra": 4,
            },
            "type": "Goal",
            "detail": "Own Goal",
            "player": {
                "name": "Test Player",
            },
        },
        {
            "time": {
                "elapsed": 81,
                "extra": None,
            },
            "type": "Card",
            "detail": "Red Card",
            "player": {
                "name": "Test Defender",
            },
        },
        {
            "time": {
                "elapsed": 50,
                "extra": None,
            },
            "type": "Card",
            "detail": "Yellow Card",
            "player": {
                "name": "Test Player",
            },
        },
    ]

    parsed = APIFootballProvider._parse_events(
        events
    )

    assert parsed == [
        {
            "minute": "23",
            "type": "goal",
            "player": "Lamine Yamal",
        },
        {
            "minute": "67",
            "type": "goal",
            "player": "Robert Lewandowski",
        },
        {
            "minute": "90+4",
            "type": "goal",
            "player": "Test Player",
        },
        {
            "minute": "81",
            "type": "red_card",
            "player": "Test Defender",
        },
    ]
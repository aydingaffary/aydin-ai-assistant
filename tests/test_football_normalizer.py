from services.football_normalizer import (
    FootballNormalizer,
)


def test_normalize_penalty_and_own_goal():
    match = {
        "match_id": "123",
        "home_team": "Team A",
        "away_team": "Team B",
        "home_score": 2,
        "away_score": 0,
        "status": "finished",
        "events": [
            {
                "minute": "83",
                "type": "penalty_goal",
                "player": "Player A",
            },
            {
                "minute": "90",
                "type": "own_goal",
                "player": "Player B",
            },
        ],
    }

    result = FootballNormalizer.normalize_match(
        match
    )

    assert len(result.events) == 2

    assert result.events[0].type == "goal"
    assert result.events[1].type == "goal"


def test_normalize_red_card():
    match = {
        "match_id": "456",
        "home_team": "Team A",
        "away_team": "Team B",
        "home_score": 1,
        "away_score": 1,
        "status": "live",
        "events": [
            {
                "minute": "72",
                "type": "red_card",
                "player": "Player A",
            },
        ],
    }

    result = FootballNormalizer.normalize_match(
        match
    )

    assert len(result.events) == 1
    assert result.events[0].type == "red_card"
    assert result.events[0].player == "Player A"


def test_normalize_ignores_unneeded_events():
    match = {
        "match_id": "789",
        "home_team": "Team A",
        "away_team": "Team B",
        "home_score": 0,
        "away_score": 0,
        "status": "live",
        "events": [
            {
                "minute": "50",
                "type": "yellow_card",
                "player": "Player A",
            },
            {
                "minute": "60",
                "type": "substitution",
                "player": "Player B",
            },
        ],
    }

    result = FootballNormalizer.normalize_match(
        match
    )

    assert result.events == []
def test_normalize_provider_team_ids_to_internal_ids():
    match = {
        "provider": "api_football",
        "match_id": "123",
        "home_team_id": 529,
        "home_team": "Barcelona",
        "away_team_id": 541,
        "away_team": "Real Madrid",
        "home_score": 2,
        "away_score": 1,
        "status": "live",
        "events": [],
    }

    normalized = FootballNormalizer.normalize_match(
        match
    )

    assert normalized.home_team_id == 2
    assert normalized.away_team_id == 1
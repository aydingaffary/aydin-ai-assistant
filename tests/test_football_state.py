from database.football_state import (
    FootballStateRepository,
)


def test_save_and_get_match_state():
    repository = FootballStateRepository()

    state = {
        "match_id": "test-123",
        "status": "live",
        "home_score": 1,
        "away_score": 0,
    }

    repository.save(
        "test-123",
        state,
    )

    result = repository.get("test-123")

    assert result == state


def test_get_unknown_match_returns_none():
    repository = FootballStateRepository()

    result = repository.get(
        "unknown-test-match"
    )

    assert result is None


def test_save_updates_existing_state():
    repository = FootballStateRepository()

    first_state = {
        "status": "live",
        "home_score": 0,
        "away_score": 0,
    }

    second_state = {
        "status": "finished",
        "home_score": 2,
        "away_score": 1,
    }

    repository.save(
        "test-update-123",
        first_state,
    )

    repository.save(
        "test-update-123",
        second_state,
    )

    result = repository.get(
        "test-update-123"
    )

    assert result == second_state
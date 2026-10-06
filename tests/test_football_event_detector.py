from services.football_event_detector import (
    FootballEventDetector,
)
from services.football_normalizer import (
    NormalizedEvent,
    NormalizedMatch,
)


def make_match(
    status="live",
    events=None,
):
    return NormalizedMatch(
        match_id="123",
        home_team_id=10,
        home_team="Team A",
        away_team_id=20,
        away_team="Team B",
        home_score=0,
        away_score=0,
        status=status,
        events=events or [],
    )


def test_detect_match_started():
    previous = make_match(status="scheduled")
    current = make_match(status="live")

    detector = FootballEventDetector()

    events = detector.detect(
        previous,
        current,
    )

    assert len(events) == 1
    assert events[0].type == "match_started"


def test_detect_match_finished():
    previous = make_match(status="live")
    current = make_match(status="finished")

    detector = FootballEventDetector()

    events = detector.detect(
        previous,
        current,
    )

    assert len(events) == 1
    assert events[0].type == "match_finished"


def test_detect_new_goal():
    previous = make_match(
        events=[],
    )

    current = make_match(
        events=[
            NormalizedEvent(
                minute="55",
                type="goal",
                player="Player A",
            ),
        ],
    )

    detector = FootballEventDetector()

    events = detector.detect(
        previous,
        current,
    )

    assert len(events) == 1
    assert events[0].type == "goal"
    assert events[0].player == "Player A"


def test_detect_new_red_card():
    previous = make_match(
        events=[],
    )

    current = make_match(
        events=[
            NormalizedEvent(
                minute="72",
                type="red_card",
                player="Player B",
            ),
        ],
    )

    detector = FootballEventDetector()

    events = detector.detect(
        previous,
        current,
    )

    assert len(events) == 1
    assert events[0].type == "red_card"
    assert events[0].player == "Player B"


def test_does_not_duplicate_existing_event():
    goal = NormalizedEvent(
        minute="55",
        type="goal",
        player="Player A",
    )

    previous = make_match(
        events=[goal],
    )

    current = make_match(
        events=[goal],
    )

    detector = FootballEventDetector()

    events = detector.detect(
        previous,
        current,
    )

    assert events == []

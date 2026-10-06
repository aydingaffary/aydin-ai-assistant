from database.football_subscriptions import (
    FootballSubscriptionRepository,
)


def test_subscribe_and_get_subscribers():
    repository = FootballSubscriptionRepository()

    repository.subscribe(
        user_id=1001,
        team_id=10,
    )

    repository.subscribe(
        user_id=1002,
        team_id=10,
    )

    subscribers = repository.get_subscribers(team_id=10)

    assert subscribers == [1001, 1002]


def test_duplicate_subscription_is_ignored():
    repository = FootballSubscriptionRepository()

    repository.subscribe(
        user_id=2001,
        team_id=20,
    )

    repository.subscribe(
        user_id=2001,
        team_id=20,
    )

    subscribers = repository.get_subscribers(team_id=20)

    assert subscribers == [2001]


def test_unsubscribe():
    repository = FootballSubscriptionRepository()

    repository.subscribe(
        user_id=3001,
        team_id=30,
    )

    repository.unsubscribe(
        user_id=3001,
        team_id=30,
    )

    subscribers = repository.get_subscribers(team_id=30)

    assert subscribers == []


def test_get_user_teams():
    repository = FootballSubscriptionRepository()

    repository.subscribe(
        user_id=4001,
        team_id=40,
    )

    repository.subscribe(
        user_id=4001,
        team_id=50,
    )

    repository.subscribe(
        user_id=4001,
        team_id=60,
    )

    teams = repository.get_user_teams(user_id=4001)

    assert teams == [40, 50, 60]


def test_different_users_can_follow_same_team():
    repository = FootballSubscriptionRepository()

    repository.subscribe(
        user_id=5001,
        team_id=70,
    )

    repository.subscribe(
        user_id=5002,
        team_id=70,
    )

    repository.subscribe(
        user_id=5003,
        team_id=70,
    )

    subscribers = repository.get_subscribers(team_id=70)

    assert subscribers == [
        5001,
        5002,
        5003,
    ]

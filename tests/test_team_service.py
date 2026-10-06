from services.team_service import TeamService


def test_get_subscribers_returns_users_for_team(monkeypatch):
    class FakeCursor:
        def execute(self, *args):
            pass

        def fetchall(self):
            return [
                (1001,),
                (1002,),
            ]

    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

        def execute(self, *args):
            return FakeCursor()

    monkeypatch.setattr(
        "services.team_service.get_connection",
        lambda: FakeConnection(),
    )

    service = TeamService()

    subscribers = service.get_subscribers(10)

    assert subscribers == [1001, 1002]
    from services.team_service import TeamService


def test_get_subscribers_returns_users_for_team(monkeypatch):
    class FakeCursor:
        def execute(self, *args):
            pass

        def fetchall(self):
            return [
                (1001,),
                (1002,),
            ]

    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

        def execute(self, *args):
            return FakeCursor()

    monkeypatch.setattr(
        "services.team_service.get_connection",
        lambda: FakeConnection(),
    )

    service = TeamService()

    subscribers = service.get_subscribers(10)

    assert subscribers == [1001, 1002]


def test_add_team_uses_insert_or_ignore(monkeypatch):
    executed_sql = []

    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

        def execute(self, sql, params):
            executed_sql.append(sql)

    monkeypatch.setattr(
        "services.team_service.get_connection",
        lambda: FakeConnection(),
    )

    service = TeamService()

    service.add_team(
        user_id=1001,
        team_id=541,
        team_name="Real Madrid",
    )

    assert "INSERT OR IGNORE" in executed_sql[0]

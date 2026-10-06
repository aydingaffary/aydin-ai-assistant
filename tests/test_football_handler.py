import asyncio

from handlers import football_handler


class FakeQuery:
    def __init__(self, data=""):
        self.data = data
        self.from_user = type(
            "User",
            (),
            {"id": 1001},
        )()
        self.edited_text = None
        self.answered = False

    async def answer(self):
        self.answered = True

    async def edit_message_text(
        self,
        text,
        reply_markup=None,
    ):
        self.edited_text = text


class FakeUpdate:
    def __init__(self, query):
        self.callback_query = query


class FakeTeamService:
    def __init__(self):
        self.removed = None

    def get_teams(self, user_id):
        return [
            {
                "team_id": 541,
                "team_name": "Real Madrid",
            },
            {
                "team_id": 529,
                "team_name": "Barcelona",
            },
        ]

    def remove_team(self, user_id, team_id):
        self.removed = (
            user_id,
            team_id,
        )


def test_start_remove_team(monkeypatch):
    service = FakeTeamService()

    monkeypatch.setattr(
        football_handler,
        "team_service",
        service,
    )

    query = FakeQuery(
        data="remove_team_menu"
    )

    update = FakeUpdate(query)

    asyncio.run(
        football_handler.start_remove_team(
            update,
            None,
        )
    )

    assert query.answered is True
    assert "تیم مورد نظر برای حذف" in query.edited_text


def test_remove_team_callback(monkeypatch):
    service = FakeTeamService()

    monkeypatch.setattr(
        football_handler,
        "team_service",
        service,
    )

    query = FakeQuery(
        data="remove_team_541"
    )

    update = FakeUpdate(query)

    asyncio.run(
        football_handler.remove_team_callback(
            update,
            None,
        )
    )

    assert query.answered is True
    assert service.removed == (
        1001,
        541,
    )

    assert "با موفقیت حذف شد" in query.edited_text


def test_show_live_scores(monkeypatch):
    class FakeFootballService:
        def get_live_matches(self):
            return [
                {
                    "home_team": "Real Madrid",
                    "away_team": "Barcelona",
                    "home_score": 2,
                    "away_score": 1,
                }
            ]

    monkeypatch.setattr(
        football_handler,
        "FootballService",
        FakeFootballService,
    )

    query = FakeQuery(
        data="live_scores"
    )

    update = FakeUpdate(query)

    asyncio.run(
        football_handler.show_live_scores(
            update,
            None,
        )
    )

    assert query.answered is True
    assert "Real Madrid" in query.edited_text
    assert "Barcelona" in query.edited_text
    assert "2 - 1" in query.edited_text

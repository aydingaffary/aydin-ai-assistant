import asyncio

from services.football_event_detector import DetectedEvent
from services.football_notification_pipeline import (
    FootballNotification,
)
from services.football_notification_router import (
    RoutedFootballNotification,
)
from services.football_normalizer import (
    NormalizedMatch,
)
from services.football_scheduler import FootballScheduler


class FakePipeline:
    def check(self):
        return [
            FootballNotification(
                event=DetectedEvent(
                    type="goal",
                    match_id="match-1",
                    minute="70",
                    player="Player A",
                ),
                match=NormalizedMatch(
                    match_id="match-1",
                    home_team_id=10,
                    home_team="Team A",
                    away_team_id=20,
                    away_team="Team B",
                    home_score=1,
                    away_score=0,
                    status="live",
                    events=[],
                ),
                message="⚽ GOAL!",
            )
        ]


class FakeRouter:
    def route(self, notification):
        return [
            RoutedFootballNotification(
                user_id=1001,
                message=notification.message,
            ),
            RoutedFootballNotification(
                user_id=1002,
                message=notification.message,
            ),
        ]


class FakeBot:
    def __init__(self):
        self.sent_messages = []

    async def send_message(self, chat_id, text):
        self.sent_messages.append(
            {
                "chat_id": chat_id,
                "text": text,
            }
        )


class FakeApplication:
    def __init__(self):
        self.bot = FakeBot()


def test_scheduler_can_start_and_stop():
    async def run_test():
        scheduler = FootballScheduler(
            pipeline=FakePipeline(),
            router=FakeRouter(),
        )

        application = FakeApplication()

        await scheduler.start(application)

        assert scheduler.task is not None

        await scheduler.stop()

        assert scheduler.task is None

    asyncio.run(run_test())


def test_scheduler_sends_notification_to_subscribers():
    async def run_test():
        scheduler = FootballScheduler(
            pipeline=FakePipeline(),
            router=FakeRouter(),
        )

        application = FakeApplication()

        await scheduler.start(application)

        await asyncio.sleep(0.05)

        await scheduler.stop()

        assert application.bot.sent_messages == [
            {
                "chat_id": 1001,
                "text": "⚽ GOAL!",
            },
            {
                "chat_id": 1002,
                "text": "⚽ GOAL!",
            },
        ]

    asyncio.run(run_test())

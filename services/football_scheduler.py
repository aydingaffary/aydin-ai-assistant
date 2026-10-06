"""Football notification scheduler."""

import asyncio
import logging

from telegram.ext import Application

from services.football_notification_pipeline import (
    FootballNotificationPipeline,
)
from services.football_notification_router import (
    FootballNotificationRouter,
)

logger = logging.getLogger(__name__)


class FootballScheduler:
    """Poll football matches and send notifications."""

    INTERVAL = 30

    def __init__(
        self,
        pipeline: FootballNotificationPipeline,
        router: FootballNotificationRouter,
    ) -> None:
        self.pipeline = pipeline
        self.router = router
        self.task = None

    async def start(
        self,
        application: Application,
    ) -> None:
        """Start the background polling task."""

        if self.task is not None:
            return

        self.task = asyncio.create_task(self._run(application))

        logger.info("Football scheduler started.")

    async def stop(self) -> None:
        """Stop the background polling task."""

        if self.task is None:
            return

        self.task.cancel()

        try:
            await self.task
        except asyncio.CancelledError:
            pass

        self.task = None

        logger.info("Football scheduler stopped.")

    async def _run(
        self,
        application: Application,
    ) -> None:
        """Run football monitoring continuously."""

        while True:
            try:
                notifications = await asyncio.to_thread(self.pipeline.check)

                for notification in notifications:
                    routed_notifications = self.router.route(notification)

                    for routed in routed_notifications:
                        try:
                            await application.bot.send_message(
                                chat_id=routed.user_id,
                                text=routed.message,
                            )

                        except Exception:
                            logger.exception(
                                "Failed to send football notification " "to user %s.",
                                routed.user_id,
                            )

            except asyncio.CancelledError:
                raise

            except Exception:
                logger.exception("Football scheduler check failed.")

            await asyncio.sleep(self.INTERVAL)

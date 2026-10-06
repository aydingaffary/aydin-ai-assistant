"""Football provider manager."""

import logging

from services.api_football_service import APIFootballProvider
from services.football_provider import FootballProvider
from services.varzesh3_service import Varzesh3Provider

logger = logging.getLogger(__name__)


class FootballProviderManager:
    """Try football providers in priority order."""

    def __init__(
        self,
        providers: list[FootballProvider] | None = None,
    ) -> None:
        if providers is not None:
            self.providers = providers
        else:
            self.providers = [
                APIFootballProvider(),
                Varzesh3Provider(),
            ]

    def get_live_matches(self) -> list[dict]:
        """Get live matches using provider fallback."""

        for provider in self.providers:
            provider_name = provider.__class__.__name__

            try:
                logger.info(
                    "Trying football provider: %s",
                    provider_name,
                )

                matches = provider.get_live_matches()

                if matches:
                    logger.info(
                        "Football provider succeeded: %s",
                        provider_name,
                    )
                    return matches

                logger.warning(
                    "Football provider returned no matches: %s",
                    provider_name,
                )

            except Exception as error:
                logger.warning(
                    "Football provider failed (%s): %s",
                    provider_name,
                    error,
                )

        logger.error("All football providers failed.")
        return []

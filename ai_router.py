"""AI providers router."""

import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError

from providers.gemini import GeminiProvider
from providers.groq import GroqProvider
from providers.huggingface import HuggingFaceProvider

logger = logging.getLogger(__name__)


class AIRouter:
    """Route AI requests to available providers."""

    TIMEOUT = 10

    def __init__(self) -> None:
        self.providers = []

        for provider_class in [
            GeminiProvider,
            GroqProvider,
            HuggingFaceProvider,
        ]:
            try:
                self.providers.append(provider_class())

            except Exception as error:
                logger.warning(
                    "%s disabled: %s",
                    provider_class.__name__,
                    error,
                )

    def ask(self, prompt: str) -> str:
        """Try providers with timeout."""

        for provider in self.providers:
            provider_name = provider.__class__.__name__

            try:
                logger.info(
                    "Trying provider: %s",
                    provider_name,
                )

                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(
                        provider.generate_response,
                        prompt,
                    )

                    response = future.result(
                        timeout=self.TIMEOUT,
                    )

                logger.info(
                    "Provider succeeded: %s",
                    provider_name,
                )

                return response

            except TimeoutError:
                logger.warning(
                    "%s timed out after %s seconds",
                    provider_name,
                    self.TIMEOUT,
                )

            except Exception as error:
                logger.warning(
                    "%s failed: %s",
                    provider_name,
                    error,
                )

        return "❌ هیچ سرویس هوش مصنوعی در دسترس نیست."

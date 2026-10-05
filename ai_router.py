"""AI providers router."""
from providers.huggingface import HuggingFaceProvider
from concurrent.futures import ThreadPoolExecutor, TimeoutError

from providers.gemini import GeminiProvider
from providers.groq import GroqProvider


class AIRouter:
    """Route AI requests to available providers."""

    TIMEOUT = 10

    def __init__(self):
        self.providers = []

        for provider_class in [
            GeminiProvider,
            GroqProvider,
            HuggingFaceProvider,
        ]:
            try:
                self.providers.append(provider_class())

            except Exception as error:
                print(
                    provider_class.__name__,
                    "disabled:",
                    error,
                )

    def ask(self, prompt: str) -> str:
        """Try providers with timeout."""

        for provider in self.providers:
            try:
                print(
                    "Trying:",
                    provider.__class__.__name__,
                )

                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(
                        provider.generate_response,
                        prompt,
                    )

                    response = future.result(timeout=self.TIMEOUT)

                print(
                    "Success:",
                    provider.__class__.__name__,
                )

                return response

            except TimeoutError:
                print(
                    provider.__class__.__name__,
                    "timeout after 10 seconds",
                )

            except Exception as error:
                print(
                    provider.__class__.__name__,
                    "failed:",
                    error,
                )

        return "❌ هیچ سرویس هوش مصنوعی در دسترس نیست."

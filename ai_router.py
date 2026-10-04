from providers.gemini import GeminiProvider


class AIRouter:
    """Route AI requests to available AI providers."""

    def __init__(self) -> None:
        self.gemini = GeminiProvider()

    def ask_gemini(self, prompt: str) -> str:
        """Send a prompt to Gemini provider."""

        return self.gemini.generate_response(prompt)
"""Groq AI provider."""

from groq import Groq

from config import GROQ_API_KEY


class GroqProvider:
    """Handle requests to Groq API."""

    def __init__(self) -> None:
        self.client = None

        if GROQ_API_KEY:
            self.client = Groq(
                api_key=GROQ_API_KEY,
            )

    def generate_response(self, prompt: str) -> str:
        """Generate response using Groq."""

        if self.client is None:
            raise RuntimeError("Groq API key is missing.")

        response = self.client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        return response.choices[0].message.content
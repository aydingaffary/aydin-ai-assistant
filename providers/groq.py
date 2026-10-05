"""Groq AI provider."""

import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()


class GroqProvider:
    """Handle requests to Groq API."""

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")

        self.client = None

        if api_key:
            self.client = Groq(
                api_key=api_key,
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

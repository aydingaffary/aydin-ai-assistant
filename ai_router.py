import os

from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()


class AIRouter:
    """Route AI requests to the available AI providers."""

    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set.")

        self.gemini = genai.Client(api_key=api_key)

    def ask_gemini(self, prompt: str) -> str:
        """Send a prompt to Gemini."""

        try:
            interaction = self.gemini.interactions.create(
                model="gemini-3.8-flash",
                input=prompt,
            )

            return interaction.output_text

        except errors.ClientError as error:
            if error.code == 429:
                raise RuntimeError(
                    "Gemini quota or rate limit was exceeded."
                ) from error

            if error.code in (401, 403):
                raise RuntimeError(
                    "Gemini authentication failed."
                ) from error

            raise RuntimeError(
                f"Gemini API error: {error.code}"
            ) from error

        except errors.ServerError as error:
            raise RuntimeError(
                "Gemini server error. Please try again later."
            ) from error

        except Exception as error:
            raise RuntimeError(
                "Unexpected error while contacting Gemini."
            ) from error
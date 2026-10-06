from google import genai
from google.genai import errors

from config import GEMINI_API_KEY


class GeminiProvider:
    """Handle requests to the Gemini API."""

    def __init__(self) -> None:
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set.")

        self.client = genai.Client(api_key=GEMINI_API_KEY)

    def generate_response(self, prompt: str) -> str:
        """Generate a response using Gemini."""

        try:
            interaction = self.client.interactions.create(
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
                raise RuntimeError("Gemini authentication failed.") from error

            raise RuntimeError(f"Gemini API error: {error.code}") from error

        except errors.ServerError as error:
            raise RuntimeError(
                "Gemini server error. Please try again later."
            ) from error

        except Exception:
            raise

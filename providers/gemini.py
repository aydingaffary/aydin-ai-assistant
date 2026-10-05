import os

from dotenv import load_dotenv
from google import genai
from google.genai import errors
from concurrent.futures import ThreadPoolExecutor, TimeoutError

load_dotenv()


class GeminiProvider:
    """Handle requests to the Gemini API."""

    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set.")

        self.client = genai.Client(api_key=api_key)

    def generate_response(self, prompt: str) -> str:
        """Generate a response using Gemini."""

        def request():
            interaction = self.client.interactions.create(
                model="gemini-3.8-flash",
                input=prompt,
            )

            return interaction.output_text

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

        except Exception as error:
            print("Gemini DEBUG ERROR:", repr(error))
            raise

import os

from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()


class HuggingFaceProvider:
    """Handle Hugging Face AI requests."""

    def __init__(self):
        api_key = os.getenv("HF_API_KEY")

        if not api_key:
            raise ValueError("HF_API_KEY is not set.")

        self.client = InferenceClient(api_key=api_key)

    def generate_response(
        self,
        prompt: str,
    ) -> str:
        """Generate AI response."""

        response = self.client.chat.completions.create(
            model="Qwen/Qwen3.8-27B",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        return response.choices[0].message.content

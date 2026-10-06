"""Hugging Face AI provider."""

from huggingface_hub import InferenceClient

from config import HF_API_KEY


class HuggingFaceProvider:
    """Handle Hugging Face AI requests."""

    def __init__(self) -> None:
        if not HF_API_KEY:
            raise ValueError("HF_API_KEY is not set.")

        self.client = InferenceClient(
            api_key=HF_API_KEY,
        )

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
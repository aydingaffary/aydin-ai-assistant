from unittest.mock import patch

from providers.gemini import GeminiProvider


def test_gemini_provider_initializes():
    """Gemini provider should initialize with a configured API key."""

    with patch("providers.gemini.genai.Client") as mock_client:
        provider = GeminiProvider()

        mock_client.assert_called_once()
        assert provider.client is mock_client.return_value

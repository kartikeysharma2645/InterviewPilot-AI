from google import genai

from config import Config


class GeminiService:
    """Handles communication with the Gemini API."""

    def __init__(self):
        if not Config.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY is not configured."
            )

        self.client = genai.Client(
            api_key=Config.GEMINI_API_KEY
        )

        self.model = Config.GEMINI_MODEL

    def generate(self, prompt: str) -> str:
        """
        Generate a text response from Gemini.
        """

        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )

            if not response.text:
                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            return response.text.strip()

        except Exception as error:
            raise RuntimeError(
                f"Gemini API request failed: {error}"
            ) from error
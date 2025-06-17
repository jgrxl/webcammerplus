# pylint: disable=R0801
import logging
from typing import Optional

from .base_ai_client import BaseAIService, NovitaAIClient

logger = logging.getLogger(__name__)


class WriteService(BaseAIService):
    """Service for generating creative text using AI."""

    def __init__(self, client: Optional[NovitaAIClient] = None):
        super().__init__(client)
        # Override model for writing tasks
        self.client.default_params["model"] = "meta-llama/llama-3.2-3b-instruct"

    def get_system_prompt(self) -> str:
        """Default system prompt for writing."""
        return "You are a creative writer. Generate engaging content based on the given instructions. Provide only the requested text without any explanations."

    def get_default_temperature(self) -> float:
        """Use default temperature for creative writing."""
        return 0.7

    def write_text(self, style: str, text: str, to_lang: str) -> str:
        """
        Generate creative text in the specified style and language.

        Args:
            style: The writing style (e.g., "romantic", "funny", "professional")
            text: The topic or context to write about
            to_lang: The language to write in

        Returns:
            Generated text

        Raises:
            ValueError: If text generation fails
        """
        prompt = self._build_prompt_write(style, text, to_lang)

        try:
            written_text = self.process_request(user_content=prompt, max_tokens=500)

            # Clean up the response
            written_text = self._clean_write_response(written_text)

            logger.info(
                f"Text generated successfully in {style} style, {to_lang} language"
            )
            return written_text

        except Exception as e:
            logger.error(f"Text generation failed: {str(e)}")
            raise ValueError(f"Text generation failed: {str(e)}")

    def _build_prompt_write(
        self,
        style: str,
        text: str,
        to_lang: str,
    ) -> str:
        """Build the text generation prompt."""
        prompt = f"Write a {style} text in {to_lang} about the following text: {text}"
        return prompt

    def _clean_write_response(self, written_text: str) -> str:
        """Clean up AI response to extract just the generated text."""
        written_text = written_text.strip()

        # Remove thinking tags if present
        if "<think>" in written_text and "</think>" in written_text:
            parts = written_text.split("</think>")
            if len(parts) > 1:
                written_text = parts[1].strip()

        return written_text


# Legacy function for backward compatibility
def write_text(style: str, text: str, to_lang: str) -> str:
    """
    Legacy function for backward compatibility.
    Use WriteService class directly for new code.
    """
    service = WriteService()
    return service.write_text(style, text, to_lang)

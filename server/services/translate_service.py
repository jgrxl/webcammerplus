# pylint: disable=R0801
import logging
import re
from typing import Optional

from .base_ai_client import BaseAIService, NovitaAIClient

logger = logging.getLogger(__name__)


class TranslateService(BaseAIService):
    """Service for translating text using AI."""

    def __init__(self, client: Optional[NovitaAIClient] = None):
        super().__init__(client)
        # Override model for translation tasks
        self.client.default_params["model"] = "meta-llama/llama-3.2-3b-instruct"

    def get_system_prompt(self) -> str:
        """Default system prompt for translation."""
        return "You are a professional translator. Provide only the direct translation without any explanations or additional text."

    def get_default_temperature(self) -> float:
        """Use lower temperature for more accurate translations."""
        return 0.3

    def translate_text(
        self,
        text: str,
        to_lang: str,
        from_lang: Optional[str] = None,
    ) -> str:
        """
        Use Novita AI API to translate `text` into `to_lang`.

        Args:
            text: Text to translate
            to_lang: Target language
            from_lang: Source language (optional)

        Returns:
            Translated text

        Raises:
            ValueError: If translation fails
        """
        prompt = self._build_prompt_translate(text, to_lang, from_lang)

        try:
            translation = self.process_request(user_content=prompt, max_tokens=500)

            # Clean up the response
            translation = self._clean_translation_response(translation)

            logger.info(f"Translation successful: {text[:50]}... -> {to_lang}")
            return translation

        except Exception as e:
            logger.error(f"Translation failed: {str(e)}")
            raise ValueError(f"Translation failed: {str(e)}")

    def _build_prompt_translate(
        self,
        text: str,
        to_lang: str,
        from_lang: Optional[str] = None,
    ) -> str:
        """Build the translation prompt."""
        prompt = f"Translate the following text to {to_lang}"
        if from_lang:
            prompt += f" from {from_lang}"
        prompt += f": {text}"
        return prompt

    def _clean_translation_response(self, translation: str) -> str:
        """Clean up AI response to extract just the translation."""
        translation = translation.strip()

        # Remove thinking tags if present
        if "<think>" in translation and "</think>" in translation:
            parts = translation.split("</think>")
            if len(parts) > 1:
                translation = parts[1].strip()

        # Handle Llama-style verbose responses
        if "translation" in translation.lower() and "is" in translation.lower():
            # Try to extract the actual translation from verbose responses
            # Pattern to match: The translation... is "..."
            quote_match = re.search(r'"([^"]+)"', translation)
            if quote_match:
                translation = quote_match.group(1)
            else:
                # Pattern to match: is [translation]
                is_match = re.search(r"\bis\s+(.+?)\.?$", translation, re.IGNORECASE)
                if is_match:
                    translation = is_match.group(1).strip(' ."')

        return translation


# Legacy function for backward compatibility
def translate_text(
    text: str,
    to_lang: str,
    from_lang: Optional[str] = None,
) -> str:
    """
    Legacy function for backward compatibility.
    Use TranslateService class directly for new code.
    """
    service = TranslateService()
    return service.translate_text(text, to_lang, from_lang)

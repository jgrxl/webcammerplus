# pylint: disable=R0801
import logging
from typing import Optional

from .base_ai_client import BaseAIService, NovitaAIClient

logger = logging.getLogger(__name__)


class ReplyService(BaseAIService):
    """Service for generating contextual replies using AI."""

    def __init__(self, client: Optional[NovitaAIClient] = None):
        super().__init__(client)
        # Override model for reply tasks
        self.client.default_params["model"] = "meta-llama/llama-3.2-3b-instruct"

    def get_system_prompt(self) -> str:
        """Default system prompt for replies."""
        return "You are a helpful assistant that generates contextual replies. Provide only the reply text without any explanations."

    def get_default_temperature(self) -> float:
        """Use default temperature for creative replies."""
        return 0.7

    def reply_text(
        self,
        original_text: str,
        response_idea: str,
        style: str,
        to_lang: str,
    ) -> str:
        """
        Generate a reply to the original text based on the response idea and style.

        Args:
            original_text: The text to reply to
            response_idea: The general idea for the response
            style: The style/tone of the reply
            to_lang: The language for the reply

        Returns:
            Generated reply text

        Raises:
            ValueError: If reply generation fails
        """
        prompt = self._build_prompt_reply(original_text, response_idea, style, to_lang)

        try:
            reply = self.process_request(user_content=prompt, max_tokens=500)

            # Clean up the response
            reply = self._clean_reply_response(reply)

            logger.info(f"Reply generated successfully in {to_lang}")
            return reply

        except Exception as e:
            logger.error(f"Reply generation failed: {str(e)}")
            raise ValueError(f"Reply generation failed: {str(e)}")

    def _build_prompt_reply(
        self,
        original_text: str,
        response_idea: str,
        style: str,
        to_lang: str,
    ) -> str:
        """Build the reply generation prompt."""
        prompt = (
            f"Reply to the following text in {to_lang}: {original_text} "
            f"using the general idea like so: {response_idea} "
            f"and the style: {style}"
        )
        return prompt

    def _clean_reply_response(self, reply: str) -> str:
        """Clean up AI response to extract just the reply."""
        reply = reply.strip()

        # Remove thinking tags if present
        if "<think>" in reply and "</think>" in reply:
            parts = reply.split("</think>")
            if len(parts) > 1:
                reply = parts[1].strip()

        return reply


# Legacy function for backward compatibility
def reply_text(
    original_text: str,
    response_idea: str,
    style: str,
    to_lang: str,
) -> str:
    """
    Legacy function for backward compatibility.
    Use ReplyService class directly for new code.
    """
    service = ReplyService()
    return service.reply_text(original_text, response_idea, style, to_lang)

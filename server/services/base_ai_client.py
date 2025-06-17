import logging
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


class NovitaAIClient:
    """Base client for Novita AI API interactions."""

    BASE_URL = "https://api.novita.ai/v3/openai"
    DEFAULT_MODEL = "meta-llama/llama-3.1-70b-instruct"

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Novita AI client.

        Args:
            api_key: Novita AI API key. If not provided, will use environment variable.
        """
        self.api_key = api_key or os.getenv("NOVITA_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Novita API key is required. Set NOVITA_API_KEY environment variable."
            )

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # Default parameters that can be overridden
        self.default_params = {
            "model": self.DEFAULT_MODEL,
            "stream": False,
            "max_tokens": 4096,
            "temperature": 0.7,
        }

    def _make_request(
        self,
        endpoint: str,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Make a request to the Novita AI API.

        Args:
            endpoint: API endpoint path
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Override default temperature
            max_tokens: Override default max tokens
            **kwargs: Additional parameters to pass to the API

        Returns:
            API response dictionary

        Raises:
            requests.RequestException: If the API request fails
        """
        url = f"{self.BASE_URL}{endpoint}"

        # Build request data with defaults and overrides
        data = self.default_params.copy()
        data.update({"messages": messages, **kwargs})

        # Apply overrides
        if temperature is not None:
            data["temperature"] = temperature
        if max_tokens is not None:
            data["max_tokens"] = max_tokens

        try:
            response = requests.post(url, json=data, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Novita AI API request failed: {str(e)}")
            raise

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> str:
        """Get a chat completion from the AI.

        Args:
            messages: List of message dictionaries
            temperature: Override default temperature
            max_tokens: Override default max tokens
            **kwargs: Additional parameters

        Returns:
            The AI's response content

        Raises:
            Exception: If the response format is unexpected
        """
        response = self._make_request(
            "/chat/completions",
            messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

        try:
            return response["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            logger.error(f"Unexpected response format: {response}")
            raise Exception("Failed to extract content from AI response") from e


class BaseAIService(ABC):
    """Abstract base class for AI services using Novita AI."""

    def __init__(self, client: Optional[NovitaAIClient] = None):
        """Initialize the service with an AI client.

        Args:
            client: NovitaAIClient instance. If not provided, creates a new one.
        """
        self.client = client or NovitaAIClient()

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt for this service.

        Returns:
            System prompt string
        """

    @abstractmethod
    def get_default_temperature(self) -> float:
        """Get the default temperature for this service.

        Returns:
            Temperature value between 0 and 1
        """

    def process_request(
        self,
        user_content: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        **kwargs,
    ) -> str:
        """Process a request using the AI client.

        Args:
            user_content: The user's input content
            system_prompt: Override the default system prompt
            temperature: Override the default temperature
            **kwargs: Additional parameters for the AI

        Returns:
            The AI's response
        """
        messages = [
            {"role": "system", "content": system_prompt or self.get_system_prompt()},
            {"role": "user", "content": user_content},
        ]

        return self.client.chat_completion(
            messages=messages,
            temperature=temperature or self.get_default_temperature(),
            **kwargs,
        )

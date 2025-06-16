# pylint: disable=R0801
import os
from typing import Optional

import requests

# Novita API Configuration
NOVITA_API_KEY = os.getenv("NOVITA_API_KEY")
NOVITA_BASE_URL = "https://api.novita.ai"
NOVITA_MODEL = "meta-llama/llama-3.2-3b-instruct"


def translate_text(
    text: str,
    to_lang: str,
    from_lang: Optional[str] = None,
) -> str:
    """
    Use Novita AI API to translate `text` into `to_lang`.
    """
    prompt = _build_prompt_translate(text, to_lang, from_lang)

    url = f"{NOVITA_BASE_URL}/v3/openai/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {NOVITA_API_KEY}",
    }

    request_body = {
        "model": NOVITA_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500,
        "temperature": 0.3,
    }

    try:
        response = requests.post(url, headers=headers, json=request_body, timeout=30)

        if not response.ok:
            error_details = ""
            try:
                error_data = response.json()
                error_details = error_data.get("error", {}).get(
                    "message", str(error_data)
                )
            except Exception:
                error_details = response.text
            raise ValueError(
                f"Novita API request failed: {response.status_code} - {error_details}"
            )

        data = response.json()

        if data.get("choices") and data["choices"][0].get("message"):
            translation = data["choices"][0]["message"]["content"].strip()

            # Clean up the response - remove thinking tags if present
            if "<think>" in translation and "</think>" in translation:
                # Extract text after the thinking section
                parts = translation.split("</think>")
                if len(parts) > 1:
                    translation = parts[1].strip()

            # Handle Llama-style verbose responses
            # Look for common patterns like "The translation of ... is ..."
            if "translation" in translation.lower() and "is" in translation.lower():
                # Try to extract the actual translation from verbose responses
                import re

                # Pattern to match: The translation... is "..."
                quote_match = re.search(r'"([^"]+)"', translation)
                if quote_match:
                    translation = quote_match.group(1)
                else:
                    # Pattern to match: is [translation]
                    is_match = re.search(
                        r"\bis\s+(.+?)\.?$", translation, re.IGNORECASE
                    )
                    if is_match:
                        translation = is_match.group(1).strip(' ."')

            return translation
        else:
            raise ValueError("Unexpected API response format")

    except requests.exceptions.RequestException as e:
        raise ValueError(f"Network error calling Novita API: {str(e)}")


def _build_prompt_translate(
    text: str,
    to_lang: str,
    from_lang: Optional[str] = None,
) -> str:
    prompt = f"Translate the following text to {to_lang}"
    if from_lang:
        prompt += f" from {from_lang}"
    prompt += f": {text}"
    return prompt

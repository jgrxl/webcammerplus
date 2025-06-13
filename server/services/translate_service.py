from typing import Optional

from ollama import Client

OLLAMA_MODEL = "tinyllama:latest"
OLLAMA_HOST = "http://localhost:11434"

client = Client(host=OLLAMA_HOST)


def translate_text(
    text: str,
    to_lang: str,
    from_lang: Optional[str] = None,
) -> str:
    """
    Use Ollama's Python client to translate `text` into `to_lang`.
    """
    prompt = _build_prompt(text, to_lang, from_lang)

    response = client.chat(
        model=OLLAMA_MODEL, messages=[{"role": "user", "content": prompt}]
    )

    if response.message.content is None:
        raise ValueError("No content in response")

    return response.message.content


def _build_prompt(
    text: str,
    to_lang: str,
    from_lang: Optional[str] = None,
) -> str:
    prompt = f"Translate the following text to {to_lang}"
    if from_lang:
        prompt += f" from {from_lang}"
    prompt += f": {text}"
    return prompt

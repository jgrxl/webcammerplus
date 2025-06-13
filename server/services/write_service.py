# pylint: disable=R0801
from ollama import Client

OLLAMA_MODEL = "tinyllama:latest"
OLLAMA_HOST = "http://localhost:11434"

client = Client(host=OLLAMA_HOST)


def write_text(style: str, text: str, to_lang: str) -> str:
    prompt = _build_prompt_write(style, text, to_lang)
    response = client.chat(
        model=OLLAMA_MODEL, messages=[{"role": "user", "content": prompt}]
    )

    if response["message"]["content"] is None:
        raise ValueError("No content in response")

    response_text: str = response["message"]["content"]
    return response_text


def _build_prompt_write(
    style: str,
    text: str,
    to_lang: str,
) -> str:
    prompt = f"Write a {style} text in {to_lang} " f"about the following text: {text}"
    return prompt

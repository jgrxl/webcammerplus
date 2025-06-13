from typing import Optional

# from ollama import chat

OLLAMA_MODEL = "llama2"  # or whichever model you've pulled


def translate_text(
    text: str,
    to_lang: str,
    from_lang: Optional[str] = None,
) -> str:
    """
    Use Ollama’s Python client to translate `text` into `to_lang`.
    """
    if from_lang:
        content = f"Translate from {from_lang} to {to_lang}: {text}"
    else:
        content = f"Translate the following text to {to_lang}: {text}"

    return content

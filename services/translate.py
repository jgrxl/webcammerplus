# type: ignore[no-any-return]
from ollama import chat
from typing import Optional, Any, cast

OLLAMA_MODEL = "llama2"  # or whichever model you've pulled

def _ensure_str(val: Any) -> str:
    if val is None:
        return ""
    return str(val)

def translate_text(
    text: str,
    to_lang: str,
    from_lang: Optional[str] = None,
) -> str:
    """Translate text using Ollama."""
    if from_lang:
        content = f"Translate from {from_lang} to {to_lang}: {text}"
    else:
        content = f"Translate the following text to {to_lang}: {text}"

    # chat() wraps the HTTP API for you
    response: Any = chat(model=OLLAMA_MODEL, messages=[{"role": "user", "content": content}])
    # the translated text is in response.message.content
    result = getattr(response.message, "content", None)
    if result is None:
        return text  # Return original text if translation fails
    
    # Ensure we always return a string
    result_str = str(result) if result is not None else text
    return result_str.strip() 
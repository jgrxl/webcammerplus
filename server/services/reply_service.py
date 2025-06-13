from ollama import Client

OLLAMA_MODEL = "tinyllama:latest"
OLLAMA_HOST = "http://localhost:11434"

client = Client(host=OLLAMA_HOST)


def reply_text(original_text, response_idea: str, style: str, to_lang: str) -> str:
    prompt = _build_prompt(original_text, response_idea, style, to_lang)
    response = client.chat(
        model=OLLAMA_MODEL, messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"]


def _build_prompt(
    original_text,
    response_idea: str,
    style: str,
    to_lang: str,
) -> str:
    prompt = (
        f"Reply to the following text in {to_lang}: {original_text} "
        f"using the general idea like so: {response_idea} "
        f"and the style: {style}"
    )
    return prompt

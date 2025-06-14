# pylint: disable=R0801
import os
import requests

# Novita API Configuration
NOVITA_API_KEY = os.getenv("NOVITA_API_KEY", "sk_Z2EJOtHGNf5Nv2tgSoouT6PZzbXoY3UoLjpn5C5cYkE")
NOVITA_BASE_URL = "https://api.novita.ai"
NOVITA_MODEL = "meta-llama/llama-3.2-3b-instruct"


def write_text(style: str, text: str, to_lang: str) -> str:
    prompt = _build_prompt_write(style, text, to_lang)
    
    url = f"{NOVITA_BASE_URL}/v3/openai/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {NOVITA_API_KEY}"
    }
    
    request_body = {
        "model": NOVITA_MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 500,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, headers=headers, json=request_body, timeout=30)
        
        if not response.ok:
            error_details = ""
            try:
                error_data = response.json()
                error_details = error_data.get("error", {}).get("message", str(error_data))
            except Exception:
                error_details = response.text
            raise ValueError(f"Novita API request failed: {response.status_code} - {error_details}")
        
        data = response.json()
        
        if data.get("choices") and data["choices"][0].get("message"):
            written_text = data["choices"][0]["message"]["content"].strip()
            
            # Clean up the response - remove thinking tags if present
            if "<think>" in written_text and "</think>" in written_text:
                # Extract text after the thinking section
                parts = written_text.split("</think>")
                if len(parts) > 1:
                    written_text = parts[1].strip()
            
            return written_text
        else:
            raise ValueError("Unexpected API response format")
            
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Network error calling Novita API: {str(e)}")


def _build_prompt_write(
    style: str,
    text: str,
    to_lang: str,
) -> str:
    prompt = f"Write a {style} text in {to_lang} " f"about the following text: {text}"
    return prompt

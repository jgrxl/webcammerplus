# pylint: disable=R0801
import os
import requests

# Novita API Configuration
NOVITA_API_KEY = os.getenv("NOVITA_API_KEY")
NOVITA_BASE_URL = "https://api.novita.ai"
NOVITA_MODEL = "meta-llama/llama-3.2-3b-instruct"


def reply_text(
    original_text: str,
    response_idea: str,
    style: str,
    to_lang: str,
) -> str:
    prompt = _build_prompt_reply(original_text, response_idea, style, to_lang)
    
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
            reply = data["choices"][0]["message"]["content"].strip()
            
            # Clean up the response - remove thinking tags if present
            if "<think>" in reply and "</think>" in reply:
                # Extract text after the thinking section
                parts = reply.split("</think>")
                if len(parts) > 1:
                    reply = parts[1].strip()
            
            return reply
        else:
            raise ValueError("Unexpected API response format")
            
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Network error calling Novita API: {str(e)}")


def _build_prompt_reply(
    original_text: str,
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

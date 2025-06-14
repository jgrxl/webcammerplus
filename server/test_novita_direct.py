#!/usr/bin/env python3
"""
Test Novita API directly to debug the issue
"""
import requests
import json

def test_novita_api():
    api_key = "sk_Z2EJOtHGNf5Nv2tgSoouT6PZzbXoY3UoLjpn5C5cYkE"
    url = "https://api.novita.ai/v3/openai/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "qwen/qwen3-4b-fp8",
        "messages": [
            {
                "role": "user",
                "content": "Translate 'Hello world' to Spanish. Respond only with the translation."
            }
        ],
        "max_tokens": 50,
        "temperature": 0.3
    }
    
    print(f"Testing Novita API...")
    print(f"URL: {url}")
    print(f"Model: {payload['model']}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success! Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out - API might be slow or unavailable")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

def test_alternative_model():
    """Test with a different model that might be more available"""
    api_key = "sk_Z2EJOtHGNf5Nv2tgSoouT6PZzbXoY3UoLjpn5C5cYkE"
    url = "https://api.novita.ai/v3/openai/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # Try a simpler/more available model
    payload = {
        "model": "meta-llama/llama-3.2-3b-instruct",
        "messages": [
            {
                "role": "user",
                "content": "Translate 'Hello world' to Spanish."
            }
        ],
        "max_tokens": 50,
        "temperature": 0.3
    }
    
    print(f"\nTesting alternative model...")
    print(f"Model: {payload['model']}")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success! Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_novita_api()
    test_alternative_model()
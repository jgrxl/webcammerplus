#!/usr/bin/env python3
"""
Simple test script to verify the translate API endpoint works with Novita AI
"""
import json

import requests


def test_translate_api():
    url = "http://localhost:5000/translate/"

    # Test data
    test_payload = {"text": "Hello world", "to_lang": "es"}

    try:
        print("Testing translate API with Novita AI...")
        print(f"URL: {url}")
        print(f"Payload: {json.dumps(test_payload, indent=2)}")

        response = requests.post(
            url,
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=60,  # Increased timeout for API calls
        )

        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Translation API working correctly with Novita AI!")
                print(f"Translation: {result.get('translation')}")
            else:
                print("❌ API returned success=false")
        else:
            print(f"❌ HTTP Error: {response.status_code}")

    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure Flask server is running on localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}")


def test_direct_service():
    """Test the translate service directly"""
    try:
        print("\nTesting translate service directly...")
        from services.translate_service import translate_text

        result = translate_text("Hello world", "es")
        print(f"✅ Direct service test successful!")
        print(f"Translation: {result}")

    except Exception as e:
        print(f"❌ Direct service test failed: {e}")


if __name__ == "__main__":
    test_direct_service()
    print("\n" + "=" * 50 + "\n")
    test_translate_api()

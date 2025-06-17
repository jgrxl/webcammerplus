#!/usr/bin/env python3
"""Debug script to show current user info"""

import json

import requests


def debug_user():
    print("🔍 Debug Current User Info")
    print("=" * 30)

    # This should use the actual token from the browser
    # For now, let's check the auth endpoint
    try:
        response = requests.get(
            "http://localhost:5000/api/v1/auth/profile",
            headers={"Authorization": "Bearer test-token"},
        )

        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            user_info = response.json()
            print(f"User Info: {json.dumps(user_info, indent=2)}")
        else:
            print(f"Error: {response.text}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    debug_user()

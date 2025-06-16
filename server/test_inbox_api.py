#!/usr/bin/env python3
"""Test script for inbox API endpoints"""

import requests
import json

# Test the inbox API endpoints
BASE_URL = "http://localhost:5000/api/v1"

def test_inbox_endpoints():
    print("🧪 Testing Inbox API Endpoints")
    print("=" * 40)
    
    # Mock auth token for testing
    headers = {
        'Authorization': 'Bearer mock-token-for-testing',
        'Content-Type': 'application/json'
    }
    
    try:
        # Test stats endpoint
        print("\n1. Testing /inbox/stats")
        response = requests.get(f"{BASE_URL}/inbox/stats", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        else:
            print(f"   Error: {response.text}")
        
        # Test conversations endpoint
        print("\n2. Testing /inbox/conversations")
        response = requests.get(f"{BASE_URL}/inbox/conversations", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        else:
            print(f"   Error: {response.text}")
            
        # Test messages endpoint
        print("\n3. Testing /inbox/messages")
        response = requests.get(f"{BASE_URL}/inbox/messages", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        else:
            print(f"   Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - make sure the server is running on port 5000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_inbox_endpoints()
#!/usr/bin/env python3
"""
Test script for inbox functionality
"""
import requests
import json

def test_inbox():
    base_url = "http://localhost:5000/api/v1/inbox"
    
    # Test without auth first to see the error
    print("🧪 Testing inbox endpoints...")
    
    try:
        # Test conversations endpoint
        response = requests.get(f"{base_url}/conversations")
        print(f"📋 Conversations (no auth): {response.status_code}")
        if response.status_code != 200:
            print(f"📋 Error: {response.text}")
        
        # Test with a conversation user
        response = requests.get(f"{base_url}/conversations/SecretAdmirer")
        print(f"💬 Messages for SecretAdmirer (no auth): {response.status_code}")
        if response.status_code != 200:
            print(f"💬 Error: {response.text}")
            
        # Test the debug endpoint
        response = requests.get(f"{base_url}/test/SecretAdmirer")
        print(f"🧪 Debug test (no auth): {response.status_code}")
        if response.status_code != 200:
            print(f"🧪 Error: {response.text}")
        
    except Exception as e:
        print(f"❌ Error calling API: {e}")

if __name__ == "__main__":
    test_inbox()
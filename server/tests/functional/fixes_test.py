#!/usr/bin/env python3
"""Test all the fixes we implemented."""

import json
import requests
import time

BASE_URL = "http://localhost:5000"

def test_health_endpoints():
    """Test health check endpoints."""
    print("\n🔍 Testing Health Check Endpoints...")
    
    # Test root health check
    response = requests.get(f"{BASE_URL}/")
    print(f"  GET / - Status: {response.status_code}")
    if response.status_code == 200:
        print(f"    Response: {response.json()}")
    
    # Test API v1 health check
    response = requests.get(f"{BASE_URL}/api/v1")
    print(f"  GET /api/v1 - Status: {response.status_code}")
    if response.status_code == 200:
        print(f"    Response: {response.json()}")
    
    # Test API v1 with trailing slash
    response = requests.get(f"{BASE_URL}/api/v1/")
    print(f"  GET /api/v1/ - Status: {response.status_code}")
    if response.status_code == 200:
        print(f"    Response: {response.json()}")


def test_influx_search():
    """Test InfluxDB search with fields that might cause schema collision."""
    print("\n🔍 Testing InfluxDB Search (Schema Collision Fix)...")
    
    # Test with _value field (should now avoid schema collision)
    payload = {
        "filters": {"method": "tip"},
        "range": {"start": "-7d", "stop": "now()"},
        "fields": ["_time", "_value", "method", "user"],
        "limit": 5
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/influx/search",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"  POST /api/v1/influx/search - Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"    Success: {data['success']}")
        print(f"    Record count: {data['count']}")
        if 'error' in data:
            print(f"    Error: {data['error']}")


def test_chaturbate_demo():
    """Test Chaturbate demo mode (async fix)."""
    print("\n🔍 Testing Chaturbate Demo Mode (Async Fix)...")
    
    # Start demo mode
    payload = {"demo_mode": True}
    response = requests.post(
        f"{BASE_URL}/api/v1/chaturbate/start",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"  POST /api/v1/chaturbate/start - Status: {response.status_code}")
    if response.status_code == 200:
        print(f"    Response: {response.json()}")
    
    # Wait a bit for async initialization
    time.sleep(2)
    
    # Check status
    response = requests.get(f"{BASE_URL}/api/v1/chaturbate/status")
    print(f"  GET /api/v1/chaturbate/status - Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"    Running: {data.get('running', False)}")
        print(f"    Demo Mode: {data.get('demo_mode', False)}")
    
    # Stop demo mode
    response = requests.post(f"{BASE_URL}/api/v1/chaturbate/stop")
    print(f"  POST /api/v1/chaturbate/stop - Status: {response.status_code}")


def test_auth_endpoints():
    """Test authentication endpoints (JSON serialization fix)."""
    print("\n🔍 Testing Auth Endpoints (JSON Serialization Fix)...")
    
    headers = {
        "Authorization": "Bearer dummy_token",
        "Content-Type": "application/json"
    }
    
    # Test profile endpoint
    response = requests.get(f"{BASE_URL}/api/v1/auth/profile", headers=headers)
    print(f"  GET /api/v1/auth/profile - Status: {response.status_code}")
    if response.status_code != 500:
        print("    ✅ No JSON serialization error!")
    
    # Test subscription status
    response = requests.get(f"{BASE_URL}/api/v1/subscription/status", headers=headers)
    print(f"  GET /api/v1/subscription/status - Status: {response.status_code}")
    if response.status_code != 500:
        print("    ✅ No JSON serialization error!")


def main():
    """Run all tests."""
    print("="*60)
    print("🧪 TESTING ALL FIXES")
    print("="*60)
    
    test_health_endpoints()
    test_influx_search()
    test_chaturbate_demo()
    test_auth_endpoints()
    
    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60)


if __name__ == "__main__":
    main()
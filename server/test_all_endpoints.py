#!/usr/bin/env python3
"""Test all API endpoints systematically."""

import json
import requests
from typing import Dict, List, Optional, Tuple
import sys

BASE_URL = "http://localhost:5000"
API_PREFIX = "/api/v1"

# Dummy auth token (will fail auth validation but useful for testing error handling)
AUTH_HEADERS = {
    "Authorization": "Bearer dummy_token",
    "Content-Type": "application/json"
}

NO_AUTH_HEADERS = {
    "Content-Type": "application/json"
}


class EndpointTester:
    def __init__(self):
        self.results = []
        
    def test_endpoint(
        self, 
        method: str, 
        path: str, 
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        expected_status: Optional[int] = None,
        description: str = ""
    ) -> Tuple[bool, Dict]:
        """Test a single endpoint."""
        url = f"{BASE_URL}{API_PREFIX}{path}"
        headers = headers or NO_AUTH_HEADERS
        
        try:
            response = requests.request(
                method=method,
                url=url,
                json=data,
                headers=headers,
                timeout=5
            )
            
            success = True
            if expected_status:
                success = response.status_code == expected_status
            else:
                success = response.status_code < 500
            
            result = {
                "method": method,
                "path": path,
                "description": description,
                "status_code": response.status_code,
                "success": success,
                "response": response.text[:200] if response.text else "",
                "error": None
            }
            
        except Exception as e:
            result = {
                "method": method,
                "path": path,
                "description": description,
                "status_code": None,
                "success": False,
                "response": None,
                "error": str(e)
            }
            
        self.results.append(result)
        return result["success"], result
    
    def print_results(self):
        """Print test results summary."""
        print("\n" + "="*80)
        print("API ENDPOINT TEST RESULTS")
        print("="*80 + "\n")
        
        # Group by success/failure
        successful = [r for r in self.results if r["success"]]
        failed = [r for r in self.results if not r["success"]]
        
        print(f"✅ Successful: {len(successful)}")
        print(f"❌ Failed: {len(failed)}")
        print(f"📊 Total: {len(self.results)}")
        
        if successful:
            print("\n✅ SUCCESSFUL ENDPOINTS:")
            print("-" * 40)
            for result in successful:
                print(f"{result['method']:6} {result['path']:40} [{result['status_code']}] {result['description']}")
        
        if failed:
            print("\n❌ FAILED ENDPOINTS:")
            print("-" * 40)
            for result in failed:
                status = result['status_code'] or 'ERR'
                error = result['error'] or result['response'][:100]
                print(f"{result['method']:6} {result['path']:40} [{status}] {result['description']}")
                print(f"       Error: {error}")
        
        print("\n" + "="*80)
        return len(failed) == 0


def main():
    """Run all endpoint tests."""
    tester = EndpointTester()
    
    # Health check (no API prefix)
    tester.test_endpoint("GET", "", description="Health check", expected_status=200)
    
    # Actually test root without API prefix
    response = requests.get(f"{BASE_URL}/")
    if response.status_code == 200:
        print("✅ Health check at / working")
    
    # Auth endpoints (require valid JWT)
    tester.test_endpoint("GET", "/auth/profile", headers=AUTH_HEADERS, description="Get user profile")
    tester.test_endpoint("GET", "/auth/usage", headers=AUTH_HEADERS, description="Get usage stats")
    tester.test_endpoint("GET", "/auth/pricing", description="Get pricing info (no auth)")
    
    # Translation endpoint
    tester.test_endpoint(
        "POST", "/translate/",
        data={"text": "Hello", "to_lang": "es", "from_lang": "en"},
        headers=AUTH_HEADERS,
        description="Translate text"
    )
    
    # Reply endpoint
    tester.test_endpoint(
        "POST", "/reply/",
        data={"original_text": "How are you?", "response_idea": "I'm fine", "style": "friendly", "to_lang": "en"},
        headers=AUTH_HEADERS,
        description="Generate reply"
    )
    
    # Write endpoint
    tester.test_endpoint(
        "POST", "/write/",
        data={"style": "casual", "text": "Thank you", "to_lang": "en"},
        headers=AUTH_HEADERS,
        description="Generate text"
    )
    
    # InfluxDB endpoints (no auth required for some)
    tester.test_endpoint(
        "POST", "/influx/tips",
        data={"broadcaster": "testuser", "days": 7},
        description="Get total tips"
    )
    
    tester.test_endpoint(
        "POST", "/influx/tippers",
        data={"broadcaster": "testuser", "days": 7, "limit": 10},
        description="Get top tippers"
    )
    
    tester.test_endpoint(
        "POST", "/influx/chatters",
        data={"broadcaster": "testuser", "days": 7, "limit": 10},
        description="Get top chatters"
    )
    
    tester.test_endpoint(
        "POST", "/influx/search",
        data={
            "filters": {"method": "tip"},
            "range": {"start": "-7d", "stop": "now()"},
            "fields": ["_time", "_value", "method"],
            "limit": 10
        },
        description="Search InfluxDB"
    )
    
    # Chaturbate endpoints
    tester.test_endpoint("GET", "/chaturbate/status", description="Get Chaturbate status")
    tester.test_endpoint(
        "POST", "/chaturbate/start",
        data={"demo_mode": True},
        description="Start Chaturbate client"
    )
    tester.test_endpoint("POST", "/chaturbate/stop", description="Stop Chaturbate client")
    
    # Chaturbate events endpoints
    tester.test_endpoint(
        "GET", "/chaturbate/events/testuser/recent?limit=5",
        headers=AUTH_HEADERS,
        description="Get recent events"
    )
    
    tester.test_endpoint(
        "GET", "/chaturbate/events/testuser/stats",
        headers=AUTH_HEADERS,
        description="Get event stats"
    )
    
    tester.test_endpoint(
        "GET", "/chaturbate/events/testuser/top-tippers?days=7&limit=5",
        headers=AUTH_HEADERS,
        description="Get top tippers"
    )
    
    tester.test_endpoint(
        "GET", "/chaturbate/events/testuser/user/someuser",
        headers=AUTH_HEADERS,
        description="Get user events"
    )
    
    # Subscription endpoints
    tester.test_endpoint(
        "GET", "/subscription/status",
        headers=AUTH_HEADERS,
        description="Get subscription status"
    )
    
    tester.test_endpoint(
        "POST", "/subscription/checkout",
        data={
            "tier": "pro",
            "billing_cycle": "monthly",
            "success_url": "http://localhost/success",
            "cancel_url": "http://localhost/cancel"
        },
        headers=AUTH_HEADERS,
        description="Create checkout session"
    )
    
    tester.test_endpoint(
        "POST", "/subscription/billing-portal",
        data={"return_url": "http://localhost/return"},
        headers=AUTH_HEADERS,
        description="Create billing portal"
    )
    
    tester.test_endpoint(
        "POST", "/subscription/cancel",
        headers=AUTH_HEADERS,
        description="Cancel subscription"
    )
    
    # User stats endpoints
    tester.test_endpoint(
        "GET", "/user_stats/testuser",
        headers=AUTH_HEADERS,
        description="Get user stats"
    )
    
    tester.test_endpoint(
        "POST", "/user_stats/bulk",
        data={"usernames": ["user1", "user2", "user3"]},
        headers=AUTH_HEADERS,
        description="Get bulk user stats"
    )
    
    # Inbox endpoints
    tester.test_endpoint(
        "GET", "/inbox/conversations",
        headers=AUTH_HEADERS,
        description="Get conversations"
    )
    
    tester.test_endpoint(
        "GET", "/inbox/messages",
        headers=AUTH_HEADERS,
        description="Get messages"
    )
    
    tester.test_endpoint(
        "GET", "/inbox/stats",
        headers=AUTH_HEADERS,
        description="Get inbox stats"
    )
    
    # Print results
    all_passed = tester.print_results()
    
    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
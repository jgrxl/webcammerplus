#!/usr/bin/env python3

import os
import sys
sys.path.append('/Users/jovanlee/Documents/webcammer+/server')

from dotenv import load_dotenv
from services.stripe_service import StripeService

# Load environment variables
load_dotenv('/Users/jovanlee/Documents/webcammer+/server/.env')

def test_stripe_connection():
    """Test Stripe connection and configuration."""
    
    print("🧪 Testing Stripe Integration...")
    print(f"📋 Stripe Secret Key: {os.getenv('STRIPE_SECRET_KEY', 'Not found')[:20]}...")
    print(f"📋 Stripe Publishable Key: {os.getenv('STRIPE_PUBLISHABLE_KEY', 'Not found')[:20]}...")
    
    try:
        # Initialize Stripe service
        stripe_service = StripeService()
        print("✅ Stripe service initialized successfully")
        
        # Test getting pricing info
        pricing = stripe_service.get_pricing_info()
        print("✅ Pricing information retrieved:")
        
        for tier, data in pricing.items():
            print(f"   💰 {data['display_name']}: ${data['monthly_price']}/month")
        
        # Test creating a test customer
        test_customer = stripe_service.create_customer(
            user_email="test@example.com",
            user_name="Test User",
            auth0_id="test_auth0_id"
        )
        
        print(f"✅ Test customer created: {test_customer.id}")
        
        # Clean up - delete test customer
        import stripe
        stripe.Customer.delete(test_customer.id)
        print("🧹 Test customer cleaned up")
        
        print("\n🎉 Stripe integration is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Stripe integration failed: {e}")
        return False

if __name__ == "__main__":
    test_stripe_connection()
#!/usr/bin/env python3
"""Test current user endpoint to get the actual Auth0 ID"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv

load_dotenv()

from datetime import datetime

from influxdb_client import Point

from client.influx_client import InfluxDBClient


def create_test_private_message():
    """Create a test private message for the current user"""
    print("📝 Creating test private message...")

    try:
        client = InfluxDBClient()
        write_api = client.write_api

        # Let's create messages for multiple possible user IDs to ensure we catch the right one
        test_user_ids = [
            "google-oauth2|117635624388576127987",  # Current hardcoded ID
            "google-oauth2|1234567890",  # Generic Google ID
            "auth0|jovangiannilee",  # Auth0 username format
            "jovangiannilee",  # Simple username
        ]

        for user_id in test_user_ids:
            point = (
                Point("chaturbate_events")
                .tag("method", "privateMessage")
                .tag("from_user", "TestSender")
                .tag("to_user", user_id)
                .tag("is_read", "false")
                .field("object.user.username", "TestSender")
                .field("object.message", f"Test message for user {user_id}")
                .field("from_user", "TestSender")
                .field("to_user", user_id)
                .time(datetime.utcnow())
            )

            write_api.write(
                bucket=client.bucket,
                org=client.org,
                record=point,
            )
            print(f"✅ Created test message for: {user_id}")

        print("\n🎯 Now try the inbox API to see which user ID works!")

    except Exception as e:
        print(f"❌ Error creating test messages: {e}")


if __name__ == "__main__":
    create_test_private_message()

#!/usr/bin/env python3
"""Test script to manually write data to InfluxDB and verify the tippers endpoint"""

from datetime import datetime

from dotenv import load_dotenv
from influxdb_client import Point

from client.influx_client import InfluxDBClient

# Load environment variables
load_dotenv()


def test_influx_write():
    """Test writing tip data to InfluxDB"""
    try:
        # Initialize client
        client = InfluxDBClient()
        write_api = client.write_api

        # Create test tip events
        test_tips = [
            ("WhaleKing", 1000, "Great show!"),
            ("DiamondHands", 500, "Thanks!"),
            ("LoyalFan", 250, "Keep it up!"),
            ("WhaleKing", 750, "Amazing!"),
            ("NewSupporter", 100, "First tip!"),
            ("DiamondHands", 300, "Love it!"),
            ("LoyalFan", 150, ""),
        ]

        for username, amount, message in test_tips:
            point = (
                Point("chaturbate_events")
                .tag("method", "tip")
                .tag("username", username)
                .field("object.tip.tokens", amount)
                .field("object.user.username", username)
                .field("object.tip.message", message)
                .time(datetime.now())
            )

            write_api.write(bucket=client.bucket, org=client.org, record=point)
            print(f"✅ Wrote tip: {username} - {amount} tokens")

        # Flush and close
        write_api.close()
        client.close()
        print(f"✅ Successfully wrote {len(test_tips)} test tip events to InfluxDB")

    except Exception as e:
        print(f"❌ Error writing to InfluxDB: {e}")


if __name__ == "__main__":
    test_influx_write()

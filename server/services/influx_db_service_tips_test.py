#!/usr/bin/env python3
"""Test script to specifically query tip data"""


from dotenv import load_dotenv

from client.influx_client import InfluxDBClient

# Load environment variables
load_dotenv()


def test_tip_query():
    """Test querying tip data specifically"""
    try:
        client = InfluxDBClient()

        # Test query specifically for tip events
        print("=== Querying specifically for tip events ===")
        query = """
            from(bucket: "chaturbate_events")
            |> range(start: -30d)
            |> filter(fn: (r) => r._measurement == "chaturbate_events" and r.method == "tip")
            |> limit(n: 10)
        """

        tables = client.query_api.query(query=query, org=client.org)
        print(f"Number of tip tables returned: {len(tables)}")

        for table in tables:
            print(f"Table: {table}")
            for record in table.records:
                print(f"Tip record: {record.values}")

        # Also test with a different time range
        print("\n=== Querying with different time range ===")
        query2 = """
            from(bucket: "chaturbate_events")
            |> range(start: 0)
            |> filter(fn: (r) => r._measurement == "chaturbate_events" and r.method == "tip")
            |> limit(n: 20)
        """

        tables2 = client.query_api.query(query=query2, org=client.org)
        print(f"Number of tip tables returned (all time): {len(tables2)}")

        for table in tables2:
            print(f"Table: {table}")
            for record in table.records:
                print(f"Tip record: {record.values}")

        client.close()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_tip_query()

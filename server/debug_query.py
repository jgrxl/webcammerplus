#!/usr/bin/env python3
"""Debug the get_top_tippers query"""

import os

from dotenv import load_dotenv

from client.influx_client import InfluxDBClient
from utils.query_builder import AggregateFunction, FluxQueryBuilder

# Load environment variables
load_dotenv()


def debug_tippers_query():
    """Debug the exact query used by get_top_tippers"""
    try:
        client = InfluxDBClient()

        # This is the exact query being used by get_top_tippers
        flux_query = (
            FluxQueryBuilder()
            .from_bucket(client.bucket)
            .range("-1d")
            .measurement("chaturbate_events")
            .filter("method", "==", "tip")
            .field("object.tip.tokens")
            .filter("_value", ">", "0")
            .custom('filter(fn: (r) => exists r.username and r.username != "")')
            .group_by(["username"])
            .aggregate(AggregateFunction.SUM)
            .sort("_value", desc=True)
            .limit(10)
            .build()
        )

        print("=== Generated Flux Query ===")
        print(flux_query)
        print("\n=== Executing Query ===")

        tables = client.query_api.query(query=flux_query, org=client.org)
        print(f"Number of tables returned: {len(tables)}")

        for i, table in enumerate(tables):
            print(f"\nTable {i}: {table}")
            for record in table.records:
                print(f"  Record: {record.values}")

        # Also test a simpler version
        print("\n=== Testing Simpler Query ===")
        simple_query = """
            from(bucket: "chaturbate_events")
            |> range(start: -1d)
            |> filter(fn: (r) => r._measurement == "chaturbate_events" and r.method == "tip" and r._field == "object.tip.tokens")
            |> filter(fn: (r) => r._value > 0)
            |> group(columns: ["username"])
            |> sum()
            |> sort(columns: ["_value"], desc: true)
            |> limit(n: 10)
        """

        print("Simple query:")
        print(simple_query)

        tables2 = client.query_api.query(query=simple_query, org=client.org)
        print(f"Simple query - Number of tables returned: {len(tables2)}")

        for i, table in enumerate(tables2):
            print(f"\nSimple Table {i}: {table}")
            for record in table.records:
                print(f"  Simple Record: {record.values}")

        client.close()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    debug_tippers_query()

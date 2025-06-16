#!/usr/bin/env python3
"""Test script to debug the InfluxDB query"""

import os
from dotenv import load_dotenv
from client.influx_client import InfluxDBClient
from services.influx_db_service import InfluxDBService

# Load environment variables
load_dotenv()

def test_query():
    """Test querying tip data from InfluxDB"""
    try:
        # Initialize client and service
        client = InfluxDBClient()
        service = InfluxDBService(client, client.bucket)
        
        print(f"InfluxDB URL: {client.url}")
        print(f"Bucket: {client.bucket}")
        print(f"Org: {client.org}")
        
        # Test the get_top_tippers method
        print("\n=== Testing get_top_tippers method ===")
        result = service.get_top_tippers(days=1, limit=10)
        print(f"Success: {result.success}")
        print(f"Days: {result.days}")
        print(f"Error: {result.error}")
        print(f"Tippers count: {len(result.tippers)}")
        
        for i, tipper in enumerate(result.tippers):
            print(f"  {i+1}. {tipper.username}: {tipper.total_tokens} tokens")
            
        # Test raw query
        print("\n=== Testing raw InfluxDB query ===")
        query = '''
            from(bucket: "chaturbate_events")
            |> range(start: -1d)
            |> filter(fn: (r) => r._measurement == "chaturbate_events")
            |> limit(n: 10)
        '''
        
        tables = service.query_api.query(query=query, org=service.org)
        print(f"Number of tables returned: {len(tables)}")
        
        for table in tables:
            print(f"Table: {table}")
            for record in table.records:
                print(f"Record: {record.values}")
                
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_query()
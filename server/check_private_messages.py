#!/usr/bin/env python3
"""Check if private messages are being generated in InfluxDB"""

from dotenv import load_dotenv
load_dotenv()

from client.influx_client import InfluxDBClient

def check_private_messages():
    print("🔍 Checking Private Messages in InfluxDB")
    print("=" * 50)
    
    try:
        client = InfluxDBClient()
        query_api = client.query_api
        
        # Query for all private messages
        query = f'''
            from(bucket: "{client.bucket}")
                |> range(start: -1h)
                |> filter(fn: (r) => r["_measurement"] == "chaturbate_events")
                |> filter(fn: (r) => r["method"] == "privateMessage")
                |> limit(n: 10)
        '''
        
        print("Running query for private messages...")
        result = query_api.query(org=client.org, query=query)
        
        message_count = 0
        for table in result:
            for record in table.records:
                message_count += 1
                print(f"Private Message {message_count}:")
                print(f"  Time: {record.get_time()}")
                print(f"  From: {record.values.get('from_user', 'Unknown')}")
                print(f"  To: {record.values.get('to_user', 'Unknown')}")
                print(f"  Message: {record.values.get('object.message', 'No message')}")
                print(f"  Read: {record.values.get('is_read', 'Unknown')}")
                print("-" * 30)
        
        if message_count == 0:
            print("❌ No private messages found in InfluxDB")
            
            # Check for any chaturbate events at all
            all_events_query = f'''
                from(bucket: "{client.bucket}")
                    |> range(start: -1h)
                    |> filter(fn: (r) => r["_measurement"] == "chaturbate_events")
                    |> group(columns: ["method"])
                    |> count()
            '''
            
            print("\nChecking all Chaturbate events...")
            all_result = query_api.query(org=client.org, query=all_events_query)
            
            for table in all_result:
                for record in table.records:
                    method = record.values.get('method', 'Unknown')
                    count = record.get_value()
                    print(f"  {method}: {count} events")
        else:
            print(f"✅ Found {message_count} private messages")
            
    except Exception as e:
        print(f"❌ Error checking private messages: {e}")

if __name__ == "__main__":
    check_private_messages()
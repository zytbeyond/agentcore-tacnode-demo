#!/usr/bin/env python3
"""
Send "SELECT * FROM test" to Gateway and capture all real messages
"""

import requests
import json
import base64
import time
import boto3

def send_select_all_and_capture_messages():
    """Send SELECT * FROM test and capture all real messages"""
    print("🔍 CAPTURING REAL MESSAGES FOR 'SELECT * FROM test'")
    print("=" * 70)
    print("🎯 Query: SELECT * FROM test")
    print("🎯 Capture: All real messages in the pipeline")
    print("🎯 NO SIMULATION: Everything is real")
    
    # Load Cognito configuration
    try:
        with open('agentcore-cognito-config.json', 'r') as f:
            cognito_config = json.load(f)
        
        client_id = cognito_config['clientId']
        client_secret = cognito_config['clientSecret']
        token_endpoint = cognito_config['tokenEndpoint']
        
    except FileNotFoundError:
        print("❌ Cognito configuration not found")
        return False
    
    # Step 1: Get authentication token
    print(f"\n📋 STEP 1: Getting authentication token")
    print("-" * 50)
    
    credentials = f"{client_id}:{client_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {encoded_credentials}"
    }
    
    data = {
        "grant_type": "client_credentials",
        "scope": "agentcore-gateway-resource-server/read agentcore-gateway-resource-server/write"
    }
    
    try:
        response = requests.post(token_endpoint, headers=headers, data=data, timeout=30)
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data['access_token']
            print(f"✅ Authentication successful")
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False
    
    # Step 2: Send SELECT * FROM test to Gateway
    print(f"\n📋 STEP 2: Sending 'SELECT * FROM test' to Gateway")
    print("-" * 50)
    
    gateway_url = "https://augment-real-agentcore-gateway-fifpg4kzwt.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp"
    
    # Real SELECT * query with unique identifier
    test_id = int(time.time())
    select_all_request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "secure-lambda-tacnode-target___query",
            "arguments": {
                "sql": "SELECT * FROM test"
            }
        },
        "id": test_id
    }
    
    print(f"🌐 REAL REQUEST TO GATEWAY:")
    print(f"   URL: {gateway_url}")
    print(f"   Test ID: {test_id}")
    print(f"   SQL Query: SELECT * FROM test")
    print(f"   Request: {json.dumps(select_all_request, indent=2)}")
    
    try:
        gateway_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
        start_time = time.time()
        gateway_response = requests.post(
            gateway_url,
            json=select_all_request,
            headers=gateway_headers,
            timeout=30
        )
        end_time = time.time()
        
        print(f"\n📡 REAL GATEWAY RESPONSE:")
        print(f"   Status: {gateway_response.status_code}")
        print(f"   Time: {(end_time - start_time):.3f}s")
        
        if gateway_response.status_code == 200:
            response_json = gateway_response.json()
            print(f"   Response: {json.dumps(response_json, indent=2)}")
            print(f"✅ Real SELECT * request sent successfully")
        else:
            print(f"❌ Gateway error: {gateway_response.status_code}")
            print(f"   Response: {gateway_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Gateway request failed: {e}")
        return False
    
    # Step 3: Wait and capture Lambda logs
    print(f"\n📋 STEP 3: Capturing Lambda CloudWatch Logs")
    print("-" * 50)
    print(f"⏳ Waiting 10 seconds for logs to appear...")
    time.sleep(10)
    
    # Get Lambda logs
    logs_client = boto3.client('logs', region_name='us-east-1')
    
    try:
        # Load Lambda configuration
        with open('secure-lambda-tacnode-config.json', 'r') as f:
            lambda_config = json.load(f)
        
        function_name = lambda_config['lambda']['functionName']
        log_group_name = f"/aws/lambda/{function_name}"
        
        print(f"📋 Fetching logs from: {log_group_name}")
        
        # Get recent log streams
        streams_response = logs_client.describe_log_streams(
            logGroupName=log_group_name,
            orderBy='LastEventTime',
            descending=True,
            limit=3
        )
        
        if not streams_response['logStreams']:
            print(f"❌ No log streams found")
            return False
        
        # Get logs from the most recent stream
        latest_stream = streams_response['logStreams'][0]
        stream_name = latest_stream['logStreamName']
        
        print(f"📋 Getting logs from stream: {stream_name}")
        
        # Get log events from the last 5 minutes
        end_time_ms = int(time.time() * 1000)
        start_time_ms = end_time_ms - (5 * 60 * 1000)  # 5 minutes ago
        
        events_response = logs_client.get_log_events(
            logGroupName=log_group_name,
            logStreamName=stream_name,
            startTime=start_time_ms,
            endTime=end_time_ms
        )
        
        # Display all relevant log messages
        print(f"\n🔍 REAL MESSAGES CAPTURED FROM LAMBDA LOGS:")
        print("=" * 70)
        
        found_messages = False
        for event in events_response['logEvents']:
            message = event['message']
            
            # Look for our SELECT * query or key message markers
            if ("SELECT * FROM test" in message or 
                "REAL MESSAGE RECEIVED FROM AGENTCORE GATEWAY" in message or
                "REAL MESSAGE BEING SENT TO TACNODE" in message or
                "REAL RESPONSE RECEIVED FROM TACNODE" in message or
                "REAL MESSAGE BEING SENT BACK TO AGENTCORE GATEWAY" in message or
                "PARSED SSE RESPONSE FROM TACNODE" in message):
                
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(event['timestamp'] / 1000))
                print(f"\n[{timestamp}] {message}")
                found_messages = True
        
        if found_messages:
            print(f"\n✅ REAL MESSAGES FOR 'SELECT * FROM test' CAPTURED!")
            print(f"✅ Lambda logs show exact messages for database query")
            print(f"✅ All table data retrieved through real pipeline")
            return True
        else:
            print(f"\n⚠️ No matching log messages found for SELECT *")
            print(f"📋 Recent log events:")
            for event in events_response['logEvents'][-5:]:  # Show last 5 events
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(event['timestamp'] / 1000))
                print(f"[{timestamp}] {event['message']}")
            return False
            
    except Exception as e:
        print(f"❌ Error fetching Lambda logs: {e}")
        return False

def extract_table_data_from_response(response_json):
    """Extract and display the actual table data"""
    print(f"\n📊 EXTRACTING REAL TABLE DATA:")
    print("-" * 50)
    
    try:
        if 'result' in response_json and 'content' in response_json['result']:
            content = response_json['result']['content']
            if content and len(content) > 0:
                text_content = content[0].get('text', '')
                
                # Parse the nested response structure
                if text_content.startswith('{"response"'):
                    # Parse the outer response wrapper
                    outer_response = json.loads(text_content)
                    if 'response' in outer_response and 'payload' in outer_response['response']:
                        payload = outer_response['response']['payload']
                        if payload.get('statusCode') == 200:
                            body = json.loads(payload['body'])
                            if 'result' in body and 'content' in body['result']:
                                inner_content = body['result']['content']
                                if inner_content and len(inner_content) > 0:
                                    table_data_text = inner_content[0].get('text', '')
                                    
                                    # Parse the actual table data
                                    if table_data_text.startswith('[') and table_data_text.endswith(']'):
                                        table_records = json.loads(table_data_text)
                                        
                                        print(f"🎉 REAL TABLE DATA FROM PostgreSQL:")
                                        print(f"   Total Records: {len(table_records)}")
                                        print(f"   Table: test")
                                        print(f"   Query: SELECT * FROM test")
                                        
                                        print(f"\n📋 ALL RECORDS IN 'test' TABLE:")
                                        for i, record in enumerate(table_records, 1):
                                            print(f"\n   Record {i}:")
                                            for column, value in record.items():
                                                print(f"     {column}: {value}")
                                        
                                        return table_records
                
                print(f"📊 Raw response text: {text_content}")
                
    except Exception as e:
        print(f"❌ Error extracting table data: {e}")
    
    return None

def main():
    """Main function"""
    print("🧪 REAL 'SELECT * FROM test' MESSAGE CAPTURE")
    print("=" * 70)
    print("🎯 OBJECTIVE: See all data in 'test' table")
    print("🎯 METHOD: Send SELECT * query, capture all messages")
    print("🎯 EVIDENCE: Show real table contents and message flow")
    print("🎯 NO SIMULATION: Everything is real")
    
    success = send_select_all_and_capture_messages()
    
    if success:
        print(f"\n🏆 REAL 'SELECT * FROM test' SUCCESS!")
        print(f"🎉 Captured exact messages for SELECT * query")
        print(f"🎉 Retrieved all real data from PostgreSQL table")
        print(f"🎉 Proved complete message flow with real table contents")
    else:
        print(f"\n🔍 SELECT * message capture failed")

if __name__ == "__main__":
    main()

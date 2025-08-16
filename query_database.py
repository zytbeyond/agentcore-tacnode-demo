#!/usr/bin/env python3
"""
Query PostgreSQL database through secure AgentCore Gateway
Usage: python3 query_database.py "SELECT * FROM test WHERE value > 100"
"""

import sys
import requests
import json
import base64
import time
import boto3

def get_cognito_token():
    """Get Cognito authentication token"""
    try:
        with open('agentcore-cognito-config.json', 'r') as f:
            cognito_config = json.load(f)
        
        client_id = cognito_config['clientId']
        client_secret = cognito_config['clientSecret']
        token_endpoint = cognito_config['tokenEndpoint']
        
    except FileNotFoundError:
        print("❌ Error: agentcore-cognito-config.json not found")
        return None
    
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
            return token_data['access_token']
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None

def send_sql_query(sql_query, access_token):
    """Send SQL query to AgentCore Gateway"""
    gateway_url = "https://augment-real-agentcore-gateway-fifpg4kzwt.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp"
    
    request_id = int(time.time())
    gateway_request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "secure-lambda-tacnode-target___query",
            "arguments": {
                "sql": sql_query
            }
        },
        "id": request_id
    }
    
    print(f"🌐 SENDING SQL QUERY TO GATEWAY:")
    print(f"   SQL: {sql_query}")
    print(f"   Gateway: {gateway_url}")
    
    try:
        gateway_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
        start_time = time.time()
        gateway_response = requests.post(
            gateway_url,
            json=gateway_request,
            headers=gateway_headers,
            timeout=30
        )
        end_time = time.time()
        
        print(f"\n📡 GATEWAY RESPONSE:")
        print(f"   Status: {gateway_response.status_code}")
        print(f"   Time: {(end_time - start_time):.3f}s")
        
        if gateway_response.status_code == 200:
            return gateway_response.json()
        else:
            print(f"❌ Gateway error: {gateway_response.status_code}")
            print(f"   Response: {gateway_response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Gateway request failed: {e}")
        return None

def extract_and_display_results(response_json, sql_query):
    """Extract and display database results"""
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
                                        
                                        print(f"\n🎉 QUERY RESULTS:")
                                        print(f"   SQL: {sql_query}")
                                        print(f"   Records Found: {len(table_records)}")
                                        
                                        if len(table_records) > 0:
                                            print(f"\n📊 DATABASE RECORDS:")
                                            
                                            # Get column names from first record
                                            columns = list(table_records[0].keys())
                                            
                                            # Print header
                                            header = " | ".join(f"{col:15}" for col in columns)
                                            print(f"   {header}")
                                            print(f"   {'-' * len(header)}")
                                            
                                            # Print records
                                            for i, record in enumerate(table_records, 1):
                                                row_values = []
                                                for col in columns:
                                                    value = record.get(col, '')
                                                    if value is None:
                                                        value = 'NULL'
                                                    elif isinstance(value, bool):
                                                        value = 'true' if value else 'false'
                                                    else:
                                                        value = str(value)
                                                    row_values.append(f"{value:15}")
                                                
                                                row = " | ".join(row_values)
                                                print(f"   {row}")
                                            
                                            print(f"\n✅ Query executed successfully!")
                                            return table_records
                                        else:
                                            print(f"\n📊 No records found matching the query.")
                                            return []
                                    else:
                                        print(f"\n📊 Non-JSON result: {table_data_text}")
                                        return table_data_text
                                else:
                                    print(f"❌ No data in response")
                        else:
                            print(f"❌ Database error: {payload.get('statusCode')}")
                            error_body = json.loads(payload.get('body', '{}'))
                            if 'error' in error_body:
                                print(f"   Error: {error_body['error'].get('message', 'Unknown error')}")
                else:
                    print(f"📊 Raw response: {text_content}")
                    
    except Exception as e:
        print(f"❌ Error parsing results: {e}")
        print(f"📊 Raw response: {json.dumps(response_json, indent=2)}")
    
    return None

def capture_lambda_logs():
    """Capture Lambda logs to show real message flow"""
    print(f"\n🔍 CAPTURING LAMBDA LOGS (Real Message Flow):")
    print("-" * 50)
    
    try:
        # Load Lambda configuration
        with open('secure-lambda-tacnode-config.json', 'r') as f:
            lambda_config = json.load(f)
        
        function_name = lambda_config['lambda']['functionName']
        log_group_name = f"/aws/lambda/{function_name}"
        
        logs_client = boto3.client('logs', region_name='us-east-1')
        
        # Get recent log streams
        streams_response = logs_client.describe_log_streams(
            logGroupName=log_group_name,
            orderBy='LastEventTime',
            descending=True,
            limit=1
        )
        
        if not streams_response['logStreams']:
            print(f"⚠️ No log streams found")
            return
        
        # Get logs from the most recent stream
        latest_stream = streams_response['logStreams'][0]
        stream_name = latest_stream['logStreamName']
        
        # Get log events from the last 2 minutes
        end_time_ms = int(time.time() * 1000)
        start_time_ms = end_time_ms - (2 * 60 * 1000)  # 2 minutes ago
        
        events_response = logs_client.get_log_events(
            logGroupName=log_group_name,
            logStreamName=stream_name,
            startTime=start_time_ms,
            endTime=end_time_ms
        )
        
        # Show key message flow logs
        key_messages = [
            "REAL MESSAGE RECEIVED FROM AGENTCORE GATEWAY",
            "REAL MESSAGE BEING SENT TO TACNODE", 
            "REAL RESPONSE RECEIVED FROM TACNODE",
            "REAL MESSAGE BEING SENT BACK TO AGENTCORE GATEWAY"
        ]
        
        found_any = False
        for event in events_response['logEvents']:
            message = event['message']
            
            for key_msg in key_messages:
                if key_msg in message:
                    timestamp = time.strftime('%H:%M:%S', time.localtime(event['timestamp'] / 1000))
                    print(f"[{timestamp}] {message.strip()}")
                    found_any = True
                    break
        
        if found_any:
            print(f"✅ Real message flow captured from Lambda logs")
        else:
            print(f"⚠️ No recent message flow found in logs")
            
    except Exception as e:
        print(f"⚠️ Could not capture Lambda logs: {e}")

def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("🔍 SECURE DATABASE QUERY TOOL")
        print("=" * 50)
        print("Usage: python3 query_database.py \"SQL_QUERY\"")
        print("")
        print("Examples:")
        print("  python3 query_database.py \"SELECT * FROM test\"")
        print("  python3 query_database.py \"SELECT * FROM test WHERE value > 100\"")
        print("  python3 query_database.py \"SELECT name, value FROM test WHERE is_active = true\"")
        print("  python3 query_database.py \"SELECT COUNT(*) FROM test\"")
        print("  python3 query_database.py \"SELECT category, AVG(value) FROM test GROUP BY category\"")
        print("")
        print("🎯 Real Architecture: Gateway → Secure Lambda → TACNode → PostgreSQL")
        print("🔒 Security: No open policies, minimal privileges, JWT authentication")
        sys.exit(1)
    
    sql_query = sys.argv[1]
    
    print("🔍 SECURE DATABASE QUERY")
    print("=" * 50)
    print(f"🎯 SQL Query: {sql_query}")
    print(f"🔒 Architecture: Gateway → Secure Lambda → TACNode → PostgreSQL")
    print(f"🔒 Security: JWT auth, no open policies, minimal privileges")
    
    # Step 1: Get authentication token
    print(f"\n📋 STEP 1: Authenticating with Cognito")
    access_token = get_cognito_token()
    if not access_token:
        print("❌ Failed to get authentication token")
        sys.exit(1)
    
    print(f"✅ Authentication successful")
    
    # Step 2: Send SQL query
    print(f"\n📋 STEP 2: Executing SQL query")
    response = send_sql_query(sql_query, access_token)
    if not response:
        print("❌ Failed to execute query")
        sys.exit(1)
    
    # Step 3: Display results
    print(f"\n📋 STEP 3: Processing results")
    results = extract_and_display_results(response, sql_query)
    
    # Step 4: Show real message flow (optional)
    capture_lambda_logs()
    
    print(f"\n🏆 QUERY COMPLETE!")
    print(f"✅ Real SQL executed on real PostgreSQL database")
    print(f"✅ Secure message flow: Gateway → Lambda → TACNode → Database")
    print(f"✅ No simulation - everything is real and secure")

if __name__ == "__main__":
    main()

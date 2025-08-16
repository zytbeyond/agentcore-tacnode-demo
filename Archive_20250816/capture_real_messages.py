#!/usr/bin/env python3
"""
Send real request to Gateway and capture exact messages from Lambda logs
"""

import requests
import json
import base64
import time
import boto3

def send_real_request_and_capture_messages():
    """Send real request to Gateway and capture Lambda logs"""
    print("🔍 CAPTURING REAL MESSAGES FROM LAMBDA")
    print("=" * 70)
    print("🎯 Step 1: Send real request to AgentCore Gateway")
    print("🎯 Step 2: Capture exact messages from Lambda CloudWatch Logs")
    print("🎯 NO SIMULATION: All messages are real")
    
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
    
    # Step 2: Send real request to Gateway
    print(f"\n📋 STEP 2: Sending real request to Gateway")
    print("-" * 50)
    
    gateway_url = "https://augment-real-agentcore-gateway-fifpg4kzwt.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp"
    
    # Real request with unique identifier to find in logs
    test_id = int(time.time())
    real_request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "secure-lambda-tacnode-target___query",
            "arguments": {
                "sql": f"SELECT 'MESSAGE_CAPTURE_TEST_{test_id}' as test_identifier, 'REAL_GATEWAY_REQUEST' as source, 'LAMBDA_LOGGING_ENABLED' as logging_status, NOW() as request_timestamp, COUNT(*) as record_count FROM test"
            }
        },
        "id": test_id
    }
    
    print(f"🌐 REAL REQUEST TO GATEWAY:")
    print(f"   URL: {gateway_url}")
    print(f"   Test ID: {test_id}")
    print(f"   Request: {json.dumps(real_request, indent=2)}")
    
    try:
        gateway_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
        start_time = time.time()
        gateway_response = requests.post(
            gateway_url,
            json=real_request,
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
            print(f"✅ Real request sent successfully")
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
        
        # Filter and display relevant log messages
        print(f"\n🔍 REAL MESSAGES CAPTURED FROM LAMBDA LOGS:")
        print("=" * 70)
        
        found_messages = False
        for event in events_response['logEvents']:
            message = event['message']
            
            # Look for our test identifier or key message markers
            if (f"MESSAGE_CAPTURE_TEST_{test_id}" in message or 
                "REAL MESSAGE RECEIVED FROM AGENTCORE GATEWAY" in message or
                "REAL MESSAGE BEING SENT TO TACNODE" in message or
                "REAL RESPONSE RECEIVED FROM TACNODE" in message or
                "REAL MESSAGE BEING SENT BACK TO AGENTCORE GATEWAY" in message):
                
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(event['timestamp'] / 1000))
                print(f"\n[{timestamp}] {message}")
                found_messages = True
        
        if found_messages:
            print(f"\n✅ REAL MESSAGES SUCCESSFULLY CAPTURED!")
            print(f"✅ Lambda logs show exact messages received and sent")
            print(f"✅ No simulation - all messages are real")
            return True
        else:
            print(f"\n⚠️ No matching log messages found")
            print(f"📋 All recent log events:")
            for event in events_response['logEvents'][-10:]:  # Show last 10 events
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(event['timestamp'] / 1000))
                print(f"[{timestamp}] {event['message']}")
            return False
            
    except Exception as e:
        print(f"❌ Error fetching Lambda logs: {e}")
        return False

def main():
    """Main function"""
    print("🧪 REAL MESSAGE CAPTURE TEST")
    print("=" * 70)
    print("🎯 OBJECTIVE: Capture exact real messages from Lambda")
    print("🎯 METHOD: Send real Gateway request, check Lambda logs")
    print("🎯 EVIDENCE: Show actual messages received and sent")
    print("🎯 NO SIMULATION: Everything is real and logged")
    
    success = send_real_request_and_capture_messages()
    
    if success:
        print(f"\n🏆 REAL MESSAGE CAPTURE SUCCESS!")
        print(f"🎉 Captured exact messages from Lambda CloudWatch Logs")
        print(f"🎉 Proved real Gateway → Lambda → TACNode message flow")
        print(f"🎉 No simulation - all messages are real and captured")
    else:
        print(f"\n🔍 Message capture failed - check logs manually")

if __name__ == "__main__":
    main()

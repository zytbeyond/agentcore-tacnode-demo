#!/usr/bin/env python3
"""
Debug the OpenAPI format and request structure
"""

import asyncio
import httpx
import json
import requests
import base64

async def debug_openapi_format():
    """Debug different OpenAPI formats and request structures"""
    print("🔧 DEBUGGING OPENAPI FORMAT AND REQUEST STRUCTURE")
    print("=" * 70)
    
    # Get Cognito token
    cognito_config = {
        "userPoolId": "us-east-1_qVOK14gn5",
        "clientId": "629cm5j58a7o0lhh1qph1re0l5",
        "clientSecret": "t7uo744afdgrlasjgqe0rsdasdm8ovg91otr12guk4jq79c3d64",
        "tokenEndpoint": "https://us-east-1-qvok14gn5.auth.us-east-1.amazoncognito.com/oauth2/token"
    }
    
    client_id = cognito_config['clientId']
    client_secret = cognito_config['clientSecret']
    token_endpoint = cognito_config['tokenEndpoint']
    
    credentials = f"{client_id}:{client_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {encoded_credentials}"
    }
    
    data = {
        "grant_type": "client_credentials",
        "scope": "gateway-resource-server/read gateway-resource-server/write"
    }
    
    response = requests.post(token_endpoint, headers=headers, data=data, timeout=30)
    
    if response.status_code != 200:
        print(f"❌ Failed to get token: {response.status_code}")
        return
    
    token_data = response.json()
    access_token = token_data['access_token']
    print(f"✅ Got Cognito token")
    
    # Test different request formats
    gateway_url = "https://pureawstacnodegateway-l0f1tg5t8o.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp"
    tool_name = "identity-tacnode-target___executeQuery"
    
    gateway_headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Test 1: Simple direct arguments (like TACNode expects)
    print(f"\n📋 TEST 1: Simple direct arguments")
    test1_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": {
                "sql": "SELECT 'test1' as format_test"
            }
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(gateway_url, json=test1_request, headers=gateway_headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                response_json = response.json()
                print(f"Response: {json.dumps(response_json, indent=2)}")
                
                if 'result' in response_json and not response_json['result'].get('isError', False):
                    print(f"✅ TEST 1 SUCCESS!")
                    return True
            else:
                print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Full JSON-RPC wrapper (current approach)
    print(f"\n📋 TEST 2: Full JSON-RPC wrapper")
    test2_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "query",
                    "arguments": {
                        "sql": "SELECT 'test2' as format_test"
                    }
                },
                "id": 1
            }
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(gateway_url, json=test2_request, headers=gateway_headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                response_json = response.json()
                print(f"Response: {json.dumps(response_json, indent=2)}")
                
                if 'result' in response_json and not response_json['result'].get('isError', False):
                    print(f"✅ TEST 2 SUCCESS!")
                    return True
            else:
                print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Check what the working direct call looks like for comparison
    print(f"\n📋 TEST 3: Direct TACNode call (for comparison)")
    tacnode_url = "https://mcp-server.tacnode.io/mcp"
    tacnode_token = "eyJhbGciOiJSUzI1NiJ9.eyJlbmNyeXB0ZWRDb25uZWN0aW9uIjoiMk51V2lPTzJzaGdmbnZvdVQvanJlWjFxNTlSekZ0QmlORmJtRytUMXlUblJXVkFseE9keGFWYXRsbHpONmJJNkt1VERCYU5XTzlZeUk2UDBKeGFVZFJ3dnE5YklQWUlZM2c4QUt0MlNmV3RQd1RPOW1FWmVVTkJlOVl6czZMQ1JIR2NTMmpZUFlDbUZXblRrMjZTeFQ1Y0FmbkNGVXd2SUxHaGo1QTBucVFPeDAxTEwyUUlabWtWck5aY2xMTVVUNkEvMU55YUEzcVZZZFdHdUtFRmFmUmxlZlZMY2ppbjltbkYrT1dsQldFR01yRTRwMUZHSEN2R2VOM2dOWTJhZUdLbWdlZUVXMTdoOUdXSG9jOXBaeTFQKzRCc1U1eWhTdjlvOG1nbDNCV242TVFaVXVNV3ZndzU1U3NJZFQvNUJqWGFYL1lZaEszK3EyN0pYVzF5aC83dUhXZnliS0R3dFVRK3pDYnVxTjZNTmptRG5PYjlQM21wakJaNGlzT0ZGbnd3OVFJdnhrRHpReTNJaVhUSFZiQUNGTE96c2ptblZMV2diT1RKRFBTSHNaczNFZTUzNmQ4TnFtZzk0Q0VNNFo2YmtYSkx6Wkp1RUpsTUlnSDhjNm85NDVjM3JhZ1JwWmtmK3U4eTBXL3d1QlRMRCtqZ0dUM1ZsQzlGZ2NhWHlwWTBqNzVCaURqYVcrMUVRdzlEVmZHV29BZS9Mc2JtTXNBaVBqMXJBVEVyMFlsOWdwb2RhRWNQd0xRcThoeVZxWmxGUDZXeUJzMEhaV0RybmdKbWNxdGVXenMrblJER1dGSURNNnZvcXdKQ0JoT09aQVRwTFlYK3ByZTNKVFFLeUpyRjB1VExPUENsdkFsTStOQW02WDJKd2lOdGNhZVVhZ1VNb2pXVWY5QnlCaFFCc0FVTjQwTzAvaGtXa3NpbHBGQUp3RkZvVEVIQXcrNXc3RTV0bGl4QjJVTDVkVi85Y08vVk9oRFNud2cyTVpNTUJBSWNtWFZtVEdHdjJxc2p2MTNxenJxVm5BTzIxcmNsbm9BbTZzRmg2Sk5mSjc2MEdENXZId2V6N1FuNjhWSVlQa0RkN2h0TzBIRkJEWmREangxaXFtL0V5QkFIU0dlTk01cVI0c0R2TC9OL0RSK21BS1hQcW4yc0syQlU4RXJWYUNyQXlwS2UyWlVZcXoySDRTcmsvZ1BuN3FnZlZiaTluK2R3ZU1BUjhYNVZzWlF1WlNqTThmRXUvK1dUa1l4eTVKajFpdGhvbDl3OWIrb0E0cjFvaHgwMXFnaGFZQnFQcnNYSmFsSWZITG44MVU1MkdibStBSEs5a1ZNcnBMbHFHek1sbWJCMzVuRkQ3K2kwaWtoVVBMellFV09YNzV6dVVyQkUvYkc4MHFBeVAzaHNwIiwiaXNzIjoibWNwLXRva2VuLXNlcnZpY2UiLCJhdWQiOiJtY3AtY2xpZW50cyIsImlhdCI6MTc1NDI5NzY3MCwiZXhwIjoxNzY5ODQ5NjcwfQ.cScHS445lUq-jCvZWyww6iuukw8cNpFgQYMGMshTQDPgj-6Q7H2jBBlCAeWyoFcazNAIdDUwJ-vdZWhLBv4QTOM5v5fyz_H1OS7iN_54NUR0DOU99Nleu0KorUZWYV6NzZEa8Pt1M5iH5v_lIrLIhGS-Ya_hsDs3UvIrbzv32eM"
    
    direct_request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "query",
            "arguments": {
                "sql": "SELECT 'direct_test' as format_test"
            }
        },
        "id": 1
    }
    
    direct_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "Authorization": f"Bearer {tacnode_token}"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(tacnode_url, json=direct_request, headers=direct_headers)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                response_text = response.text
                if response_text.startswith('event: message\ndata: '):
                    json_data = response_text.replace('event: message\ndata: ', '').strip()
                    response_json = json.loads(json_data)
                else:
                    response_json = response.json()
                
                print(f"✅ Direct call works")
                print(f"Response: {json.dumps(response_json, indent=2)}")
                
                if 'result' in response_json and not response_json['result'].get('isError', False):
                    print(f"✅ Direct call returns real data")
                    return True
            else:
                print(f"❌ Direct call failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Direct call error: {e}")
    
    return False

async def main():
    """Debug OpenAPI format"""
    print("🔧 OPENAPI FORMAT DEBUG")
    print("=" * 70)
    
    success = await debug_openapi_format()
    
    if success:
        print(f"\n✅ Found working format!")
    else:
        print(f"\n❌ No working format found")
        print(f"💡 The issue may be with credential provider configuration")
        print(f"💡 Or the OpenAPI spec doesn't match TACNode expectations")

if __name__ == "__main__":
    asyncio.run(main())

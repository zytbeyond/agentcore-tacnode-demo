#!/usr/bin/env python3
"""
Debug the gateway integration issue by comparing direct vs gateway calls
"""

import asyncio
import httpx
import json
import requests
import base64

async def debug_gateway_issue():
    """Debug why gateway calls fail while direct calls work"""
    print("🔧 DEBUGGING GATEWAY INTEGRATION ISSUE")
    print("=" * 60)
    
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
    
    # Test 1: Direct TACNode call (working)
    print(f"\n📋 TEST 1: Direct TACNode Call (Known Working)")
    print("-" * 50)
    
    tacnode_url = "https://mcp-server.tacnode.io/mcp"
    tacnode_token = "eyJhbGciOiJSUzI1NiJ9.eyJlbmNyeXB0ZWRDb25uZWN0aW9uIjoiMk51V2lPTzJzaGdmbnZvdVQvanJlWjFxNTlSekZ0QmlORmJtRytUMXlUblJXVkFseE9keGFWYXRsbHpONmJJNkt1VERCYU5XTzlZeUk2UDBKeGFVZFJ3dnE5YklQWUlZM2c4QUt0MlNmV3RQd1RPOW1FWmVVTkJlOVl6czZMQ1JIR2NTMmpZUFlDbUZXblRrMjZTeFQ1Y0FmbkNGVXd2SUxHaGo1QTBucVFPeDAxTEwyUUlabWtWck5aY2xMTVVUNkEvMU55YUEzcVZZZFdHdUtFRmFmUmxlZlZMY2ppbjltbkYrT1dsQldFR01yRTRwMUZHSEN2R2VOM2dOWTJhZUdLbWdlZUVXMTdoOUdXSG9jOXBaeTFQKzRCc1U1eWhTdjlvOG1nbDNCV242TVFaVXVNV3ZndzU1U3NJZFQvNUJqWGFYL1lZaEszK3EyN0pYVzF5aC83dUhXZnliS0R3dFVRK3pDYnVxTjZNTmptRG5PYjlQM21wakJaNGlzT0ZGbnd3OVFJdnhrRHpReTNJaVhUSFZiQUNGTE96c2ptblZMV2diT1RKRFBTSHNaczNFZTUzNmQ4TnFtZzk0Q0VNNFo2YmtYSkx6Wkp1RUpsTUlnSDhjNm85NDVjM3JhZ1JwWmtmK3U4eTBXL3d1QlRMRCtqZ0dUM1ZsQzlGZ2NhWHlwWTBqNzVCaURqYVcrMUVRdzlEVmZHV29BZS9Mc2JtTXNBaVBqMXJBVEVyMFlsOWdwb2RhRWNQd0xRcThoeVZxWmxGUDZXeUJzMEhaV0RybmdKbWNxdGVXenMrblJER1dGSURNNnZvcXdKQ0JoT09aQVRwTFlYK3ByZTNKVFFLeUpyRjB1VExPUENsdkFsTStOQW02WDJKd2lOdGNhZVVhZ1VNb2pXVWY5QnlCaFFCc0FVTjQwTzAvaGtXa3NpbHBGQUp3RkZvVEVIQXcrNXc3RTV0bGl4QjJVTDVkVi85Y08vVk9oRFNud2cyTVpNTUJBSWNtWFZtVEdHdjJxc2p2MTNxenJxVm5BTzIxcmNsbm9BbTZzRmg2Sk5mSjc2MEdENXZId2V6N1FuNjhWSVlQa0RkN2h0TzBIRkJEWmREangxaXFtL0V5QkFIU0dlTk01cVI0c0R2TC9OL0RSK21BS1hQcW4yc0syQlU4RXJWYUNyQXlwS2UyWlVZcXoySDRTcmsvZ1BuN3FnZlZiaTluK2R3ZU1BUjhYNVZzWlF1WlNqTThmRXUvK1dUa1l4eTVKajFpdGhvbDl3OWIrb0E0cjFvaHgwMXFnaGFZQnFQcnNYSmFsSWZITG44MVU1MkdibStBSEs5a1ZNcnBMbHFHek1sbWJCMzVuRkQ3K2kwaWtoVVBMellFV09YNzV6dVVyQkUvYkc4MHFBeVAzaHNwIiwiaXNzIjoibWNwLXRva2VuLXNlcnZpY2UiLCJhdWQiOiJtY3AtY2xpZW50cyIsImlhdCI6MTc1NDI5NzY3MCwiZXhwIjoxNzY5ODQ5NjcwfQ.cScHS445lUq-jCvZWyww6iuukw8cNpFgQYMGMshTQDPgj-6Q7H2jBBlCAeWyoFcazNAIdDUwJ-vdZWhLBv4QTOM5v5fyz_H1OS7iN_54NUR0DOU99Nleu0KorUZWYV6NzZEa8Pt1M5iH5v_lIrLIhGS-Ya_hsDs3UvIrbzv32eM"
    
    direct_request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "query",
            "arguments": {
                "sql": "SELECT 'direct_call' as test_type, COUNT(*) as record_count FROM test"
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
                
                print(f"✅ Direct call successful")
                print(f"Response: {json.dumps(response_json, indent=2)}")
                
                if 'result' in response_json and not response_json['result'].get('isError', False):
                    print(f"✅ Real data retrieved via direct call")
                else:
                    print(f"❌ Direct call has errors")
            else:
                print(f"❌ Direct call failed: {response.status_code}")
                print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Direct call error: {e}")
    
    # Test 2: Gateway call (failing)
    print(f"\n📋 TEST 2: Gateway Call (Currently Failing)")
    print("-" * 50)
    
    gateway_url = "https://pureawstacnodegateway-l0f1tg5t8o.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp"
    
    gateway_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "pure-aws-tacnode-target___executeQuery",
            "arguments": {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "query",
                    "arguments": {
                        "sql": "SELECT 'gateway_call' as test_type, COUNT(*) as record_count FROM test"
                    }
                },
                "id": 1
            }
        }
    }
    
    gateway_headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(gateway_url, json=gateway_request, headers=gateway_headers)
            print(f"Status: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                response_json = response.json()
                print(f"Gateway Response: {json.dumps(response_json, indent=2)}")
                
                if 'result' in response_json:
                    result = response_json['result']
                    if result.get('isError', False):
                        print(f"❌ Gateway call returned error: {result}")
                    else:
                        print(f"✅ Gateway call successful with data")
                else:
                    print(f"❌ No result in gateway response")
            else:
                print(f"❌ Gateway call failed: {response.status_code}")
                print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Gateway call error: {e}")
    
    # Test 3: Try simplified gateway call
    print(f"\n📋 TEST 3: Simplified Gateway Call")
    print("-" * 50)
    
    simple_gateway_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "pure-aws-tacnode-target___executeQuery",
            "arguments": {
                "sql": "SELECT 'simple_test' as test_type"
            }
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(gateway_url, json=simple_gateway_request, headers=gateway_headers)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                response_json = response.json()
                print(f"Simple Gateway Response: {json.dumps(response_json, indent=2)}")
                
                if 'result' in response_json:
                    result = response_json['result']
                    if result.get('isError', False):
                        print(f"❌ Simple gateway call returned error: {result}")
                    else:
                        print(f"✅ Simple gateway call successful")
                else:
                    print(f"❌ No result in simple gateway response")
            else:
                print(f"❌ Simple gateway call failed: {response.status_code}")
                print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Simple gateway call error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_gateway_issue())

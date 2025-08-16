#!/usr/bin/env python3
"""
Test what tools are available in the gateway
"""

import asyncio
import httpx
import json
import requests
import base64

async def test_gateway_tools():
    """Test what tools are available in the gateway"""
    print("🔧 TESTING GATEWAY TOOLS")
    print("=" * 50)
    
    # Real Cognito config
    cognito_config = {
        "userPoolId": "us-east-1_qVOK14gn5",
        "clientId": "629cm5j58a7o0lhh1qph1re0l5",
        "clientSecret": "t7uo744afdgrlasjgqe0rsdasdm8ovg91otr12guk4jq79c3d64",
        "tokenEndpoint": "https://us-east-1-qvok14gn5.auth.us-east-1.amazoncognito.com/oauth2/token"
    }
    
    # Get token
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
    print(f"✅ Got token: {access_token[:50]}...")
    
    # Test gateway
    gateway_url = "https://pureawstacnodegateway-l0f1tg5t8o.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp"
    
    # Test 1: List tools
    print(f"\n📋 TEST 1: List available tools")
    list_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list"
    }
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(gateway_url, json=list_request, headers=headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                response_json = response.json()
                print(f"Tools list: {json.dumps(response_json, indent=2)}")
            else:
                print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Try different tool names
    tool_names = ["executeQuery", "query", "sql", "tacnode"]
    
    for tool_name in tool_names:
        print(f"\n📋 TEST: Tool '{tool_name}'")
        test_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": {
                    "sql": "SELECT 1 as test"
                }
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(gateway_url, json=test_request, headers=headers)
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    response_json = response.json()
                    print(f"Response: {json.dumps(response_json, indent=2)}")
                    if 'result' in response_json:
                        print(f"✅ Tool '{tool_name}' works!")
                        return tool_name
                else:
                    print(f"Error: {response.text}")
        except Exception as e:
            print(f"Error: {e}")
    
    return None

if __name__ == "__main__":
    asyncio.run(test_gateway_tools())

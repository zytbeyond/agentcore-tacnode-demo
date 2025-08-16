#!/usr/bin/env python3
"""
Test the corrected gateway integration
"""

import asyncio
import httpx
import json
import requests
import base64

async def test_corrected_gateway():
    """Test the corrected gateway with proper OpenAPI spec"""
    print("🧪 TESTING CORRECTED GATEWAY INTEGRATION")
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
        return False
    
    token_data = response.json()
    access_token = token_data['access_token']
    print(f"✅ Got Cognito token")
    
    # Test corrected gateway
    gateway_url = "https://pureawstacnodegateway-l0f1tg5t8o.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp"
    new_target_id = "MAII1DK5R6"
    
    print(f"\n📋 Testing Corrected Gateway Integration")
    print(f"Gateway: pureawstacnodegateway-l0f1tg5t8o")
    print(f"New Target: {new_target_id}")
    print("-" * 50)
    
    # First, check what tools are available
    list_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list"
    }
    
    gateway_headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print("🔍 Checking available tools...")
            response = await client.post(gateway_url, json=list_request, headers=gateway_headers)
            
            if response.status_code == 200:
                response_json = response.json()
                tools = response_json.get('result', {}).get('tools', [])
                
                print(f"Available tools:")
                for tool in tools:
                    print(f"  - {tool.get('name', 'Unknown')}")
                
                # Find the corrected target tool
                corrected_tool_name = None
                for tool in tools:
                    if 'corrected-tacnode-target' in tool.get('name', ''):
                        corrected_tool_name = tool['name']
                        break
                
                if corrected_tool_name:
                    print(f"✅ Found corrected tool: {corrected_tool_name}")
                    
                    # Test the corrected tool
                    print(f"\n🧪 Testing corrected tool...")
                    
                    corrected_request = {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "tools/call",
                        "params": {
                            "name": corrected_tool_name,
                            "arguments": {
                                "jsonrpc": "2.0",
                                "method": "tools/call",
                                "params": {
                                    "name": "query",
                                    "arguments": {
                                        "sql": "SELECT 'corrected_gateway' as test_type, COUNT(*) as record_count FROM test"
                                    }
                                },
                                "id": 1
                            }
                        }
                    }
                    
                    response = await client.post(gateway_url, json=corrected_request, headers=gateway_headers)
                    print(f"Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        response_json = response.json()
                        print(f"Response: {json.dumps(response_json, indent=2)}")
                        
                        if 'result' in response_json:
                            result = response_json['result']
                            if result.get('isError', False):
                                print(f"❌ Tool returned error: {result}")
                                return False
                            else:
                                # Check if we got real data
                                content = result.get('content', [])
                                if content and len(content) > 0:
                                    text_content = content[0].get('text', '')
                                    if 'corrected_gateway' in text_content and 'record_count' in text_content:
                                        print(f"🎉 SUCCESS! Real data retrieved through corrected gateway!")
                                        print(f"✅ Data: {text_content}")
                                        return True
                                    else:
                                        print(f"❌ Unexpected data format: {text_content}")
                                        return False
                                else:
                                    print(f"❌ No content in result")
                                    return False
                        else:
                            print(f"❌ No result in response")
                            return False
                    else:
                        print(f"❌ Tool call failed: {response.status_code}")
                        print(f"Response: {response.text}")
                        return False
                else:
                    print(f"❌ Corrected tool not found in available tools")
                    return False
            else:
                print(f"❌ Failed to list tools: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def main():
    """Run the corrected gateway test"""
    print("🎯 CORRECTED GATEWAY INTEGRATION TEST")
    print("=" * 70)
    
    success = await test_corrected_gateway()
    
    if success:
        print(f"\n🎉 CORRECTED GATEWAY INTEGRATION SUCCESSFUL!")
        print(f"✅ Real data retrieved through AWS AgentCore Gateway")
        print(f"✅ Pure AWS solution working end-to-end")
        print(f"✅ No simulation, no mocking - REAL DATA")
    else:
        print(f"\n❌ CORRECTED GATEWAY INTEGRATION FAILED")
        print(f"❌ Still investigating the issue")

if __name__ == "__main__":
    asyncio.run(main())

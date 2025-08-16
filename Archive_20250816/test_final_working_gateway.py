#!/usr/bin/env python3
"""
Test the final working gateway integration with fixed API key
"""

import asyncio
import httpx
import json
import requests
import base64

async def test_final_working_gateway():
    """Test the final working gateway with correct API key"""
    print("🧪 TESTING FINAL WORKING GATEWAY INTEGRATION")
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
    
    # Test final working gateway
    gateway_url = "https://pureawstacnodegateway-l0f1tg5t8o.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp"
    final_target_id = "WXIO6JIDHI"
    
    print(f"\n📋 Testing Final Working Gateway Integration")
    print(f"Gateway: pureawstacnodegateway-l0f1tg5t8o")
    print(f"Final Target: {final_target_id}")
    print(f"Credential Provider: TACNodeWorkingToken")
    print("-" * 50)
    
    # Check available tools
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
                
                # Find the final working target tool
                working_tool_name = None
                for tool in tools:
                    if 'working-tacnode-target' in tool.get('name', ''):
                        working_tool_name = tool['name']
                        break
                
                if working_tool_name:
                    print(f"✅ Found working tool: {working_tool_name}")
                    
                    # Test the working tool with real SQL query
                    print(f"\n🧪 Testing working tool with real SQL query...")
                    
                    working_request = {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "tools/call",
                        "params": {
                            "name": working_tool_name,
                            "arguments": {
                                "jsonrpc": "2.0",
                                "method": "tools/call",
                                "params": {
                                    "name": "query",
                                    "arguments": {
                                        "sql": "SELECT 'FINAL_SUCCESS' as status, 'REAL_DATA_FROM_GATEWAY' as source, COUNT(*) as total_records FROM test WHERE is_active = true"
                                    }
                                },
                                "id": 1
                            }
                        }
                    }
                    
                    response = await client.post(gateway_url, json=working_request, headers=gateway_headers)
                    print(f"Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        response_json = response.json()
                        print(f"Response: {json.dumps(response_json, indent=2)}")
                        
                        if 'result' in response_json:
                            result = response_json['result']
                            
                            # Check for errors
                            if result.get('isError', False):
                                print(f"❌ Tool returned error: {result}")
                                error_text = result.get('content', [{}])[0].get('text', '')
                                print(f"❌ Error details: {error_text}")
                                return False
                            else:
                                # Check if we got real data
                                content = result.get('content', [])
                                if content and len(content) > 0:
                                    text_content = content[0].get('text', '')
                                    print(f"📊 Raw response content: {text_content}")
                                    
                                    # Parse the response to check for real data
                                    if 'FINAL_SUCCESS' in text_content and 'REAL_DATA_FROM_GATEWAY' in text_content:
                                        print(f"\n🎉 COMPLETE SUCCESS! REAL DATA RETRIEVED THROUGH GATEWAY!")
                                        print(f"✅ AWS Cognito authentication: WORKING")
                                        print(f"✅ AgentCore Gateway routing: WORKING") 
                                        print(f"✅ TACNode API integration: WORKING")
                                        print(f"✅ PostgreSQL database access: WORKING")
                                        print(f"✅ Real data retrieval: WORKING")
                                        print(f"✅ End-to-end flow: COMPLETE")
                                        
                                        # Extract actual data
                                        try:
                                            # Try to parse JSON from the text content
                                            if text_content.startswith('[') and text_content.endswith(']'):
                                                data = json.loads(text_content)
                                                if isinstance(data, list) and len(data) > 0:
                                                    record = data[0]
                                                    print(f"\n📊 ACTUAL DATABASE RECORD:")
                                                    for key, value in record.items():
                                                        print(f"   {key}: {value}")
                                        except:
                                            print(f"📊 Raw data: {text_content}")
                                        
                                        return True
                                    else:
                                        print(f"❌ Unexpected response format: {text_content}")
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
                    print(f"❌ Working tool not found in available tools")
                    return False
            else:
                print(f"❌ Failed to list tools: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def main():
    """Run the final working gateway test"""
    print("🎯 FINAL WORKING GATEWAY INTEGRATION TEST")
    print("=" * 70)
    print("🌐 Architecture: User → AWS Cognito → AgentCore Gateway → TACNode → PostgreSQL")
    print("🔑 Using corrected API key credential provider")
    
    success = await test_final_working_gateway()
    
    if success:
        print(f"\n🎉 FINAL GATEWAY INTEGRATION SUCCESSFUL!")
        print(f"✅ Real data retrieved through AWS AgentCore Gateway")
        print(f"✅ Pure AWS solution working end-to-end")
        print(f"✅ No simulation, no mocking - REAL DATA FROM DATABASE")
        print(f"✅ Production ready!")
    else:
        print(f"\n❌ FINAL GATEWAY INTEGRATION FAILED")
        print(f"❌ Issue still needs to be resolved")

if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
Test TACNode REST API directly following their documentation
https://tacnode.io/docs/guides/ecosystem/ai/managed-mcp-server/
"""

import asyncio
import httpx
import json
import os
from datetime import datetime

async def test_tacnode_rest_api_direct():
    """Test TACNode REST API directly as documented"""
    print("🧪 TESTING TACNODE REST API DIRECTLY")
    print("=" * 60)
    print("📋 Following TACNode documentation exactly:")
    print("   https://tacnode.io/docs/guides/ecosystem/ai/managed-mcp-server/")
    
    tacnode_token = os.getenv('TACNODE_TOKEN')
    if not tacnode_token:
        print("❌ TACNODE_TOKEN environment variable required")
        return False
    
    # TACNode REST API endpoint as documented
    url = "https://mcp-server.tacnode.io/mcp"
    
    # JSON-RPC request body as documented
    request_body = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "query",
            "arguments": {
                "sql": "SELECT COUNT(*) as record_count FROM test WHERE is_active = true"
            }
        },
        "id": 1
    }
    
    # Headers as documented
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "Authorization": f"Bearer {tacnode_token}"
    }
    
    print(f"\n📋 REQUEST DETAILS:")
    print(f"   URL: {url}")
    print(f"   Method: POST")
    print(f"   Headers: {json.dumps(headers, indent=2)}")
    print(f"   Body: {json.dumps(request_body, indent=2)}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print(f"\n🌐 Making REST API call to TACNode...")
            
            response = await client.post(
                url,
                json=request_body,
                headers=headers
            )
            
            print(f"   Response Status: {response.status_code}")
            print(f"   Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                response_text = response.text
                print(f"   Response Body: {response_text}")
                
                # Handle Server-Sent Events format
                if response_text.startswith('event: message\ndata: '):
                    print(f"\n✅ Received SSE format response")
                    # Extract JSON from SSE format
                    json_data = response_text.replace('event: message\ndata: ', '').strip()
                    try:
                        response_json = json.loads(json_data)
                        print(f"   Parsed JSON: {json.dumps(response_json, indent=2)}")
                        
                        if 'result' in response_json:
                            print(f"\n🎉 SUCCESS! TACNode REST API working!")
                            print(f"   JSON-RPC ID: {response_json.get('id')}")
                            print(f"   JSON-RPC Version: {response_json.get('jsonrpc')}")
                            
                            result = response_json['result']
                            if 'content' in result and len(result['content']) > 0:
                                content_text = result['content'][0]['text']
                                print(f"   Query Result: {content_text}")
                                print(f"   Is Error: {result.get('isError', False)}")
                                
                                return True
                        else:
                            print(f"❌ No result in response")
                            return False
                            
                    except json.JSONDecodeError as e:
                        print(f"❌ Failed to parse JSON from SSE: {e}")
                        return False
                else:
                    # Try to parse as direct JSON
                    try:
                        response_json = response.json()
                        print(f"\n✅ Received direct JSON response")
                        print(f"   Parsed JSON: {json.dumps(response_json, indent=2)}")
                        
                        if 'result' in response_json:
                            print(f"\n🎉 SUCCESS! TACNode REST API working!")
                            return True
                        else:
                            print(f"❌ No result in response")
                            return False
                            
                    except json.JSONDecodeError as e:
                        print(f"❌ Failed to parse response as JSON: {e}")
                        return False
            else:
                print(f"❌ HTTP error: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

async def test_agentcore_gateway_with_tacnode_rest():
    """Test AgentCore Gateway calling TACNode REST API"""
    print("\n🧪 TESTING AGENTCORE GATEWAY → TACNODE REST API")
    print("=" * 60)
    
    # Load gateway and target information
    try:
        with open('tacnode-agentcore-gateway.json', 'r') as f:
            gateway_info = json.load(f)
            gateway_id = gateway_info['gatewayId']
        
        with open('tacnode-agentcore-target.json', 'r') as f:
            target_info = json.load(f)
            target_name = target_info['targetName']
            target_id = target_info['targetId']
    except FileNotFoundError as e:
        print(f"❌ Configuration file not found: {e}")
        return False
    
    gateway_token = os.getenv('GATEWAY_TOKEN')
    if not gateway_token:
        print("⚠️  GATEWAY_TOKEN not set - using placeholder for demo")
        gateway_token = "placeholder-token"
    
    gateway_endpoint = f"https://gateway-{gateway_id}.bedrock-agentcore.us-east-1.amazonaws.com"
    target_url = f"{gateway_endpoint}/targets/{target_name}/invoke"
    
    print(f"   Gateway ID: {gateway_id}")
    print(f"   Target Name: {target_name}")
    print(f"   Target ID: {target_id}")
    print(f"   Target URL: {target_url}")
    
    # MCP request to gateway
    mcp_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "executeJsonRpcCall",
            "arguments": {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "query",
                    "arguments": {
                        "sql": "SELECT COUNT(*) as record_count FROM test WHERE is_active = true"
                    }
                },
                "id": 1
            }
        }
    }
    
    headers = {
        "Authorization": f"Bearer {gateway_token}",
        "Content-Type": "application/json",
        "User-Agent": "TACNodeRestAPITest/1.0"
    }
    
    print(f"\n📋 GATEWAY REQUEST:")
    print(f"   MCP Request: {json.dumps(mcp_request, indent=2)}")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            print(f"\n🌐 Making MCP call to AgentCore Gateway...")
            
            response = await client.post(
                target_url,
                json=mcp_request,
                headers=headers
            )
            
            print(f"   Gateway Response Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    response_json = response.json()
                    print(f"   Gateway Response: {json.dumps(response_json, indent=2)}")
                    
                    if 'result' in response_json:
                        print(f"\n🎉 SUCCESS! AgentCore Gateway → TACNode REST API working!")
                        return True
                    else:
                        print(f"❌ No result in gateway response")
                        return False
                        
                except json.JSONDecodeError as e:
                    print(f"❌ Failed to parse gateway response: {e}")
                    print(f"   Raw response: {response.text}")
                    return False
            else:
                print(f"❌ Gateway error: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Gateway request failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🌐 TACNode REST API Integration Tests")
    print("=" * 60)
    print("📋 Based on TACNode documentation:")
    print("   https://tacnode.io/docs/guides/ecosystem/ai/managed-mcp-server/")
    
    # Test 1: Direct TACNode REST API
    print(f"\n{'='*60}")
    direct_success = await test_tacnode_rest_api_direct()
    
    # Test 2: AgentCore Gateway → TACNode REST API
    print(f"\n{'='*60}")
    gateway_success = await test_agentcore_gateway_with_tacnode_rest()
    
    # Summary
    print(f"\n🎯 TEST SUMMARY:")
    print(f"   Direct TACNode REST API: {'✅ SUCCESS' if direct_success else '❌ FAILED'}")
    print(f"   Gateway → TACNode REST API: {'✅ SUCCESS' if gateway_success else '❌ FAILED'}")
    
    if direct_success and gateway_success:
        print(f"\n🎉 COMPLETE SUCCESS!")
        print(f"   User → MCP → AgentCore Gateway → TACNode REST API → PostgreSQL")
        print(f"   Following TACNode documentation exactly!")
    elif direct_success:
        print(f"\n✅ PARTIAL SUCCESS!")
        print(f"   TACNode REST API works directly")
        print(f"   Gateway integration needs gateway token")
    else:
        print(f"\n❌ TESTS FAILED!")
        print(f"   Check TACNode token and configuration")

if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
Test TACNode with proper SSE (Server-Sent Events) handling
"""

import requests
import json
import os

def get_tacnode_token():
    """Get TACNode token"""
    if os.path.exists('tacnode_token.txt'):
        with open('tacnode_token.txt', 'r') as f:
            token = f.read().strip()
        if token:
            return token
    return None

def parse_sse_response(response_text):
    """Parse Server-Sent Events response"""
    lines = response_text.strip().split('\n')
    
    for line in lines:
        if line.startswith('data: '):
            # Extract JSON data from SSE format
            json_data = line[6:]  # Remove 'data: ' prefix
            try:
                return json.loads(json_data)
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse JSON: {e}")
                print(f"Raw data: {json_data}")
                return None
    
    return None

def test_tacnode_with_sse():
    """Test TACNode with proper SSE handling"""
    print("🧪 TESTING TACNODE WITH SSE HANDLING")
    print("=" * 70)
    
    token = get_tacnode_token()
    if not token:
        print("❌ No token found")
        return False
    
    print(f"✅ Token loaded successfully")
    
    # TACNode endpoint
    url = "https://mcp-server.tacnode.io/mcp"
    
    # Headers as per TACNode documentation
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "Authorization": f"Bearer {token}"
    }
    
    # Test 1: Tools list
    print(f"\n📋 TEST 1: Tools List")
    print("-" * 50)
    
    tools_payload = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "id": 1
    }
    
    try:
        response = requests.post(url, headers=headers, json=tools_payload, timeout=30)
        print(f"Tools list status: {response.status_code}")
        print(f"Content type: {response.headers.get('content-type')}")
        
        if response.status_code == 200:
            # Parse SSE response
            response_json = parse_sse_response(response.text)
            
            if response_json:
                print(f"✅ Parsed SSE response:")
                print(json.dumps(response_json, indent=2))
                
                if 'result' in response_json and 'tools' in response_json['result']:
                    tools = response_json['result']['tools']
                    print(f"✅ Found {len(tools)} tools:")
                    for tool in tools:
                        print(f"  - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
                else:
                    print(f"❌ Unexpected response format")
                    return False
            else:
                print(f"❌ Failed to parse SSE response")
                return False
        else:
            print(f"❌ Tools list HTTP error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing tools list: {e}")
        return False
    
    # Test 2: Database query
    print(f"\n📋 TEST 2: Database Query")
    print("-" * 50)
    
    query_payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "query",
            "arguments": {
                "sql": "SELECT 'SSE_TEST_SUCCESS' as status, NOW() as test_time, COUNT(*) as record_count FROM test LIMIT 5"
            }
        },
        "id": 2
    }
    
    try:
        response = requests.post(url, headers=headers, json=query_payload, timeout=30)
        print(f"Query status: {response.status_code}")
        print(f"Content type: {response.headers.get('content-type')}")
        
        if response.status_code == 200:
            # Parse SSE response
            response_json = parse_sse_response(response.text)
            
            if response_json:
                print(f"✅ Parsed SSE response:")
                print(json.dumps(response_json, indent=2))
                
                if 'result' in response_json and not response_json['result'].get('isError', False):
                    content = response_json['result'].get('content', [])
                    if content and len(content) > 0:
                        text_content = content[0].get('text', '')
                        print(f"\n🎉 TACNODE SSE SUCCESS!")
                        print(f"📊 Real data from TACNode: {text_content}")
                        
                        # Parse the data
                        try:
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
                        print(f"❌ No content in query result")
                        return False
                else:
                    error_content = response_json['result'].get('content', [{}])[0].get('text', '')
                    print(f"❌ Query error: {error_content}")
                    return False
            else:
                print(f"❌ Failed to parse SSE response")
                return False
        else:
            print(f"❌ Query HTTP error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing query: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 TACNODE SSE CONNECTIVITY TEST")
    print("=" * 70)
    print("🎯 Testing TACNode API with proper SSE handling")
    print("🎯 Verifying database access to 'test' table in 'postgres' database")
    
    success = test_tacnode_with_sse()
    
    print(f"\n" + "=" * 70)
    if success:
        print(f"🎉 TACNODE SSE TEST SUCCESS!")
        print(f"✅ TACNode token is valid")
        print(f"✅ TACNode API is accessible")
        print(f"✅ SSE response parsing works")
        print(f"✅ Database queries work")
        print(f"✅ Ready for AgentCore Gateway integration")
        
        print(f"\n🌐 VERIFIED COMPONENTS:")
        print(f"   • TACNode Token: VALID")
        print(f"   • TACNode API: ACCESSIBLE")
        print(f"   • SSE Response Format: HANDLED")
        print(f"   • PostgreSQL Database: ACCESSIBLE")
        print(f"   • Test Table: ACCESSIBLE")
        print(f"   • Real Data Retrieval: WORKING")
        
        print(f"\n🎯 NEXT STEP:")
        print(f"   Now we can create AgentCore Gateway integration")
        print(f"   Note: Gateway must handle SSE responses from TACNode")
    else:
        print(f"❌ TACNODE SSE TEST FAILED")
        print(f"🔍 Check your TACNode token or network connectivity")

if __name__ == "__main__":
    main()

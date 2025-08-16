#!/usr/bin/env python3
"""
Test TACNode directly to verify token and connectivity
"""

import requests
import json
import os

def get_tacnode_token():
    """Get TACNode token"""
    # Check file
    if os.path.exists('tacnode_token.txt'):
        with open('tacnode_token.txt', 'r') as f:
            token = f.read().strip()
        if token:
            print(f"✅ Found TACNode token in tacnode_token.txt")
            return token
    
    print("❌ No TACNode token found")
    return None

def test_tacnode_direct():
    """Test TACNode directly"""
    print("🧪 TESTING TACNODE DIRECTLY")
    print("=" * 70)
    
    token = get_tacnode_token()
    if not token:
        return False
    
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
        
        if response.status_code == 200:
            response_json = response.json()
            print(f"Tools list response: {json.dumps(response_json, indent=2)}")
            
            if 'result' in response_json and not response_json['result'].get('isError', False):
                tools = response_json['result'].get('tools', [])
                print(f"✅ Found {len(tools)} tools")
                for tool in tools:
                    print(f"  - {tool.get('name', 'Unknown')}")
            else:
                print(f"❌ Tools list failed")
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
                "sql": "SELECT 'DIRECT_TEST_SUCCESS' as status, NOW() as test_time, COUNT(*) as record_count FROM test LIMIT 5"
            }
        },
        "id": 2
    }
    
    try:
        response = requests.post(url, headers=headers, json=query_payload, timeout=30)
        print(f"Query status: {response.status_code}")
        
        if response.status_code == 200:
            response_json = response.json()
            print(f"Query response: {json.dumps(response_json, indent=2)}")
            
            if 'result' in response_json and not response_json['result'].get('isError', False):
                content = response_json['result'].get('content', [])
                if content and len(content) > 0:
                    text_content = content[0].get('text', '')
                    print(f"\n🎉 DIRECT TACNODE SUCCESS!")
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
            print(f"❌ Query HTTP error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing query: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 DIRECT TACNODE CONNECTIVITY TEST")
    print("=" * 70)
    print("🎯 Testing TACNode API directly with your token")
    print("🎯 Verifying database access to 'test' table in 'postgres' database")
    
    success = test_tacnode_direct()
    
    print(f"\n" + "=" * 70)
    if success:
        print(f"🎉 DIRECT TACNODE TEST SUCCESS!")
        print(f"✅ TACNode token is valid")
        print(f"✅ TACNode API is accessible")
        print(f"✅ Database queries work")
        print(f"✅ Ready for AgentCore Gateway integration")
        
        print(f"\n🌐 VERIFIED COMPONENTS:")
        print(f"   • TACNode Token: VALID")
        print(f"   • TACNode API: ACCESSIBLE")
        print(f"   • PostgreSQL Database: ACCESSIBLE")
        print(f"   • Test Table: ACCESSIBLE")
        print(f"   • Real Data Retrieval: WORKING")
        
        print(f"\n🎯 NEXT STEP:")
        print(f"   Now we can create AgentCore Gateway integration")
    else:
        print(f"❌ DIRECT TACNODE TEST FAILED")
        print(f"🔍 Check your TACNode token or network connectivity")

if __name__ == "__main__":
    main()

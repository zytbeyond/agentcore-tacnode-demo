#!/usr/bin/env python3
"""
Sanity test: Direct connection to TACNode to verify it's still working
"""

import requests
import json

def test_tacnode_direct():
    """Test direct connection to TACNode"""
    print("🔍 SANITY TEST: Direct TACNode Connection")
    print("=" * 70)
    print("🎯 Testing direct connection to TACNode API")
    print("🎯 Verifying TACNode is still working")
    
    # Load TACNode token
    try:
        with open('tacnode_token.txt', 'r') as f:
            tacnode_token = f.read().strip()
        print(f"✅ TACNode token loaded: {tacnode_token[:20]}...")
    except FileNotFoundError:
        print("❌ TACNode token not found")
        return False
    
    tacnode_url = "https://mcp-server.tacnode.io/mcp"
    
    # Test 1: Tools list
    print(f"\n📋 TEST 1: TACNode Tools List")
    print("-" * 50)
    
    tools_request = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "id": 1
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream',
        'Authorization': f'Bearer {tacnode_token}'
    }
    
    print(f"🌐 Direct request to TACNode:")
    print(f"   URL: {tacnode_url}")
    print(f"   Headers: {headers}")
    print(f"   Request: {json.dumps(tools_request, indent=2)}")
    
    try:
        response = requests.post(
            tacnode_url,
            json=tools_request,
            headers=headers,
            timeout=30
        )
        
        print(f"\n📡 TACNode Response:")
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        print(f"   Content Type: {response.headers.get('content-type', 'Unknown')}")
        
        if response.status_code == 200:
            response_text = response.data if hasattr(response, 'data') else response.text
            print(f"   Raw Response: {response_text}")
            
            # Check if it's SSE format
            if 'text/event-stream' in response.headers.get('content-type', ''):
                print(f"✅ TACNode returned SSE response")
                
                # Parse SSE
                lines = response_text.strip().split('\n')
                for line in lines:
                    if line.startswith('data: '):
                        json_data = line[6:]  # Remove 'data: ' prefix
                        try:
                            parsed_data = json.loads(json_data)
                            print(f"✅ Parsed SSE data: {json.dumps(parsed_data, indent=2)}")
                            
                            if 'result' in parsed_data and 'tools' in parsed_data['result']:
                                tools = parsed_data['result']['tools']
                                print(f"✅ Found {len(tools)} tools from TACNode")
                                for tool in tools:
                                    print(f"   - {tool['name']}: {tool['description']}")
                                return True
                        except json.JSONDecodeError as e:
                            print(f"❌ Failed to parse SSE JSON: {e}")
            else:
                # Regular JSON response
                try:
                    json_response = json.loads(response_text)
                    print(f"✅ TACNode JSON response: {json.dumps(json_response, indent=2)}")
                    return True
                except json.JSONDecodeError:
                    print(f"❌ Failed to parse JSON response")
        else:
            print(f"❌ TACNode error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Direct TACNode connection failed: {e}")
    
    return False

def test_tacnode_database_query():
    """Test direct database query to TACNode"""
    print(f"\n📋 TEST 2: TACNode Database Query")
    print("-" * 50)
    
    # Load TACNode token
    try:
        with open('tacnode_token.txt', 'r') as f:
            tacnode_token = f.read().strip()
    except FileNotFoundError:
        print("❌ TACNode token not found")
        return False
    
    tacnode_url = "https://mcp-server.tacnode.io/mcp"
    
    query_request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "query",
            "arguments": {
                "sql": "SELECT 'DIRECT_TACNODE_TEST' as test_type, 'SANITY_CHECK' as purpose, NOW() as timestamp, COUNT(*) as record_count FROM test"
            }
        },
        "id": 2
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream',
        'Authorization': f'Bearer {tacnode_token}'
    }
    
    print(f"🌐 Direct database query to TACNode:")
    print(f"   SQL: {query_request['params']['arguments']['sql']}")
    print(f"   Request: {json.dumps(query_request, indent=2)}")
    
    try:
        response = requests.post(
            tacnode_url,
            json=query_request,
            headers=headers,
            timeout=30
        )
        
        print(f"\n📡 TACNode Database Response:")
        print(f"   Status: {response.status_code}")
        print(f"   Content Type: {response.headers.get('content-type', 'Unknown')}")
        
        if response.status_code == 200:
            response_text = response.text
            print(f"   Raw Response: {response_text}")
            
            # Check if it's SSE format
            if 'text/event-stream' in response.headers.get('content-type', ''):
                print(f"✅ TACNode returned SSE response")
                
                # Parse SSE
                lines = response_text.strip().split('\n')
                for line in lines:
                    if line.startswith('data: '):
                        json_data = line[6:]  # Remove 'data: ' prefix
                        try:
                            parsed_data = json.loads(json_data)
                            print(f"✅ Parsed SSE data: {json.dumps(parsed_data, indent=2)}")
                            
                            if 'result' in parsed_data and not parsed_data['result'].get('isError', False):
                                content = parsed_data['result'].get('content', [])
                                if content and len(content) > 0:
                                    text_content = content[0].get('text', '')
                                    print(f"✅ Database data: {text_content}")
                                    
                                    # Parse database records
                                    try:
                                        if text_content.startswith('[') and text_content.endswith(']'):
                                            records = json.loads(text_content)
                                            print(f"✅ Direct TACNode database query successful!")
                                            for record in records:
                                                for key, value in record.items():
                                                    print(f"   {key}: {value}")
                                            return True
                                    except json.JSONDecodeError:
                                        print(f"✅ Raw database response: {text_content}")
                                        return True
                        except json.JSONDecodeError as e:
                            print(f"❌ Failed to parse SSE JSON: {e}")
        else:
            print(f"❌ TACNode database query error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Direct TACNode database query failed: {e}")
    
    return False

def main():
    """Main sanity test function"""
    print("🧪 TACNODE DIRECT CONNECTION SANITY TEST")
    print("=" * 70)
    print("🎯 Verifying TACNode is still working before fixing Gateway issue")
    
    # Test 1: Tools list
    tools_success = test_tacnode_direct()
    
    # Test 2: Database query
    query_success = test_tacnode_database_query()
    
    print(f"\n" + "=" * 70)
    print(f"📊 TACNODE SANITY TEST RESULTS")
    print("=" * 70)
    
    if tools_success and query_success:
        print(f"✅ TACNode is working perfectly!")
        print(f"✅ Tools list: SUCCESS")
        print(f"✅ Database query: SUCCESS")
        print(f"✅ SSE responses: WORKING")
        print(f"✅ PostgreSQL access: WORKING")
        
        print(f"\n🎯 CONCLUSION:")
        print(f"   TACNode is working fine")
        print(f"   The issue is in Gateway → Lambda → TACNode request format")
        print(f"   Need to fix how Gateway calls Lambda and how Lambda calls TACNode")
        
        return True
    else:
        print(f"❌ TACNode has issues!")
        print(f"❌ Tools list: {'SUCCESS' if tools_success else 'FAILED'}")
        print(f"❌ Database query: {'SUCCESS' if query_success else 'FAILED'}")
        
        print(f"\n🎯 CONCLUSION:")
        print(f"   TACNode itself has problems")
        print(f"   Need to fix TACNode connection first")
        
        return False

if __name__ == "__main__":
    main()

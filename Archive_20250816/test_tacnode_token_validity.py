#!/usr/bin/env python3
"""
Test if the current TACNode token is still valid
"""

import asyncio
import httpx
import json
from datetime import datetime

async def test_tacnode_token():
    """Test if the current TACNode token works"""
    print("🔍 TESTING TACNODE TOKEN VALIDITY")
    print("=" * 60)
    
    # Current TACNode token
    tacnode_token = "eyJhbGciOiJSUzI1NiJ9.eyJlbmNyeXB0ZWRDb25uZWN0aW9uIjoiMk51V2lPTzJzaGdmbnZvdVQvanJlWjFxNTlSekZ0QmlORmJtRytUMXlUblJXVkFseE9keGFWYXRsbHpONmJJNkt1VERCYU5XTzlZeUk2UDBKeGFVZFJ3dnE5YklQWUlZM2c4QUt0MlNmV3RQd1RPOW1FWmVVTkJlOVl6czZMQ1JIR2NTMmpZUFlDbUZXblRrMjZTeFQ1Y0FmbkNGVXd2SUxHaGo1QTBucVFPeDAxTEwyUUlabWtWck5aY2xMTVVUNkEvMU55YUEzcVZZZFdHdUtFRmFmUmxlZlZMY2ppbjltbkYrT1dsQldFR01yRTRwMUZHSEN2R2VOM2dOWTJhZUdLbWdlZUVXMTdoOUdXSG9jOXBaeTFQKzRCc1U1eWhTdjlvOG1nbDNCV242TVFaVXVNV3ZndzU1U3NJZFQvNUJqWGFYL1lZaEszK3EyN0pYVzF5aC83dUhXZnliS0R3dFVRK3pDYnVxTjZNTmptRG5PYjlQM21wakJaNGlzT0ZGbnd3OVFJdnhrRHpReTNJaVhUSFZiQUNGTE96c2ptblZMV2diT1RKRFBTSHNaczNFZTUzNmQ4TnFtZzk0Q0VNNFo2YmtYSkx6Wkp1RUpsTUlnSDhjNm85NDVjM3JhZ1JwWmtmK3U4eTBXL3d1QlRMRCtqZ0dUM1ZsQzlGZ2NhWHlwWTBqNzVCaURqYVcrMUVRdzlEVmZHV29BZS9Mc2JtTXNBaVBqMXJBVEVyMFlsOWdwb2RhRWNQd0xRcThoeVZxWmxGUDZXeUJzMEhaV0RybmdKbWNxdGVXenMrblJER1dGSURNNnZvcXdKQ0JoT09aQVRwTFlYK3ByZTNKVFFLeUpyRjB1VExPUENsdkFsTStOQW02WDJKd2lOdGNhZVVhZ1VNb2pXVWY5QnlCaFFCc0FVTjQwTzAvaGtXa3NpbHBGQUp3RkZvVEVIQXcrNXc3RTV0bGl4QjJVTDVkVi85Y08vVk9oRFNud2cyTVpNTUJBSWNtWFZtVEdHdjJxc2p2MTNxenJxVm5BTzIxcmNsbm9BbTZzRmg2Sk5mSjc2MEdENXZId2V6N1FuNjhWSVlQa0RkN2h0TzBIRkJEWmREangxaXFtL0V5QkFIU0dlTk01cVI0c0R2TC9OL0RSK21BS1hQcW4yc0syQlU4RXJWYUNyQXlwS2UyWlVZcXoySDRTcmsvZ1BuN3FnZlZiaTluK2R3ZU1BUjhYNVZzWlF1WlNqTThmRXUvK1dUa1l4eTVKajFpdGhvbDl3OWIrb0E0cjFvaHgwMXFnaGFZQnFQcnNYSmFsSWZITG44MVU1MkdibStBSEs5a1ZNcnBMbHFHek1sbWJCMzVuRkQ3K2kwaWtoVVBMellFV09YNzV6dVVyQkUvYkc4MHFBeVAzaHNwIiwiaXNzIjoibWNwLXRva2VuLXNlcnZpY2UiLCJhdWQiOiJtY3AtY2xpZW50cyIsImlhdCI6MTc1NDI5NzY3MCwiZXhwIjoxNzY5ODQ5NjcwfQ.cScHS445lUq-jCvZWyww6iuukw8cNpFgQYMGMshTQDPgj-6Q7H2jBBlCAeWyoFcazNAIdDUwJ-vdZWhLBv4QTOM5v5fyz_H1OS7iN_54NUR0DOU99Nleu0KorUZWYV6NzZEa8Pt1M5iH5v_lIrLIhGS-Ya_hsDs3UvIrbzv32eM"
    
    tacnode_url = "https://mcp-server.tacnode.io/mcp"
    
    print(f"Token: {tacnode_token[:50]}...")
    print(f"URL: {tacnode_url}")
    
    # Test request
    test_request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "query",
            "arguments": {
                "sql": "SELECT 'token_test' as test_type, NOW() as current_time, COUNT(*) as record_count FROM test"
            }
        },
        "id": 1
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "Authorization": f"Bearer {tacnode_token}"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print(f"\n🌐 Testing TACNode API call...")
            print(f"Request: {json.dumps(test_request, indent=2)}")
            
            response = await client.post(tacnode_url, json=test_request, headers=headers)
            
            print(f"\nResponse Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                response_text = response.text
                print(f"Raw Response: {response_text}")
                
                # Handle SSE format
                if response_text.startswith('event: message\ndata: '):
                    json_data = response_text.replace('event: message\ndata: ', '').strip()
                    try:
                        response_json = json.loads(json_data)
                    except json.JSONDecodeError:
                        print(f"❌ Failed to parse SSE JSON: {json_data}")
                        return False
                else:
                    try:
                        response_json = response.json()
                    except json.JSONDecodeError:
                        print(f"❌ Failed to parse JSON response")
                        return False
                
                print(f"\nParsed Response: {json.dumps(response_json, indent=2)}")
                
                # Check if token works
                if 'result' in response_json:
                    result = response_json['result']
                    if result.get('isError', False):
                        error_content = result.get('content', [{}])[0].get('text', '')
                        print(f"\n❌ TOKEN INVALID OR EXPIRED")
                        print(f"Error: {error_content}")
                        
                        # Check for specific error types
                        if 'unauthorized' in error_content.lower() or 'invalid token' in error_content.lower():
                            print(f"🔑 RECOMMENDATION: Get a new TACNode token")
                            return False
                        elif 'connect' in error_content.lower() and 'refused' in error_content.lower():
                            print(f"✅ TOKEN IS VALID (database connection issue is expected in test environment)")
                            return True
                        else:
                            print(f"❓ UNKNOWN ERROR: {error_content}")
                            return False
                    else:
                        # Success - got real data
                        content = result.get('content', [])
                        if content and len(content) > 0:
                            text_content = content[0].get('text', '')
                            print(f"\n✅ TOKEN IS VALID AND WORKING!")
                            print(f"Real data retrieved: {text_content}")
                            return True
                        else:
                            print(f"\n❌ No content in successful response")
                            return False
                else:
                    print(f"\n❌ No result in response")
                    return False
                    
            elif response.status_code == 401:
                print(f"\n❌ TOKEN INVALID - 401 Unauthorized")
                print(f"Response: {response.text}")
                print(f"🔑 RECOMMENDATION: Get a new TACNode token")
                return False
            elif response.status_code == 403:
                print(f"\n❌ TOKEN EXPIRED OR INSUFFICIENT PERMISSIONS - 403 Forbidden")
                print(f"Response: {response.text}")
                print(f"🔑 RECOMMENDATION: Get a new TACNode token")
                return False
            else:
                print(f"\n❌ Unexpected status code: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"\n❌ Request failed: {e}")
        return False

async def main():
    """Test TACNode token validity"""
    print("🔍 TACNODE TOKEN VALIDITY TEST")
    print("=" * 70)
    print(f"Test Time: {datetime.now()}")
    
    is_valid = await test_tacnode_token()
    
    print(f"\n" + "=" * 70)
    if is_valid:
        print(f"✅ CURRENT TOKEN IS VALID AND WORKING")
        print(f"✅ No need to get a new token")
        print(f"✅ Can proceed with fixing the credential provider")
    else:
        print(f"❌ CURRENT TOKEN IS INVALID OR EXPIRED")
        print(f"🔑 YOU NEED TO GET A NEW TACNODE TOKEN")
        print(f"❌ Cannot proceed until token is refreshed")

if __name__ == "__main__":
    asyncio.run(main())

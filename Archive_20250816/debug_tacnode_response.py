#!/usr/bin/env python3
"""
Debug TACNode response to see what we're getting
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

def debug_tacnode_response():
    """Debug TACNode response"""
    print("🔍 DEBUGGING TACNODE RESPONSE")
    print("=" * 70)
    
    token = get_tacnode_token()
    if not token:
        print("❌ No token found")
        return
    
    print(f"✅ Token length: {len(token)} characters")
    print(f"✅ Token starts with: {token[:50]}...")
    
    # TACNode endpoint
    url = "https://mcp-server.tacnode.io/mcp"
    
    # Headers as per TACNode documentation
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "Authorization": f"Bearer {token}"
    }
    
    # Simple tools list request
    tools_payload = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "id": 1
    }
    
    print(f"\n📋 Making request to: {url}")
    print(f"📋 Headers: {json.dumps(headers, indent=2)}")
    print(f"📋 Payload: {json.dumps(tools_payload, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=tools_payload, timeout=30)
        
        print(f"\n📊 RESPONSE DETAILS:")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Content Type: {response.headers.get('content-type', 'Unknown')}")
        print(f"Content Length: {len(response.content)} bytes")
        
        print(f"\n📊 RAW RESPONSE:")
        print(f"Text: {repr(response.text)}")
        
        print(f"\n📊 RAW CONTENT:")
        print(f"Bytes: {response.content}")
        
        # Try to parse as JSON
        try:
            response_json = response.json()
            print(f"\n📊 PARSED JSON:")
            print(json.dumps(response_json, indent=2))
        except Exception as json_error:
            print(f"\n❌ JSON parsing failed: {json_error}")
            
            # Check if it's streaming response
            if 'text/event-stream' in response.headers.get('content-type', ''):
                print(f"🔍 This appears to be a streaming response")
                lines = response.text.split('\n')
                for i, line in enumerate(lines):
                    print(f"Line {i}: {repr(line)}")
        
    except Exception as e:
        print(f"❌ Request failed: {e}")

def main():
    debug_tacnode_response()

if __name__ == "__main__":
    main()

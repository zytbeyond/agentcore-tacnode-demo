#!/usr/bin/env python3
"""
Extract and verify the token from the credential provider
"""

import boto3
import json
import asyncio
import httpx

async def extract_and_verify_token():
    """Extract token from credential provider and verify it works"""
    print("🔍 EXTRACTING AND VERIFYING TOKEN")
    print("=" * 60)
    
    secrets_client = boto3.client('secretsmanager', region_name='us-east-1')
    
    try:
        # Get the stored secret
        secret_arn = "arn:aws:secretsmanager:us-east-1:560155322832:secret:bedrock-agentcore-identity!default/apikey/TACNodeWorkingToken-5TaPnL"
        secret_response = secrets_client.get_secret_value(SecretId=secret_arn)
        stored_secret = secret_response['SecretString']
        
        print(f"Raw stored secret: {stored_secret}")
        
        # Parse the JSON to extract the actual token
        try:
            secret_data = json.loads(stored_secret)
            actual_token = secret_data['api_key_value']
            print(f"✅ Extracted token: {actual_token[:50]}...")
        except json.JSONDecodeError:
            print(f"❌ Secret is not valid JSON")
            return False
        except KeyError:
            print(f"❌ No 'api_key_value' key in secret")
            return False
        
        # Verify the extracted token works with TACNode
        print(f"\n🧪 Testing extracted token with TACNode...")
        
        tacnode_url = "https://mcp-server.tacnode.io/mcp"
        
        test_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "query",
                "arguments": {
                    "sql": "SELECT 'extracted_token_test' as test_type, COUNT(*) as record_count FROM test"
                }
            },
            "id": 1
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "Authorization": f"Bearer {actual_token}"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(tacnode_url, json=test_request, headers=headers)
            
            print(f"Response Status: {response.status_code}")
            
            if response.status_code == 200:
                response_text = response.text
                
                # Handle SSE format
                if response_text.startswith('event: message\ndata: '):
                    json_data = response_text.replace('event: message\ndata: ', '').strip()
                    response_json = json.loads(json_data)
                else:
                    response_json = response.json()
                
                print(f"Response: {json.dumps(response_json, indent=2)}")
                
                if 'result' in response_json and not response_json['result'].get('isError', False):
                    print(f"✅ EXTRACTED TOKEN WORKS WITH TACNODE!")
                    content = response_json['result']['content'][0]['text']
                    print(f"Real data: {content}")
                    return True
                else:
                    print(f"❌ Token test failed - error in response")
                    return False
            else:
                print(f"❌ Token test failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Failed to extract/verify token: {e}")
        return False

async def main():
    """Extract and verify token"""
    print("🔍 TOKEN EXTRACTION AND VERIFICATION")
    print("=" * 70)
    
    success = await extract_and_verify_token()
    
    if success:
        print(f"\n✅ TOKEN EXTRACTION SUCCESSFUL!")
        print(f"✅ The token stored in the credential provider works with TACNode")
        print(f"❓ The issue must be in how the gateway is using the token")
        print(f"💡 The gateway might not be extracting the token from the JSON correctly")
    else:
        print(f"\n❌ TOKEN EXTRACTION FAILED")
        print(f"❌ There's an issue with the stored token")

if __name__ == "__main__":
    asyncio.run(main())

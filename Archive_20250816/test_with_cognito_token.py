#!/usr/bin/env python3
"""
Test gateway with Cognito token to see if it works
Sometimes gateways are more flexible than they appear
"""

import asyncio
import httpx
import json
import boto3

async def test_gateway_with_cognito_token():
    """Test if Cognito token works with current gateway setup"""
    print("🧪 TESTING GATEWAY WITH COGNITO TOKEN")
    print("=" * 60)
    
    # Load Cognito configuration
    try:
        with open('cognito-tokens.json', 'r') as f:
            token_info = json.load(f)
            access_token = token_info['accessToken']
    except FileNotFoundError:
        print("❌ No Cognito tokens found. Run reconfiguration first.")
        return False
    
    # Load gateway info
    with open('tacnode-agentcore-gateway.json', 'r') as f:
        gateway_info = json.load(f)
        gateway_id = gateway_info['gatewayId']
    
    gateway_url = f"https://{gateway_id}.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp"
    
    print(f"Gateway URL: {gateway_url}")
    print(f"Token: {access_token[:50]}...")
    
    # Test MCP call with Cognito token
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
                        "sql": "SELECT 1 as test"
                    }
                },
                "id": 1
            }
        }
    }
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                gateway_url,
                json=mcp_request,
                headers=headers
            )
            
            print(f"Response Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            print(f"Response Body: {response.text}")
            
            if response.status_code == 200:
                print("🎉 SUCCESS! Cognito token works with gateway!")
                return True
            elif response.status_code == 401:
                print("❌ 401 Unauthorized - Cognito token not accepted")
                return False
            else:
                print(f"❌ Unexpected status: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

async def get_aws_sts_token():
    """Try to get AWS STS token as alternative"""
    print("\n🧪 TESTING WITH AWS STS TOKEN")
    print("=" * 60)
    
    try:
        # Get AWS STS token
        sts_client = boto3.client('sts', region_name='us-east-1')
        response = sts_client.get_session_token(DurationSeconds=3600)
        
        session_token = response['Credentials']['SessionToken']
        access_key = response['Credentials']['AccessKeyId']
        secret_key = response['Credentials']['SecretAccessKey']
        
        print(f"STS Session Token: {session_token[:50]}...")
        print(f"Access Key: {access_key}")
        
        # Test with STS token
        with open('tacnode-agentcore-gateway.json', 'r') as f:
            gateway_info = json.load(f)
            gateway_id = gateway_info['gatewayId']
        
        gateway_url = f"https://{gateway_id}.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp"
        
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
                            "sql": "SELECT 1 as test"
                        }
                    },
                    "id": 1
                }
            }
        }
        
        headers = {
            "Authorization": f"Bearer {session_token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                gateway_url,
                json=mcp_request,
                headers=headers
            )
            
            print(f"STS Token Response Status: {response.status_code}")
            print(f"STS Token Response: {response.text[:200]}")
            
            if response.status_code == 200:
                print("🎉 SUCCESS! AWS STS token works!")
                return session_token
            else:
                print("❌ AWS STS token doesn't work")
                return None
                
    except Exception as e:
        print(f"❌ STS token test failed: {e}")
        return None

async def try_simple_aws_auth():
    """Try simple AWS authentication approaches"""
    print("\n🧪 TRYING SIMPLE AWS AUTHENTICATION")
    print("=" * 60)
    
    # Get current AWS credentials
    session = boto3.Session()
    credentials = session.get_credentials()
    
    print(f"AWS Access Key: {credentials.access_key[:10]}...")
    print(f"AWS Secret Key: {credentials.secret_key[:10]}...")
    
    # Try different token formats
    test_tokens = [
        credentials.access_key,  # Raw access key
        f"{credentials.access_key}:{credentials.secret_key}",  # Access:Secret
        credentials.token if credentials.token else "no-session-token"  # Session token
    ]
    
    with open('tacnode-agentcore-gateway.json', 'r') as f:
        gateway_info = json.load(f)
        gateway_id = gateway_info['gatewayId']
    
    gateway_url = f"https://{gateway_id}.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp"
    
    for i, token in enumerate(test_tokens, 1):
        if token == "no-session-token":
            continue
            
        print(f"\n🧪 Test {i}: {token[:20]}...")
        
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
                            "sql": "SELECT 1 as test"
                        }
                    },
                    "id": 1
                }
            }
        }
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    gateway_url,
                    json=mcp_request,
                    headers=headers
                )
                
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    print(f"   🎉 SUCCESS! Token works: {token[:20]}...")
                    return token
                elif response.status_code == 401:
                    print(f"   ❌ 401 Unauthorized")
                else:
                    print(f"   ❌ Status: {response.status_code}")
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return None

async def main():
    """Test different authentication approaches"""
    print("🔑 TESTING DIFFERENT AUTHENTICATION APPROACHES")
    print("=" * 60)
    
    # Test 1: Cognito token
    cognito_success = await test_gateway_with_cognito_token()
    
    # Test 2: AWS STS token
    sts_token = await get_aws_sts_token()
    
    # Test 3: Simple AWS auth
    simple_token = await try_simple_aws_auth()
    
    print(f"\n🎯 RESULTS SUMMARY:")
    print(f"   Cognito Token: {'✅ SUCCESS' if cognito_success else '❌ FAILED'}")
    print(f"   AWS STS Token: {'✅ SUCCESS' if sts_token else '❌ FAILED'}")
    print(f"   Simple AWS Auth: {'✅ SUCCESS' if simple_token else '❌ FAILED'}")
    
    if cognito_success:
        print(f"\n🎉 SOLUTION: Use Cognito token")
        print(f"   export GATEWAY_TOKEN='<cognito-access-token>'")
    elif sts_token:
        print(f"\n🎉 SOLUTION: Use AWS STS token")
        print(f"   export GATEWAY_TOKEN='{sts_token}'")
    elif simple_token:
        print(f"\n🎉 SOLUTION: Use simple AWS token")
        print(f"   export GATEWAY_TOKEN='{simple_token}'")
    else:
        print(f"\n❌ NO WORKING AUTHENTICATION FOUND")
        print(f"   Gateway requires specific OAuth setup")

if __name__ == "__main__":
    asyncio.run(main())

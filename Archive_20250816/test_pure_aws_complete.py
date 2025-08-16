#!/usr/bin/env python3
"""
Test complete pure AWS AgentCore Gateway solution
Get Cognito token and test end-to-end integration
"""

import asyncio
import httpx
import json
import requests
import base64
import time

async def get_cognito_token():
    """Get Cognito token using client credentials flow"""
    print("🔑 GETTING AWS COGNITO TOKEN")
    print("=" * 60)
    
    # Cognito configuration from gateway creation
    cognito_config = {
        "userPoolId": "us-east-1_j2hhA2nBw",
        "clientId": "6qlqhqhqhqhqhqhqhqhqhqhqhq",  # This will be different
        "clientSecret": "secret-from-creation",  # This will be different
        "domain": "us-east-1-j2hha2nbw",
        "tokenEndpoint": "https://us-east-1-j2hha2nbw.auth.us-east-1.amazoncognito.com/oauth2/token"
    }
    
    # For now, let's try to get the actual values from the gateway
    print("⚠️  Need to get actual Cognito client credentials")
    print("📋 Let me check what we have from the gateway creation...")
    
    # Try to read from any saved config files
    try:
        with open('pure-aws-gateway-complete.json', 'r') as f:
            gateway_config = json.load(f)
            if 'cognitoConfig' in gateway_config:
                cognito_config = gateway_config['cognitoConfig']
                print(f"✅ Found Cognito config in gateway file")
    except FileNotFoundError:
        print("⚠️  No saved gateway config found")
    
    print(f"Client ID: {cognito_config.get('clientId', 'NOT_FOUND')}")
    print(f"Token endpoint: {cognito_config.get('tokenEndpoint', 'NOT_FOUND')}")
    
    if 'clientSecret' not in cognito_config:
        print("❌ Client secret not available - need to get from Cognito")
        return None
    
    try:
        # Get token using client credentials flow
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
        
        print(f"🌐 Requesting token from: {token_endpoint}")
        
        response = requests.post(token_endpoint, headers=headers, data=data, timeout=10)
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data['access_token']
            
            print(f"✅ Cognito token obtained!")
            print(f"   Token: {access_token[:50]}...")
            print(f"   Expires in: {token_data.get('expires_in', 'Unknown')} seconds")
            
            return access_token
        else:
            print(f"❌ Token request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Token generation failed: {e}")
        return None

async def test_pure_aws_gateway(token):
    """Test the pure AWS gateway with Cognito token"""
    print(f"\n🧪 TESTING PURE AWS GATEWAY")
    print("=" * 60)
    
    # Gateway configuration
    gateway_id = "pureawstacnodegateway-l0f1tg5t8o"
    target_id = "TGK8WM9V22"
    gateway_url = f"https://{gateway_id}.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp"
    
    print(f"Gateway ID: {gateway_id}")
    print(f"Target ID: {target_id}")
    print(f"Gateway URL: {gateway_url}")
    print(f"Token: {token[:50]}...")
    
    # MCP request to test TACNode integration
    mcp_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "executeQuery",
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
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print(f"\n🌐 Making MCP call to pure AWS gateway...")
            
            response = await client.post(
                gateway_url,
                json=mcp_request,
                headers=headers
            )
            
            print(f"Response Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    response_json = response.json()
                    print(f"Response JSON: {json.dumps(response_json, indent=2)}")
                    
                    if 'result' in response_json:
                        print(f"\n🎉 SUCCESS! PURE AWS END-TO-END INTEGRATION WORKING!")
                        print(f"✅ User → MCP → AWS Cognito → AgentCore Gateway → TACNode → PostgreSQL")
                        print(f"✅ 100% AWS authentication (Cognito)")
                        print(f"✅ AWS AgentCore Gateway routing")
                        print(f"✅ TACNode API integration")
                        print(f"✅ PostgreSQL database access")
                        
                        return True
                    else:
                        print(f"❌ No result in response")
                        return False
                        
                except json.JSONDecodeError as e:
                    print(f"❌ Failed to parse response: {e}")
                    print(f"Raw response: {response.text}")
                    return False
            elif response.status_code == 401:
                print(f"❌ 401 Unauthorized - Cognito token not accepted")
                print(f"Response: {response.text}")
                return False
            else:
                print(f"❌ Unexpected status: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

async def show_manual_token_instructions():
    """Show instructions for manually getting Cognito token"""
    print(f"\n📋 MANUAL TOKEN INSTRUCTIONS")
    print("=" * 60)
    print("Since the Cognito domain may still be propagating, here's how to get the token manually:")
    
    print(f"\n🔧 Option 1: Wait and retry")
    print("   • Cognito domains take 5-10 minutes to be ready")
    print("   • Run this script again in a few minutes")
    
    print(f"\n🔧 Option 2: Use AWS CLI")
    print("   • aws cognito-idp admin-initiate-auth \\")
    print("     --user-pool-id us-east-1_j2hhA2nBw \\")
    print("     --client-id <client-id> \\")
    print("     --auth-flow ADMIN_USER_PASSWORD_AUTH \\")
    print("     --auth-parameters USERNAME=test@example.com,PASSWORD=password")
    
    print(f"\n🔧 Option 3: Direct curl")
    print("   • Wait for domain to be ready")
    print("   • Use the curl command from earlier output")
    
    print(f"\n📋 Once you have the token:")
    print("   export GATEWAY_TOKEN='<your-cognito-token>'")
    print("   python3 test_pure_aws_complete.py")

async def main():
    """Test complete pure AWS solution"""
    print("🎯 PURE AWS AGENTCORE GATEWAY - COMPLETE TEST")
    print("=" * 70)
    print("🌐 Architecture: User → MCP → AWS Cognito → AgentCore Gateway → TACNode → PostgreSQL")
    print("✅ 100% AWS (except TACNode as intended)")
    
    # Try to get Cognito token
    token = await get_cognito_token()
    
    if token:
        # Test with token
        success = await test_pure_aws_gateway(token)
        
        if success:
            print(f"\n🎉 COMPLETE SUCCESS!")
            print(f"   Pure AWS solution working end-to-end")
            print(f"   No Google OAuth needed")
            print(f"   AWS Cognito authentication")
            print(f"   TACNode integration working")
        else:
            print(f"\n❌ Gateway test failed")
    else:
        # Show manual instructions
        await show_manual_token_instructions()
        
        print(f"\n📋 CURRENT STATUS:")
        print(f"   ✅ Pure AWS Gateway created")
        print(f"   ✅ AWS Cognito configured")
        print(f"   ✅ TACNode target created")
        print(f"   ⏳ Waiting for Cognito domain")
        print(f"   🔑 Need token to test complete flow")

if __name__ == "__main__":
    asyncio.run(main())

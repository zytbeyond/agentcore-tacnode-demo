#!/usr/bin/env python3
"""
Test AgentCore Gateway without token to see what authentication is actually needed
"""

import asyncio
import httpx
import json

async def test_gateway_without_token():
    """Test gateway without token to understand authentication requirements"""
    print("🧪 TESTING GATEWAY WITHOUT TOKEN")
    print("=" * 60)
    
    # Load gateway info
    with open('tacnode-agentcore-gateway.json', 'r') as f:
        gateway_info = json.load(f)
        gateway_id = gateway_info['gatewayId']
    
    with open('tacnode-agentcore-target.json', 'r') as f:
        target_info = json.load(f)
        target_name = target_info['targetName']
    
    # Use the correct gateway URL from AWS response
    gateway_endpoint = f"https://{gateway_id}.gateway.bedrock-agentcore.us-east-1.amazonaws.com"
    gateway_mcp_url = f"{gateway_endpoint}/mcp"
    
    print(f"Gateway ID: {gateway_id}")
    print(f"Gateway Endpoint: {gateway_endpoint}")
    print(f"Gateway MCP URL: {gateway_mcp_url}")
    print(f"Target Name: {target_name}")

    # Test different endpoints to understand authentication
    test_urls = [
        f"{gateway_endpoint}/",
        f"{gateway_mcp_url}",
        f"{gateway_endpoint}/health",
        f"{gateway_endpoint}/targets",
        f"{gateway_endpoint}/targets/{target_name}",
        f"{gateway_endpoint}/targets/{target_name}/invoke"
    ]
    
    for url in test_urls:
        print(f"\n🌐 Testing: {url}")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Test without any authentication
                response = await client.get(url)
                print(f"   Status: {response.status_code}")
                print(f"   Headers: {dict(response.headers)}")
                
                if response.status_code == 401:
                    print(f"   ✅ 401 Unauthorized - Authentication required")
                    print(f"   Response: {response.text[:200]}")
                elif response.status_code == 403:
                    print(f"   ✅ 403 Forbidden - Authorization issue")
                    print(f"   Response: {response.text[:200]}")
                elif response.status_code == 200:
                    print(f"   ✅ 200 OK - No authentication needed!")
                    print(f"   Response: {response.text[:200]}")
                else:
                    print(f"   Status: {response.status_code}")
                    print(f"   Response: {response.text[:200]}")
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")

async def test_gateway_with_aws_credentials():
    """Test gateway using AWS credentials"""
    print(f"\n🧪 TESTING GATEWAY WITH AWS CREDENTIALS")
    print("=" * 60)
    
    # Load gateway info
    with open('tacnode-agentcore-gateway.json', 'r') as f:
        gateway_info = json.load(f)
        gateway_id = gateway_info['gatewayId']
    
    with open('tacnode-agentcore-target.json', 'r') as f:
        target_info = json.load(f)
        target_name = target_info['targetName']
    
    # Use correct gateway URL
    gateway_endpoint = f"https://{gateway_id}.gateway.bedrock-agentcore.us-east-1.amazonaws.com"
    gateway_mcp_url = f"{gateway_endpoint}/mcp"
    
    # Try with AWS signature
    import boto3
    from botocore.auth import SigV4Auth
    from botocore.awsrequest import AWSRequest
    
    session = boto3.Session()
    credentials = session.get_credentials()
    
    print(f"AWS Access Key: {credentials.access_key[:10]}...")
    print(f"Gateway MCP URL: {gateway_mcp_url}")
    
    # Create MCP request
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
    
    try:
        # Create AWS signed request to MCP endpoint
        request = AWSRequest(
            method='POST',
            url=gateway_mcp_url,
            data=json.dumps(mcp_request),
            headers={
                'Content-Type': 'application/json'
            }
        )
        
        # Sign with AWS credentials
        SigV4Auth(credentials, 'bedrock-agentcore', 'us-east-1').add_auth(request)
        
        print(f"Signed headers: {dict(request.headers)}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                gateway_mcp_url,
                content=request.body,
                headers=dict(request.headers)
            )
            
            print(f"Response Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            print(f"Response Body: {response.text}")
            
            if response.status_code == 200:
                print(f"🎉 SUCCESS! AWS credentials work!")
                return True
            else:
                print(f"❌ AWS credentials didn't work")
                return False
                
    except Exception as e:
        print(f"❌ AWS signing failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🔍 UNDERSTANDING GATEWAY AUTHENTICATION")
    print("=" * 60)
    
    # Test 1: No authentication
    await test_gateway_without_token()
    
    # Test 2: AWS credentials
    await test_gateway_with_aws_credentials()

if __name__ == "__main__":
    asyncio.run(main())

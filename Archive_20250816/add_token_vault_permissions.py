#!/usr/bin/env python3
"""
Add specific token vault permissions and test different approaches
"""

import boto3
import json
import time

def add_token_vault_permissions():
    """Add specific token vault permissions to the Gateway role"""
    print("🔑 ADDING TOKEN VAULT PERMISSIONS")
    print("=" * 70)
    
    iam = boto3.client('iam', region_name='us-east-1')
    role_name = "AmazonBedrockAgentCoreGatewayServiceRole"
    
    # The credential provider ARN from the logs
    credential_provider_arn = "arn:aws:bedrock-agentcore:us-east-1:560155322832:token-vault/default/apikeycredentialprovider/tacnode-mcp-token"
    
    print(f"🎯 Target Role: {role_name}")
    print(f"🎯 Credential Provider: {credential_provider_arn}")
    
    try:
        # Add comprehensive token vault permissions
        token_vault_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "bedrock-agentcore:GetCredentialProvider",
                        "bedrock-agentcore:GetApiKeyCredentialProvider",
                        "bedrock-agentcore:ListCredentialProviders",
                        "bedrock-agentcore:DescribeCredentialProvider",
                        "bedrock-agentcore:UseCredentialProvider"
                    ],
                    "Resource": [
                        credential_provider_arn,
                        "arn:aws:bedrock-agentcore:us-east-1:560155322832:token-vault/*",
                        "*"
                    ]
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "bedrock-agentcore:GetTokenVault",
                        "bedrock-agentcore:ListTokenVaults",
                        "bedrock-agentcore:DescribeTokenVault"
                    ],
                    "Resource": "*"
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "secretsmanager:GetSecretValue",
                        "secretsmanager:DescribeSecret"
                    ],
                    "Resource": "*"
                }
            ]
        }
        
        # Update the existing policy
        policy_name = "CredentialProviderAccess"
        
        try:
            iam.put_role_policy(
                RoleName=role_name,
                PolicyName=policy_name,
                PolicyDocument=json.dumps(token_vault_policy)
            )
            print(f"✅ Updated token vault permissions policy: {policy_name}")
            
            # Wait for permissions to propagate
            print(f"⏳ Waiting for permissions to propagate...")
            time.sleep(30)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to update permissions: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Error adding token vault permissions: {e}")
        return False

def test_different_approaches():
    """Test different request approaches to isolate the issue"""
    print(f"\n🧪 TESTING DIFFERENT APPROACHES")
    print("=" * 50)
    
    import asyncio
    import httpx
    import requests
    import base64
    
    # Get Cognito token
    cognito_config = {
        "userPoolId": "us-east-1_qVOK14gn5",
        "clientId": "629cm5j58a7o0lhh1qph1re0l5",
        "clientSecret": "t7uo744afdgrlasjgqe0rsdasdm8ovg91otr12guk4jq79c3d64",
        "tokenEndpoint": "https://us-east-1-qvok14gn5.auth.us-east-1.amazoncognito.com/oauth2/token"
    }
    
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
    
    response = requests.post(token_endpoint, headers=headers, data=data, timeout=30)
    
    if response.status_code != 200:
        print(f"❌ Failed to get Cognito token: {response.status_code}")
        return False
    
    token_data = response.json()
    access_token = token_data['access_token']
    print(f"✅ Got Cognito token")
    
    gateway_url = "https://pureawstacnodegateway-l0f1tg5t8o.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp"
    
    gateway_headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    async def test_approaches():
        async with httpx.AsyncClient(timeout=30.0) as client:
            
            # Test 1: Simple tools/list
            print(f"\n📋 TEST 1: Simple tools/list")
            list_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list"
            }
            
            response = await client.post(gateway_url, json=list_request, headers=gateway_headers)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                response_json = response.json()
                if 'result' in response_json and not response_json['result'].get('isError', False):
                    tools = response_json['result'].get('tools', [])
                    print(f"✅ Tools list successful: {len(tools)} tools")
                    for tool in tools:
                        print(f"  - {tool.get('name', 'Unknown')}")
                else:
                    error_content = response_json.get('result', {}).get('content', [{}])[0].get('text', 'Unknown error')
                    print(f"❌ Tools list failed: {error_content}")
            else:
                print(f"❌ Tools list HTTP error: {response.status_code}")
            
            # Test 2: Simple tool call without nested JSON-RPC
            print(f"\n📋 TEST 2: Simple tool call (no nested JSON-RPC)")
            simple_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "tacnode-mcp___tools_call",
                    "arguments": {
                        "sql": "SELECT 'SIMPLE_TEST' as test_type"
                    }
                }
            }
            
            response = await client.post(gateway_url, json=simple_request, headers=gateway_headers)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                response_json = response.json()
                if 'result' in response_json:
                    if response_json['result'].get('isError', False):
                        error_content = response_json['result'].get('content', [{}])[0].get('text', 'Unknown error')
                        print(f"❌ Simple call failed: {error_content}")
                    else:
                        print(f"✅ Simple call successful!")
                        content = response_json['result'].get('content', [])
                        if content:
                            print(f"📊 Response: {content[0].get('text', 'No text')}")
                else:
                    print(f"❌ No result in response")
            else:
                print(f"❌ Simple call HTTP error: {response.status_code}")
            
            # Test 3: Check if the issue is with the specific target
            print(f"\n📋 TEST 3: Check target configuration")
            
            # Try to call a different tool if available
            list_response = await client.post(gateway_url, json=list_request, headers=gateway_headers)
            if list_response.status_code == 200:
                list_json = list_response.json()
                if 'result' in list_json and not list_json['result'].get('isError', False):
                    tools = list_json['result'].get('tools', [])
                    
                    # Try each tool to see which ones work
                    for tool in tools[:3]:  # Test first 3 tools
                        tool_name = tool.get('name', 'Unknown')
                        print(f"\n🔍 Testing tool: {tool_name}")
                        
                        test_request = {
                            "jsonrpc": "2.0",
                            "id": 1,
                            "method": "tools/call",
                            "params": {
                                "name": tool_name,
                                "arguments": {}
                            }
                        }
                        
                        response = await client.post(gateway_url, json=test_request, headers=gateway_headers)
                        if response.status_code == 200:
                            response_json = response.json()
                            if 'result' in response_json:
                                if response_json['result'].get('isError', False):
                                    error_content = response_json['result'].get('content', [{}])[0].get('text', 'Unknown error')
                                    print(f"  ❌ Tool failed: {error_content}")
                                else:
                                    print(f"  ✅ Tool successful!")
                            else:
                                print(f"  ❌ No result")
                        else:
                            print(f"  ❌ HTTP error: {response.status_code}")
    
    return asyncio.run(test_approaches())

def main():
    """Add token vault permissions and test different approaches"""
    print("🔑 TOKEN VAULT PERMISSIONS AND TESTING")
    print("=" * 70)
    print("🎯 Adding comprehensive token vault permissions")
    print("🎯 Testing different request approaches")
    
    # Add token vault permissions
    permissions_added = add_token_vault_permissions()
    
    if not permissions_added:
        print(f"\n❌ FAILED TO ADD TOKEN VAULT PERMISSIONS")
        return
    
    # Test different approaches
    test_different_approaches()
    
    print(f"\n" + "=" * 70)
    print(f"🔍 TOKEN VAULT PERMISSIONS TESTING COMPLETE")
    print(f"📊 Check the test results above for specific insights")

if __name__ == "__main__":
    main()

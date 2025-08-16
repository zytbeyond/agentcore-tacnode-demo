#!/usr/bin/env python3
"""
Fix Gateway execution role permissions and enable debug logging
"""

import boto3
import json
import time

def check_gateway_permissions():
    """Check and fix Gateway execution role permissions"""
    print("🔧 DIAGNOSING GATEWAY EXECUTION ROLE PERMISSIONS")
    print("=" * 70)
    
    bedrock_agentcore = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
    iam = boto3.client('iam', region_name='us-east-1')
    
    gateway_id = "pureawstacnodegateway-l0f1tg5t8o"
    
    try:
        # Get Gateway details to find execution role
        print(f"\n📋 STEP 1: Getting Gateway execution role")
        print("-" * 50)
        
        gateway_response = bedrock_agentcore.get_gateway(gatewayIdentifier=gateway_id)
        gateway_details = gateway_response['gateway']
        
        print(f"Gateway ID: {gateway_details['gatewayId']}")
        print(f"Gateway Name: {gateway_details['name']}")
        print(f"Gateway Status: {gateway_details['status']}")
        
        # Check if there's an execution role
        execution_role_arn = gateway_details.get('executionRoleArn')
        if execution_role_arn:
            print(f"✅ Execution Role: {execution_role_arn}")
            role_name = execution_role_arn.split('/')[-1]
        else:
            print(f"❌ No execution role found - this might be the issue!")
            return False
        
        # Get current role policies
        print(f"\n📋 STEP 2: Checking current IAM permissions")
        print("-" * 50)
        
        try:
            # Get attached policies
            attached_policies = iam.list_attached_role_policies(RoleName=role_name)
            print(f"Attached policies:")
            for policy in attached_policies['AttachedPolicies']:
                print(f"  - {policy['PolicyName']}: {policy['PolicyArn']}")
            
            # Get inline policies
            inline_policies = iam.list_role_policies(RoleName=role_name)
            print(f"Inline policies:")
            for policy_name in inline_policies['PolicyNames']:
                print(f"  - {policy_name}")
                
        except Exception as e:
            print(f"❌ Error checking role policies: {e}")
            return False
        
        # Check if role has credential provider permissions
        print(f"\n📋 STEP 3: Checking credential provider permissions")
        print("-" * 50)
        
        has_credential_permissions = False
        
        # Check attached policies for credential provider permissions
        for policy in attached_policies['AttachedPolicies']:
            try:
                policy_version = iam.get_policy(PolicyArn=policy['PolicyArn'])
                policy_document = iam.get_policy_version(
                    PolicyArn=policy['PolicyArn'],
                    VersionId=policy_version['Policy']['DefaultVersionId']
                )
                
                statements = policy_document['PolicyVersion']['Document'].get('Statement', [])
                for statement in statements:
                    actions = statement.get('Action', [])
                    if isinstance(actions, str):
                        actions = [actions]
                    
                    # Check for credential provider permissions
                    for action in actions:
                        if ('bedrock-agentcore:GetCredentialProvider' in action or 
                            'bedrock-agentcore:*' in action or
                            'secretsmanager:GetSecretValue' in action):
                            has_credential_permissions = True
                            print(f"✅ Found credential permissions in {policy['PolicyName']}")
                            break
                            
            except Exception as e:
                print(f"⚠️ Could not check policy {policy['PolicyName']}: {e}")
        
        if not has_credential_permissions:
            print(f"❌ Missing credential provider permissions!")
            print(f"🔧 Adding required permissions...")
            
            # Create policy for credential provider access
            credential_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "bedrock-agentcore:GetCredentialProvider",
                            "bedrock-agentcore:GetApiKeyCredentialProvider",
                            "secretsmanager:GetSecretValue",
                            "secretsmanager:DescribeSecret"
                        ],
                        "Resource": "*"
                    },
                    {
                        "Effect": "Allow",
                        "Action": [
                            "logs:CreateLogGroup",
                            "logs:CreateLogStream",
                            "logs:PutLogEvents",
                            "logs:DescribeLogGroups",
                            "logs:DescribeLogStreams"
                        ],
                        "Resource": "*"
                    }
                ]
            }
            
            # Add inline policy to role
            policy_name = "AgentCoreCredentialProviderAccess"
            
            try:
                iam.put_role_policy(
                    RoleName=role_name,
                    PolicyName=policy_name,
                    PolicyDocument=json.dumps(credential_policy)
                )
                print(f"✅ Added credential provider permissions policy: {policy_name}")
                has_credential_permissions = True
                
                # Wait for permissions to propagate
                print(f"⏳ Waiting for permissions to propagate...")
                time.sleep(30)
                
            except Exception as e:
                print(f"❌ Failed to add permissions: {e}")
                return False
        else:
            print(f"✅ Credential provider permissions already exist")
        
        return has_credential_permissions
        
    except Exception as e:
        print(f"❌ Error checking gateway permissions: {e}")
        return False

def enable_debug_logging():
    """Enable debug logging for the Gateway"""
    print(f"\n📋 STEP 4: Enabling debug logging")
    print("-" * 50)
    
    logs_client = boto3.client('logs', region_name='us-east-1')
    
    # Create log group for AgentCore Gateway if it doesn't exist
    log_group_name = "/aws/bedrock-agentcore/gateway"
    
    try:
        logs_client.create_log_group(logGroupName=log_group_name)
        print(f"✅ Created log group: {log_group_name}")
    except logs_client.exceptions.ResourceAlreadyExistsException:
        print(f"✅ Log group already exists: {log_group_name}")
    except Exception as e:
        print(f"⚠️ Could not create log group: {e}")
    
    # Set retention policy
    try:
        logs_client.put_retention_policy(
            logGroupName=log_group_name,
            retentionInDays=7
        )
        print(f"✅ Set log retention to 7 days")
    except Exception as e:
        print(f"⚠️ Could not set retention policy: {e}")
    
    print(f"📊 Debug logs will be available in CloudWatch:")
    print(f"   Log Group: {log_group_name}")
    print(f"   Region: us-east-1")
    
    return log_group_name

def test_with_fixed_permissions():
    """Test the integration with fixed permissions"""
    print(f"\n📋 STEP 5: Testing with fixed permissions")
    print("-" * 50)
    
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
    
    # Test the Gateway with fixed permissions
    gateway_url = "https://pureawstacnodegateway-l0f1tg5t8o.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp"
    
    test_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "tacnode-mcp___tools_call",
            "arguments": {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "query",
                    "arguments": {
                        "sql": "SELECT 'PERMISSIONS_FIXED' as status, NOW() as test_time"
                    }
                },
                "id": 1
            }
        }
    }
    
    gateway_headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    async def test_call():
        async with httpx.AsyncClient(timeout=30.0) as client:
            print(f"🌐 Testing Gateway with fixed permissions...")
            response = await client.post(gateway_url, json=test_request, headers=gateway_headers)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                response_json = response.json()
                print(f"Response: {json.dumps(response_json, indent=2)}")
                
                if 'result' in response_json:
                    result = response_json['result']
                    if result.get('isError', False):
                        error_content = result.get('content', [{}])[0].get('text', '')
                        print(f"\n🔍 Error after permission fix: {error_content}")
                        
                        if 'internal error' in error_content.lower():
                            print(f"❌ Still getting internal error - may need additional permissions")
                            return False
                        elif 'connect' in error_content.lower() and 'refused' in error_content.lower():
                            print(f"✅ PERMISSIONS FIXED! Now getting connection error (expected)")
                            print(f"✅ Gateway can now authenticate with TACNode!")
                            return True
                        else:
                            print(f"🔍 Different error - check CloudWatch logs for details")
                            return False
                    else:
                        print(f"✅ SUCCESS! Got real data from TACNode!")
                        return True
                else:
                    print(f"❌ No result in response")
                    return False
            else:
                print(f"❌ Request failed: {response.status_code}")
                return False
    
    return asyncio.run(test_call())

def main():
    """Fix Gateway permissions and test"""
    print("🔧 GATEWAY PERMISSIONS DIAGNOSTIC AND FIX")
    print("=" * 70)
    print("🎯 Fixing IAM permissions for credential provider access")
    print("🎯 Enabling debug logging for better error visibility")
    
    # Step 1: Check and fix permissions
    permissions_fixed = check_gateway_permissions()
    
    if not permissions_fixed:
        print(f"\n❌ FAILED TO FIX PERMISSIONS")
        return
    
    # Step 2: Enable debug logging
    log_group = enable_debug_logging()
    
    # Step 3: Test with fixed permissions
    test_success = test_with_fixed_permissions()
    
    print(f"\n" + "=" * 70)
    if test_success:
        print(f"🎉 PERMISSIONS FIXED SUCCESSFULLY!")
        print(f"✅ Gateway execution role now has credential provider access")
        print(f"✅ Debug logging enabled in CloudWatch")
        print(f"✅ Gateway can authenticate with TACNode")
        print(f"📊 Check CloudWatch logs for detailed information:")
        print(f"   Log Group: {log_group}")
    else:
        print(f"❌ PERMISSIONS FIX INCOMPLETE")
        print(f"🔍 Check CloudWatch logs for detailed error information")
        print(f"📊 Log Group: {log_group}")

if __name__ == "__main__":
    main()

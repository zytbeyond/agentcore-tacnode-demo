#!/usr/bin/env python3
"""
Create REAL AgentCore Gateway with proper OIDC configuration
Following AWS documentation exactly
"""

import boto3
import json
import time
import base64
import requests

def create_proper_cognito_setup():
    """Create proper Cognito setup for AgentCore Gateway"""
    print("🔐 CREATING PROPER COGNITO SETUP FOR AGENTCORE GATEWAY")
    print("=" * 70)
    
    cognito_idp = boto3.client('cognito-idp', region_name='us-east-1')
    
    try:
        # Step 1: Create user pool
        print("📋 Step 1: Creating Cognito User Pool")
        
        user_pool_response = cognito_idp.create_user_pool(
            PoolName='agentcore-gateway-user-pool',
            Policies={
                'PasswordPolicy': {
                    'MinimumLength': 8,
                    'RequireUppercase': False,
                    'RequireLowercase': False,
                    'RequireNumbers': False,
                    'RequireSymbols': False
                }
            }
        )
        
        user_pool_id = user_pool_response['UserPool']['Id']
        print(f"✅ User Pool created: {user_pool_id}")
        
        # Step 2: Create resource server
        print("📋 Step 2: Creating Resource Server")
        
        resource_server_response = cognito_idp.create_resource_server(
            UserPoolId=user_pool_id,
            Identifier='agentcore-gateway-resource-server',
            Name='AgentCoreGatewayResourceServer',
            Scopes=[
                {
                    'ScopeName': 'read',
                    'ScopeDescription': 'Read access to gateway'
                },
                {
                    'ScopeName': 'write', 
                    'ScopeDescription': 'Write access to gateway'
                }
            ]
        )
        
        print(f"✅ Resource Server created: agentcore-gateway-resource-server")
        
        # Step 3: Create user pool client
        print("📋 Step 3: Creating User Pool Client")
        
        client_response = cognito_idp.create_user_pool_client(
            UserPoolId=user_pool_id,
            ClientName='agentcore-gateway-client',
            GenerateSecret=True,
            AllowedOAuthFlows=['client_credentials'],
            AllowedOAuthScopes=[
                'agentcore-gateway-resource-server/read',
                'agentcore-gateway-resource-server/write'
            ],
            AllowedOAuthFlowsUserPoolClient=True,
            SupportedIdentityProviders=['COGNITO']
        )
        
        client_id = client_response['UserPoolClient']['ClientId']
        client_secret = client_response['UserPoolClient']['ClientSecret']
        print(f"✅ User Pool Client created: {client_id}")
        
        # Step 4: Create domain
        print("📋 Step 4: Creating User Pool Domain")
        
        # Remove underscores from user pool ID for domain
        domain_name = user_pool_id.replace('_', '').lower()
        
        try:
            domain_response = cognito_idp.create_user_pool_domain(
                Domain=domain_name,
                UserPoolId=user_pool_id
            )
            print(f"✅ User Pool Domain created: {domain_name}")
        except Exception as domain_error:
            if 'already exists' in str(domain_error):
                print(f"⚠️ Domain already exists: {domain_name}")
            else:
                print(f"❌ Domain creation failed: {domain_error}")
        
        # Step 5: Construct discovery URL
        discovery_url = f"https://cognito-idp.us-east-1.amazonaws.com/{user_pool_id}/.well-known/openid-configuration"
        token_endpoint = f"https://{domain_name}.auth.us-east-1.amazoncognito.com/oauth2/token"
        
        print(f"✅ Discovery URL: {discovery_url}")
        print(f"✅ Token Endpoint: {token_endpoint}")
        
        # Test the discovery URL
        print("📋 Step 5: Testing OIDC Discovery URL")
        
        try:
            response = requests.get(discovery_url, timeout=10)
            if response.status_code == 200:
                print(f"✅ OIDC Discovery URL is valid and accessible")
                oidc_config = response.json()
                print(f"✅ Issuer: {oidc_config.get('issuer', 'N/A')}")
                print(f"✅ Token Endpoint: {oidc_config.get('token_endpoint', 'N/A')}")
            else:
                print(f"❌ OIDC Discovery URL returned: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ OIDC Discovery URL test failed: {e}")
            return None
        
        cognito_config = {
            'userPoolId': user_pool_id,
            'clientId': client_id,
            'clientSecret': client_secret,
            'discoveryUrl': discovery_url,
            'tokenEndpoint': token_endpoint,
            'domain': domain_name
        }
        
        # Save configuration
        with open('agentcore-cognito-config.json', 'w') as f:
            json.dump(cognito_config, f, indent=2)
        
        print(f"✅ Cognito configuration saved")
        
        return cognito_config
        
    except Exception as e:
        print(f"❌ Error creating Cognito setup: {e}")
        return None

def create_gateway_execution_role():
    """Create IAM role for gateway execution"""
    print(f"\n🔐 CREATING GATEWAY EXECUTION ROLE")
    print("-" * 50)
    
    iam = boto3.client('iam', region_name='us-east-1')
    
    try:
        role_name = f"AgentCoreGatewayRole-{int(time.time())}"
        
        # Trust policy for AgentCore Gateway
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "bedrock-agentcore.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        # Create role
        role_response = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="IAM role for AgentCore Gateway - Created by Augment Agent"
        )
        
        role_arn = role_response['Role']['Arn']
        print(f"✅ Gateway IAM role created: {role_arn}")
        
        # Comprehensive permissions policy
        permissions_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream", 
                        "logs:PutLogEvents",
                        "lambda:InvokeFunction",
                        "lambda:GetFunction",
                        "bedrock-agentcore:*"
                    ],
                    "Resource": "*"
                }
            ]
        }
        
        policy_name = f"AgentCoreGatewayPolicy-{int(time.time())}"
        
        # Create policy
        policy_response = iam.create_policy(
            PolicyName=policy_name,
            PolicyDocument=json.dumps(permissions_policy),
            Description="Permissions for AgentCore Gateway - Created by Augment Agent"
        )
        
        # Attach policy to role
        iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn=policy_response['Policy']['Arn']
        )
        
        print(f"✅ Gateway permissions attached")
        
        # Wait for role to propagate
        print(f"⏳ Waiting for IAM role to propagate...")
        time.sleep(30)
        
        return role_arn
        
    except Exception as e:
        print(f"❌ Error creating gateway role: {e}")
        return None

def create_real_agentcore_gateway():
    """Create real AgentCore Gateway with proper configuration"""
    print(f"\n🏗️ CREATING REAL AGENTCORE GATEWAY")
    print("=" * 70)
    
    # Step 1: Create proper Cognito setup
    cognito_config = create_proper_cognito_setup()
    if not cognito_config:
        print("❌ Failed to create Cognito setup")
        return None, None, None
    
    # Step 2: Create Gateway execution role
    role_arn = create_gateway_execution_role()
    if not role_arn:
        print("❌ Failed to create Gateway execution role")
        return None, None, None
    
    # Step 3: Create the Gateway
    print(f"\n📋 CREATING AGENTCORE GATEWAY")
    print("-" * 50)
    
    bedrock_agentcore = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
    
    try:
        gateway_name = "augment-real-agentcore-gateway"
        
        print(f"📋 Gateway name: {gateway_name}")
        print(f"📋 Role ARN: {role_arn}")
        print(f"📋 Discovery URL: {cognito_config['discoveryUrl']}")
        print(f"📋 Client ID: {cognito_config['clientId']}")
        
        # Create gateway with proper configuration
        gateway_response = bedrock_agentcore.create_gateway(
            name=gateway_name,
            description="Real AgentCore Gateway with Lambda target for TACNode - Created by Augment Agent",
            roleArn=role_arn,
            protocolType="MCP",
            authorizerType="CUSTOM_JWT",
            authorizerConfiguration={
                "customJWTAuthorizer": {
                    "discoveryUrl": cognito_config['discoveryUrl'],
                    "allowedClients": [cognito_config['clientId']]
                }
            }
        )
        
        gateway_id = gateway_response['gatewayId']
        print(f"✅ Gateway created: {gateway_id}")
        
        # Wait for gateway to be ready
        print(f"⏳ Waiting for gateway to be ready...")
        time.sleep(60)  # Give it more time
        
        # Get gateway details
        gateway_details = bedrock_agentcore.get_gateway(gatewayIdentifier=gateway_id)
        gateway_url = gateway_details['gateway']['gatewayUrl']
        gateway_status = gateway_details['gateway']['status']
        
        print(f"✅ Gateway status: {gateway_status}")
        print(f"✅ Gateway URL: {gateway_url}")
        
        return gateway_id, gateway_url, cognito_config
        
    except Exception as e:
        print(f"❌ Error creating gateway: {e}")
        print(f"🔍 Error details: {str(e)}")
        return None, None, None

def main():
    """Main function"""
    print("🚀 REAL AGENTCORE GATEWAY CREATION")
    print("=" * 70)
    print("🎯 Creating real AgentCore Gateway with proper OIDC")
    print("🎯 Following AWS documentation exactly")
    print("🎯 No shortcuts, no simulation - everything real")
    
    gateway_id, gateway_url, cognito_config = create_real_agentcore_gateway()
    
    if gateway_id and gateway_url:
        print(f"\n" + "=" * 70)
        print(f"🎉 REAL AGENTCORE GATEWAY CREATED SUCCESSFULLY!")
        print(f"✅ Gateway ID: {gateway_id}")
        print(f"✅ Gateway URL: {gateway_url}")
        print(f"✅ Cognito User Pool: {cognito_config['userPoolId']}")
        print(f"✅ Client ID: {cognito_config['clientId']}")
        print(f"✅ Discovery URL: {cognito_config['discoveryUrl']}")
        
        print(f"\n🎯 NEXT STEP:")
        print(f"   Add Lambda target to this real Gateway")
        print(f"   Then test real Gateway → Lambda → TACNode flow")
    else:
        print(f"\n❌ FAILED TO CREATE REAL AGENTCORE GATEWAY")

if __name__ == "__main__":
    main()

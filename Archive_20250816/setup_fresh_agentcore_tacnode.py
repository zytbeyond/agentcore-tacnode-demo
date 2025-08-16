#!/usr/bin/env python3
"""
Fresh AgentCore Gateway setup with TACNode integration
Following AWS documentation and TACNode best practices
"""

import boto3
import json
import time
import sys
import os

def get_tacnode_token():
    """Get TACNode token from user input or environment"""
    # Check environment variable first
    token = os.environ.get('TACNODE_TOKEN')
    if token:
        print(f"✅ Found TACNode token in environment variable")
        return token
    
    # Check file
    if os.path.exists('tacnode_token.txt'):
        with open('tacnode_token.txt', 'r') as f:
            token = f.read().strip()
        if token:
            print(f"✅ Found TACNode token in tacnode_token.txt")
            return token
    
    # Ask user for input
    print("🔑 Please provide your TACNode token:")
    print("   You can:")
    print("   1. Set environment variable: export TACNODE_TOKEN=your_token")
    print("   2. Create file tacnode_token.txt with your token")
    print("   3. Enter it now:")
    
    token = input("Enter TACNode token: ").strip()
    if not token:
        print("❌ No token provided. Exiting.")
        sys.exit(1)
    
    return token

def create_fresh_agentcore_gateway():
    """Create a fresh AgentCore Gateway with proper naming"""
    print("🏗️ CREATING FRESH AGENTCORE GATEWAY")
    print("=" * 70)

    bedrock_agentcore = boto3.client('bedrock-agentcore-control', region_name='us-east-1')

    try:
        # First create a basic execution role for gateway creation
        gateway_name = "augment-tacnode-gateway"

        print(f"📋 Creating basic execution role first...")
        basic_role_arn = create_basic_execution_role()
        if not basic_role_arn:
            print(f"❌ Failed to create basic execution role")
            return None, None

        print(f"📋 Creating gateway: {gateway_name}")

        # Custom JWT configuration for authentication (using Cognito)
        authorizer_configuration = {
            "customJWTAuthorizer": {
                "discoveryUrl": "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_qVOK14gn5/.well-known/openid-configuration",
                "allowedAudience": ["629cm5j58a7o0lhh1qph1re0l5"],
                "allowedClients": ["629cm5j58a7o0lhh1qph1re0l5"]
            }
        }

        gateway_response = bedrock_agentcore.create_gateway(
            name=gateway_name,
            description="Fresh AgentCore Gateway for TACNode integration - Created by Augment Agent",
            roleArn=basic_role_arn,
            protocolType="MCP",
            authorizerType="CUSTOM_JWT",
            authorizerConfiguration=authorizer_configuration
        )

        gateway_id = gateway_response['gatewayId']
        print(f"✅ Gateway created: {gateway_id}")

        # Wait for gateway to be ready
        print(f"⏳ Waiting for gateway to be ready...")
        time.sleep(30)

        # Verify gateway status
        gateway_details = bedrock_agentcore.get_gateway(gatewayIdentifier=gateway_id)
        print(f"✅ Gateway status: {gateway_details['gateway']['status']}")
        print(f"✅ Gateway URL: {gateway_details['gateway']['gatewayUrl']}")

        return gateway_id, gateway_details['gateway']['gatewayUrl']

    except Exception as e:
        print(f"❌ Error creating gateway: {e}")
        return None, None

def create_basic_execution_role():
    """Create basic execution role for gateway creation"""
    iam = boto3.client('iam', region_name='us-east-1')

    try:
        role_name = f"augment-agentcore-basic-role-{int(time.time())}"

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
            Description="Basic IAM role for AgentCore Gateway creation - Created by Augment Agent"
        )

        role_arn = role_response['Role']['Arn']

        # Basic permissions policy
        basic_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents"
                    ],
                    "Resource": "*"
                }
            ]
        }

        policy_name = f"augment-agentcore-basic-policy-{int(time.time())}"

        # Create policy
        policy_response = iam.create_policy(
            PolicyName=policy_name,
            PolicyDocument=json.dumps(basic_policy),
            Description="Basic permissions for AgentCore Gateway - Created by Augment Agent"
        )

        # Attach policy to role
        iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn=policy_response['Policy']['Arn']
        )

        # Wait for role to propagate
        time.sleep(15)

        return role_arn

    except Exception as e:
        print(f"❌ Error creating basic execution role: {e}")
        return None

def create_api_key_credential_provider(tacnode_token):
    """Create API key credential provider for TACNode token"""
    print(f"\n🔑 CREATING API KEY CREDENTIAL PROVIDER")
    print("-" * 50)
    
    bedrock_agentcore = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
    
    try:
        provider_name = "augment-tacnode-api-key"
        
        print(f"📋 Creating credential provider: {provider_name}")
        
        provider_response = bedrock_agentcore.create_api_key_credential_provider(
            name=provider_name,
            description="TACNode API key credential provider - Created by Augment Agent",
            apiKey=tacnode_token
        )
        
        provider_arn = provider_response['credentialProviderArn']
        print(f"✅ Credential provider created: {provider_arn}")
        
        return provider_arn
        
    except Exception as e:
        print(f"❌ Error creating credential provider: {e}")
        return None

def create_gateway_execution_role(gateway_id, provider_arn):
    """Create and configure IAM role for gateway execution with comprehensive permissions"""
    print(f"\n🔐 CREATING GATEWAY EXECUTION ROLE")
    print("-" * 50)
    
    iam = boto3.client('iam', region_name='us-east-1')
    
    try:
        role_name = f"augment-agentcore-gateway-role-{gateway_id[:8]}"
        
        # Trust policy for AgentCore Gateway
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "bedrock-agentcore.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole",
                    "Condition": {
                        "StringEquals": {
                            "aws:SourceAccount": boto3.Session().get_credentials().access_key.split(':')[4] if ':' in boto3.Session().get_credentials().access_key else boto3.client('sts').get_caller_identity()['Account']
                        }
                    }
                }
            ]
        }
        
        print(f"📋 Creating IAM role: {role_name}")
        
        # Create role
        role_response = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="IAM role for AgentCore Gateway execution - Created by Augment Agent",
            MaxSessionDuration=3600
        )
        
        role_arn = role_response['Role']['Arn']
        print(f"✅ IAM role created: {role_arn}")
        
        # Get account ID
        account_id = boto3.client('sts').get_caller_identity()['Account']
        
        # Comprehensive permissions policy
        permissions_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "AgentCoreGatewayBasicPermissions",
                    "Effect": "Allow",
                    "Action": [
                        "bedrock-agentcore:*",
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents"
                    ],
                    "Resource": "*"
                },
                {
                    "Sid": "GetResourceApiKey",
                    "Effect": "Allow",
                    "Action": [
                        "bedrock-agentcore:GetResourceApiKey"
                    ],
                    "Resource": [
                        provider_arn
                    ]
                },
                {
                    "Sid": "TokenVaultAccess",
                    "Effect": "Allow",
                    "Action": [
                        "bedrock-agentcore:GetWorkloadAccessToken",
                        "bedrock-agentcore:GetResourceApiKey",
                        "bedrock-agentcore:GetResourceOauth2Token"
                    ],
                    "Resource": [
                        f"arn:aws:bedrock-agentcore:us-east-1:{account_id}:token-vault/default",
                        f"arn:aws:bedrock-agentcore:us-east-1:{account_id}:token-vault/default/*",
                        f"arn:aws:bedrock-agentcore:us-east-1:{account_id}:workload-identity-directory/default",
                        f"arn:aws:bedrock-agentcore:us-east-1:{account_id}:workload-identity-directory/default/*"
                    ]
                },
                {
                    "Sid": "SecretsManagerAccess",
                    "Effect": "Allow",
                    "Action": [
                        "secretsmanager:GetSecretValue"
                    ],
                    "Resource": [
                        f"arn:aws:secretsmanager:us-east-1:{account_id}:secret:*"
                    ]
                }
            ]
        }
        
        policy_name = f"augment-agentcore-gateway-policy-{gateway_id[:8]}"
        
        print(f"📋 Creating IAM policy: {policy_name}")
        
        # Create policy
        policy_response = iam.create_policy(
            PolicyName=policy_name,
            PolicyDocument=json.dumps(permissions_policy),
            Description="Comprehensive permissions for AgentCore Gateway - Created by Augment Agent"
        )
        
        policy_arn = policy_response['Policy']['Arn']
        print(f"✅ IAM policy created: {policy_arn}")
        
        # Attach policy to role
        iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn=policy_arn
        )
        
        print(f"✅ Policy attached to role")
        
        # Wait for role to propagate
        print(f"⏳ Waiting for IAM role to propagate...")
        time.sleep(30)
        
        return role_arn
        
    except Exception as e:
        print(f"❌ Error creating IAM role: {e}")
        return None

def update_gateway_execution_role(gateway_id, role_arn):
    """Update gateway with execution role"""
    print(f"\n🔧 UPDATING GATEWAY WITH EXECUTION ROLE")
    print("-" * 50)
    
    bedrock_agentcore = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
    
    try:
        print(f"📋 Updating gateway {gateway_id} with role {role_arn}")
        
        bedrock_agentcore.update_gateway(
            gatewayIdentifier=gateway_id,
            executionRoleArn=role_arn
        )
        
        print(f"✅ Gateway updated with execution role")
        
        # Wait for update to propagate
        time.sleep(15)
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating gateway: {e}")
        return False

def create_tacnode_target(gateway_id, provider_arn):
    """Create TACNode target with proper OpenAPI schema"""
    print(f"\n🎯 CREATING TACNODE TARGET")
    print("-" * 50)
    
    bedrock_agentcore = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
    
    try:
        # Minimal OpenAPI schema for TACNode (JSON-only as per AWS docs)
        openapi_schema = {
            "openapi": "3.0.1",
            "info": {
                "title": "TACNode MCP Server",
                "version": "1.0.0",
                "description": "TACNode Managed MCP Server for database queries"
            },
            "servers": [
                {
                    "url": "https://mcp-server.tacnode.io"
                }
            ],
            "paths": {
                "/mcp": {
                    "post": {
                        "operationId": "mcp_call",
                        "summary": "Execute MCP calls on TACNode",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "jsonrpc": {
                                                "type": "string",
                                                "example": "2.0"
                                            },
                                            "method": {
                                                "type": "string",
                                                "example": "tools/call"
                                            },
                                            "params": {
                                                "type": "object"
                                            },
                                            "id": {
                                                "type": "integer",
                                                "example": 1
                                            }
                                        },
                                        "required": ["jsonrpc", "method", "id"]
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "Successful MCP response",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "jsonrpc": {
                                                    "type": "string"
                                                },
                                                "result": {
                                                    "type": "object"
                                                },
                                                "id": {
                                                    "type": "integer"
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        target_name = "augment-tacnode-mcp"
        
        print(f"📋 Creating target: {target_name}")
        print(f"📊 Using TACNode endpoint: https://mcp-server.tacnode.io/mcp")
        
        # Target configuration
        target_configuration = {
            "mcp": {
                "openApiSchema": {
                    "inlinePayload": json.dumps(openapi_schema)
                }
            }
        }
        
        # Credential provider configuration (exactly one as per AWS docs)
        credential_provider_configurations = [
            {
                "credentialProviderType": "API_KEY",
                "credentialProvider": {
                    "apiKeyCredentialProvider": {
                        "providerArn": provider_arn,
                        "credentialLocation": "HEADER",
                        "credentialParameterName": "Authorization",
                        "credentialPrefix": "Bearer "
                    }
                }
            }
        ]
        
        # Create target
        target_response = bedrock_agentcore.create_gateway_target(
            gatewayIdentifier=gateway_id,
            name=target_name,
            description="TACNode MCP Server target for database queries - Created by Augment Agent",
            targetConfiguration=target_configuration,
            credentialProviderConfigurations=credential_provider_configurations
        )
        
        target_id = target_response['targetId']
        print(f"✅ Target created: {target_id}")
        
        # Wait for target to be ready
        print(f"⏳ Waiting for target to be ready...")
        time.sleep(30)
        
        # Verify target
        target_details = bedrock_agentcore.get_gateway_target(
            gatewayIdentifier=gateway_id,
            targetId=target_id
        )
        
        print(f"✅ Target status: {target_details['target']['status']}")
        
        return target_id
        
    except Exception as e:
        print(f"❌ Error creating target: {e}")
        return None

def save_configuration(gateway_id, gateway_url, provider_arn, role_arn, target_id):
    """Save configuration to file"""
    config = {
        "gateway": {
            "id": gateway_id,
            "url": gateway_url,
            "name": "augment-tacnode-gateway"
        },
        "credentialProvider": {
            "arn": provider_arn,
            "name": "augment-tacnode-api-key"
        },
        "executionRole": {
            "arn": role_arn
        },
        "target": {
            "id": target_id,
            "name": "augment-tacnode-mcp"
        },
        "tacnode": {
            "endpoint": "https://mcp-server.tacnode.io/mcp",
            "database": "postgres",
            "table": "test"
        },
        "cognito": {
            "userPoolId": "us-east-1_qVOK14gn5",
            "clientId": "629cm5j58a7o0lhh1qph1re0l5",
            "clientSecret": "t7uo744afdgrlasjgqe0rsdasdm8ovg91otr12guk4jq79c3d64",
            "tokenEndpoint": "https://us-east-1-qvok14gn5.auth.us-east-1.amazoncognito.com/oauth2/token"
        },
        "created_by": "Augment Agent",
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    }
    
    with open('augment-agentcore-tacnode-config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Configuration saved to: augment-agentcore-tacnode-config.json")
    
    return config

def main():
    """Main setup function"""
    print("🚀 FRESH AGENTCORE GATEWAY + TACNODE SETUP")
    print("=" * 70)
    print("🎯 Creating new AgentCore Gateway with TACNode integration")
    print("🎯 Following AWS documentation best practices")
    print("🎯 All resources prefixed with 'augment-' for identification")
    
    # Get TACNode token
    tacnode_token = get_tacnode_token()
    
    # Step 1: Create fresh gateway
    gateway_id, gateway_url = create_fresh_agentcore_gateway()
    if not gateway_id:
        print("❌ Failed to create gateway. Exiting.")
        return
    
    # Step 2: Create credential provider
    provider_arn = create_api_key_credential_provider(tacnode_token)
    if not provider_arn:
        print("❌ Failed to create credential provider. Exiting.")
        return
    
    # Step 3: Create execution role with comprehensive permissions
    role_arn = create_gateway_execution_role(gateway_id, provider_arn)
    if not role_arn:
        print("❌ Failed to create execution role. Exiting.")
        return
    
    # Step 4: Update gateway with execution role
    if not update_gateway_execution_role(gateway_id, role_arn):
        print("❌ Failed to update gateway with execution role. Exiting.")
        return
    
    # Step 5: Create TACNode target
    target_id = create_tacnode_target(gateway_id, provider_arn)
    if not target_id:
        print("❌ Failed to create TACNode target. Exiting.")
        return
    
    # Step 6: Save configuration
    config = save_configuration(gateway_id, gateway_url, provider_arn, role_arn, target_id)
    
    print(f"\n" + "=" * 70)
    print(f"🎉 FRESH AGENTCORE GATEWAY SETUP COMPLETE!")
    print(f"✅ Gateway ID: {gateway_id}")
    print(f"✅ Gateway URL: {gateway_url}")
    print(f"✅ Target ID: {target_id}")
    print(f"✅ All resources created with 'augment-' prefix")
    print(f"✅ Configuration saved to: augment-agentcore-tacnode-config.json")
    
    print(f"\n🧪 NEXT STEPS:")
    print(f"1. Run the test script to verify the integration")
    print(f"2. Use the gateway URL for MCP calls")
    print(f"3. Query the 'test' table in 'postgres' database")

if __name__ == "__main__":
    main()

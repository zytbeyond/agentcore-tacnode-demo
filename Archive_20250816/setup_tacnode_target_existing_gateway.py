#!/usr/bin/env python3
"""
Add TACNode target to existing AgentCore Gateway
Using the working gateway we already have
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
    
    print("❌ No TACNode token found. Please provide it.")
    sys.exit(1)

def create_api_key_credential_provider(tacnode_token):
    """Create API key credential provider for TACNode token"""
    print(f"\n🔑 CREATING API KEY CREDENTIAL PROVIDER")
    print("-" * 50)
    
    bedrock_agentcore = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
    
    try:
        provider_name = "augment-tacnode-api-key-fresh"
        
        print(f"📋 Creating credential provider: {provider_name}")
        
        provider_response = bedrock_agentcore.create_api_key_credential_provider(
            name=provider_name,
            apiKey=tacnode_token
        )
        
        provider_arn = provider_response['credentialProviderArn']
        print(f"✅ Credential provider created: {provider_arn}")
        
        return provider_arn
        
    except Exception as e:
        print(f"❌ Error creating credential provider: {e}")
        return None

def update_gateway_execution_role_permissions(gateway_id, provider_arn):
    """Update the existing gateway execution role with comprehensive permissions"""
    print(f"\n🔐 UPDATING GATEWAY EXECUTION ROLE PERMISSIONS")
    print("-" * 50)
    
    bedrock_agentcore = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
    iam = boto3.client('iam', region_name='us-east-1')
    
    try:
        # Get current gateway details
        gateway_details = bedrock_agentcore.get_gateway(gatewayIdentifier=gateway_id)
        current_role_arn = gateway_details['gateway']['roleArn']
        
        print(f"📋 Current gateway role: {current_role_arn}")
        
        # Extract role name from ARN
        role_name = current_role_arn.split('/')[-1]
        
        # Get account ID
        account_id = boto3.client('sts').get_caller_identity()['Account']
        
        # Create comprehensive permissions policy
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
        
        policy_name = f"augment-tacnode-permissions-{int(time.time())}"
        
        print(f"📋 Creating comprehensive IAM policy: {policy_name}")
        
        # Create policy
        policy_response = iam.create_policy(
            PolicyName=policy_name,
            PolicyDocument=json.dumps(permissions_policy),
            Description="Comprehensive permissions for TACNode integration - Created by Augment Agent"
        )
        
        policy_arn = policy_response['Policy']['Arn']
        print(f"✅ IAM policy created: {policy_arn}")
        
        # Attach policy to existing role
        iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn=policy_arn
        )
        
        print(f"✅ Policy attached to existing gateway role")
        
        # Wait for permissions to propagate
        print(f"⏳ Waiting for permissions to propagate...")
        time.sleep(30)
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating role permissions: {e}")
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
        
        target_name = "augment-tacnode-mcp-fresh"
        
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
            description="TACNode MCP Server target for database queries - Created by Augment Agent (Fresh)",
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

def save_configuration(gateway_id, gateway_url, provider_arn, target_id):
    """Save configuration to file"""
    config = {
        "gateway": {
            "id": gateway_id,
            "url": gateway_url,
            "name": "existing-gateway-with-tacnode"
        },
        "credentialProvider": {
            "arn": provider_arn,
            "name": "augment-tacnode-api-key-fresh"
        },
        "target": {
            "id": target_id,
            "name": "augment-tacnode-mcp-fresh"
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
    
    with open('augment-tacnode-existing-gateway-config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Configuration saved to: augment-tacnode-existing-gateway-config.json")
    
    return config

def main():
    """Main setup function"""
    print("🚀 TACNODE TARGET SETUP ON EXISTING GATEWAY")
    print("=" * 70)
    print("🎯 Adding TACNode target to existing working gateway")
    print("🎯 Following AWS documentation best practices")
    print("🎯 All resources prefixed with 'augment-' for identification")
    
    # Use existing working gateway
    gateway_id = "pureawstacnodegateway-l0f1tg5t8o"
    gateway_url = "https://pureawstacnodegateway-l0f1tg5t8o.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp"
    
    print(f"✅ Using existing gateway: {gateway_id}")
    print(f"✅ Gateway URL: {gateway_url}")
    
    # Get TACNode token
    tacnode_token = get_tacnode_token()
    
    # Step 1: Create credential provider
    provider_arn = create_api_key_credential_provider(tacnode_token)
    if not provider_arn:
        print("❌ Failed to create credential provider. Exiting.")
        return
    
    # Step 2: Update gateway execution role permissions
    if not update_gateway_execution_role_permissions(gateway_id, provider_arn):
        print("❌ Failed to update gateway permissions. Exiting.")
        return
    
    # Step 3: Create TACNode target
    target_id = create_tacnode_target(gateway_id, provider_arn)
    if not target_id:
        print("❌ Failed to create TACNode target. Exiting.")
        return
    
    # Step 4: Save configuration
    config = save_configuration(gateway_id, gateway_url, provider_arn, target_id)
    
    print(f"\n" + "=" * 70)
    print(f"🎉 TACNODE TARGET SETUP COMPLETE!")
    print(f"✅ Gateway ID: {gateway_id}")
    print(f"✅ Gateway URL: {gateway_url}")
    print(f"✅ Target ID: {target_id}")
    print(f"✅ All resources created with 'augment-' prefix")
    print(f"✅ Configuration saved to: augment-tacnode-existing-gateway-config.json")
    
    print(f"\n🧪 NEXT STEPS:")
    print(f"1. Run the test script to verify the integration")
    print(f"2. Use the gateway URL for MCP calls")
    print(f"3. Query the 'test' table in 'postgres' database")

if __name__ == "__main__":
    main()

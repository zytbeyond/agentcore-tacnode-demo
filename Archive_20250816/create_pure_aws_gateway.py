#!/usr/bin/env python3
"""
Create a new AgentCore Gateway with pure AWS Cognito authentication
Delete the old Google OAuth gateway and create a proper AWS one
"""

import boto3
import json
import time
from datetime import datetime

class PureAWSGatewayCreator:
    """Create pure AWS gateway with Cognito authentication"""
    
    def __init__(self):
        self.cognito_client = boto3.client('cognito-idp', region_name='us-east-1')
        self.bedrock_agentcore = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
        self.iam_client = boto3.client('iam', region_name='us-east-1')
        
        print("🔧 CREATING PURE AWS AGENTCORE GATEWAY")
        print("=" * 60)
        print("🎯 Goal: 100% AWS solution (TACNode is only external)")
    
    def create_cognito_setup(self):
        """Create Cognito User Pool and Client"""
        print("\n📋 STEP 1: Creating AWS Cognito Setup")
        print("-" * 50)
        
        pool_name = "PureAWSAgentCoreGateway"
        
        try:
            # Create Cognito User Pool
            pool_response = self.cognito_client.create_user_pool(
                PoolName=pool_name,
                Policies={
                    'PasswordPolicy': {
                        'MinimumLength': 8,
                        'RequireUppercase': False,
                        'RequireLowercase': False,
                        'RequireNumbers': False,
                        'RequireSymbols': False
                    }
                },
                AutoVerifiedAttributes=['email'],
                UsernameAttributes=['email'],
                Schema=[
                    {
                        'Name': 'email',
                        'AttributeDataType': 'String',
                        'Required': True,
                        'Mutable': True
                    }
                ]
            )
            
            user_pool_id = pool_response['UserPool']['Id']
            
            # Create User Pool Client
            client_response = self.cognito_client.create_user_pool_client(
                UserPoolId=user_pool_id,
                ClientName="PureAWSGatewayClient",
                GenerateSecret=False,
                ExplicitAuthFlows=[
                    'ALLOW_ADMIN_USER_PASSWORD_AUTH',
                    'ALLOW_USER_PASSWORD_AUTH',
                    'ALLOW_REFRESH_TOKEN_AUTH'
                ],
                TokenValidityUnits={
                    'AccessToken': 'hours',
                    'IdToken': 'hours'
                },
                AccessTokenValidity=24,
                IdTokenValidity=24
            )
            
            client_id = client_response['UserPoolClient']['ClientId']
            
            print(f"✅ Cognito User Pool: {user_pool_id}")
            print(f"✅ Cognito Client: {client_id}")
            
            return {
                "userPoolId": user_pool_id,
                "clientId": client_id,
                "discoveryUrl": f"https://cognito-idp.us-east-1.amazonaws.com/{user_pool_id}/.well-known/openid_configuration"
            }
            
        except Exception as e:
            print(f"❌ Cognito setup failed: {e}")
            return None
    
    def create_test_user(self, cognito_config):
        """Create test user in Cognito"""
        print("\n📋 STEP 2: Creating Test User")
        print("-" * 50)
        
        test_email = "aws-gateway-test@example.com"
        test_password = "AWSGateway123!"
        
        try:
            self.cognito_client.admin_create_user(
                UserPoolId=cognito_config['userPoolId'],
                Username=test_email,
                UserAttributes=[
                    {'Name': 'email', 'Value': test_email},
                    {'Name': 'email_verified', 'Value': 'true'}
                ],
                TemporaryPassword=test_password,
                MessageAction='SUPPRESS'
            )
            
            self.cognito_client.admin_set_user_password(
                UserPoolId=cognito_config['userPoolId'],
                Username=test_email,
                Password=test_password,
                Permanent=True
            )
            
            print(f"✅ Test user: {test_email}")
            print(f"✅ Password: {test_password}")
            
            return {"email": test_email, "password": test_password}
            
        except Exception as e:
            print(f"❌ Test user creation failed: {e}")
            return None
    
    def delete_old_gateway(self):
        """Delete the old Google OAuth gateway"""
        print("\n📋 STEP 3: Cleaning Up Old Gateway")
        print("-" * 50)
        
        old_gateway_id = "tacnodecontextlakegateway-bkq6ozcvxp"
        
        try:
            # First, delete all targets
            targets_response = self.bedrock_agentcore.list_gateway_targets(
                gatewayIdentifier=old_gateway_id
            )
            
            for target in targets_response.get('gatewayTargets', []):
                target_id = target['targetId']
                print(f"   Deleting target: {target_id}")
                self.bedrock_agentcore.delete_gateway_target(
                    gatewayIdentifier=old_gateway_id,
                    targetId=target_id
                )
            
            # Delete the gateway
            print(f"   Deleting gateway: {old_gateway_id}")
            self.bedrock_agentcore.delete_gateway(
                gatewayIdentifier=old_gateway_id
            )
            
            print(f"✅ Old gateway deleted")
            return True
            
        except Exception as e:
            print(f"⚠️  Old gateway deletion failed (might not exist): {e}")
            return False
    
    def create_pure_aws_gateway(self, cognito_config):
        """Create new gateway with pure AWS Cognito authentication"""
        print("\n📋 STEP 4: Creating Pure AWS Gateway")
        print("-" * 50)
        
        try:
            # Create gateway with Cognito authentication
            response = self.bedrock_agentcore.create_gateway(
                name="PureAWSTACNodeGateway",
                description="Pure AWS AgentCore Gateway for TACNode - Cognito authentication",
                roleArn="arn:aws:iam::560155322832:role/AmazonBedrockAgentCoreGatewayServiceRole",
                protocolType="MCP",
                protocolConfiguration={
                    "mcp": {
                        "supportedVersions": ["2025-03-26"],
                        "instructions": "Pure AWS Gateway for TACNode Context Lake with Cognito authentication",
                        "searchType": "SEMANTIC"
                    }
                },
                authorizerType="CUSTOM_JWT",
                authorizerConfiguration={
                    "customJWTAuthorizer": {
                        "discoveryUrl": cognito_config['discoveryUrl'],
                        "allowedAudience": [cognito_config['clientId']],
                        "allowedClients": ["aws-agentcore-gateway", "tacnode-client"]
                    }
                }
            )
            
            gateway_id = response['gatewayId']
            gateway_url = response['gatewayUrl']
            
            print(f"✅ Pure AWS Gateway created:")
            print(f"   Gateway ID: {gateway_id}")
            print(f"   Gateway URL: {gateway_url}")
            print(f"   Authentication: AWS Cognito")
            
            # Save gateway configuration
            gateway_config = {
                "gatewayId": gateway_id,
                "gatewayUrl": gateway_url,
                "name": "PureAWSTACNodeGateway",
                "authorizerType": "CUSTOM_JWT",
                "cognitoConfig": cognito_config,
                "created": datetime.now().isoformat()
            }
            
            with open('pure-aws-gateway.json', 'w') as f:
                json.dump(gateway_config, f, indent=2)
            
            return gateway_config
            
        except Exception as e:
            print(f"❌ Gateway creation failed: {e}")
            return None
    
    def create_tacnode_target(self, gateway_config):
        """Create TACNode target for the new gateway"""
        print("\n📋 STEP 5: Creating TACNode Target")
        print("-" * 50)
        
        gateway_id = gateway_config['gatewayId']
        
        # Load TACNode OpenAPI spec
        try:
            with open('tacnode_openapi_spec.json', 'r') as f:
                openapi_spec = json.load(f)
        except FileNotFoundError:
            print("❌ TACNode OpenAPI spec not found")
            return None
        
        try:
            # Create credential provider for TACNode
            cred_response = self.bedrock_agentcore.create_api_key_credential_provider(
                name="TACNodeAPIKeyProvider",
                description="API Key provider for TACNode authentication",
                secretArn="arn:aws:secretsmanager:us-east-1:560155322832:secret:tacnode-api-key-final-8Lw7Ej"
            )
            
            cred_provider_id = cred_response['credentialProviderId']
            print(f"✅ Credential provider: {cred_provider_id}")
            
            # Create TACNode target
            target_response = self.bedrock_agentcore.create_gateway_target(
                gatewayIdentifier=gateway_id,
                name="pure-aws-tacnode-target",
                description="TACNode Context Lake target with pure AWS authentication",
                targetType="OPENAPI",
                openAPIConfiguration={
                    "openAPISpecification": json.dumps(openapi_spec),
                    "credentialProviderId": cred_provider_id
                }
            )
            
            target_id = target_response['targetId']
            print(f"✅ TACNode target created: {target_id}")
            
            # Update gateway config
            gateway_config['targetId'] = target_id
            gateway_config['targetName'] = "pure-aws-tacnode-target"
            gateway_config['credentialProviderId'] = cred_provider_id
            
            with open('pure-aws-gateway.json', 'w') as f:
                json.dump(gateway_config, f, indent=2)
            
            return target_id
            
        except Exception as e:
            print(f"❌ Target creation failed: {e}")
            return None
    
    def get_cognito_token(self, cognito_config, test_user):
        """Get Cognito JWT token"""
        print("\n📋 STEP 6: Getting AWS Cognito Token")
        print("-" * 50)
        
        try:
            response = self.cognito_client.admin_initiate_auth(
                UserPoolId=cognito_config['userPoolId'],
                ClientId=cognito_config['clientId'],
                AuthFlow='ADMIN_USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': test_user['email'],
                    'PASSWORD': test_user['password']
                }
            )
            
            access_token = response['AuthenticationResult']['AccessToken']
            
            print(f"✅ AWS Cognito token obtained")
            print(f"   Token: {access_token[:50]}...")
            
            print(f"\n🔑 GATEWAY_TOKEN for testing:")
            print(f"export GATEWAY_TOKEN='{access_token}'")
            
            return access_token
            
        except Exception as e:
            print(f"❌ Token generation failed: {e}")
            return None
    
    async def create_complete_pure_aws_solution(self):
        """Create complete pure AWS solution"""
        print("🔧 CREATING COMPLETE PURE AWS SOLUTION")
        print("=" * 70)
        
        # Step 1: Create Cognito
        cognito_config = self.create_cognito_setup()
        if not cognito_config:
            return False
        
        # Step 2: Create test user
        test_user = self.create_test_user(cognito_config)
        if not test_user:
            return False
        
        # Step 3: Delete old gateway
        self.delete_old_gateway()
        
        # Step 4: Create new gateway
        gateway_config = self.create_pure_aws_gateway(cognito_config)
        if not gateway_config:
            return False
        
        # Step 5: Create TACNode target
        target_id = self.create_tacnode_target(gateway_config)
        if not target_id:
            return False
        
        # Step 6: Get token
        token = self.get_cognito_token(cognito_config, test_user)
        if not token:
            return False
        
        print("\n🎉 PURE AWS SOLUTION COMPLETE!")
        print("=" * 70)
        print("✅ AWS COMPONENTS:")
        print(f"   • AgentCore Gateway: {gateway_config['gatewayId']}")
        print(f"   • Cognito User Pool: {cognito_config['userPoolId']}")
        print(f"   • Cognito Client: {cognito_config['clientId']}")
        print(f"   • Target: {target_id}")
        print(f"   • Secrets Manager: TACNode API key")
        
        print("\n🌐 EXTERNAL COMPONENTS:")
        print("   • TACNode: mcp-server.tacnode.io (ONLY external)")
        
        print("\n🔑 AUTHENTICATION:")
        print("   • 100% AWS Cognito")
        print("   • No Google OAuth")
        print("   • Pure AWS end-to-end")
        
        print(f"\n🧪 TEST COMMAND:")
        print(f"export GATEWAY_TOKEN='{token}'")
        print("python3 test_tacnode_rest_api_direct.py")
        
        return True

async def main():
    print("🔧 Pure AWS AgentCore Gateway Creator")
    print("=" * 60)
    
    try:
        creator = PureAWSGatewayCreator()
        success = await creator.create_complete_pure_aws_solution()
        
        if success:
            print("\n✅ PURE AWS SOLUTION READY!")
        else:
            print("\n❌ CREATION FAILED!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

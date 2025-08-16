#!/usr/bin/env python3
"""
Reconfigure AgentCore Gateway to use AWS Cognito instead of Google OAuth
Pure AWS end-to-end solution - TACNode is the only external component
"""

import boto3
import json
import time
from datetime import datetime

class AWSCognitoGatewayReconfiguration:
    """Reconfigure gateway to use AWS Cognito for pure AWS solution"""
    
    def __init__(self):
        self.cognito_client = boto3.client('cognito-idp', region_name='us-east-1')
        self.bedrock_agentcore = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
        
        # Load gateway info
        with open('tacnode-agentcore-gateway.json', 'r') as f:
            self.gateway_info = json.load(f)
            self.gateway_id = self.gateway_info['gatewayId']
        
        print("🔧 RECONFIGURING GATEWAY TO USE AWS COGNITO")
        print("=" * 60)
        print(f"✅ Gateway ID: {self.gateway_id}")
        print("🎯 Goal: Pure AWS end-to-end solution")
        print("🌐 External: Only TACNode")
    
    def create_cognito_user_pool(self):
        """Create AWS Cognito User Pool for gateway authentication"""
        print("\n📋 STEP 1: Creating AWS Cognito User Pool")
        print("-" * 50)
        
        pool_name = "AgentCoreGatewayUserPool"
        
        try:
            # Create Cognito User Pool
            response = self.cognito_client.create_user_pool(
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
                ],
                AdminCreateUserConfig={
                    'AllowAdminCreateUserOnly': False
                }
            )
            
            user_pool_id = response['UserPool']['Id']
            user_pool_arn = response['UserPool']['Arn']
            
            print(f"✅ Cognito User Pool created:")
            print(f"   Pool ID: {user_pool_id}")
            print(f"   Pool ARN: {user_pool_arn}")
            
            # Create User Pool Client
            client_response = self.cognito_client.create_user_pool_client(
                UserPoolId=user_pool_id,
                ClientName="AgentCoreGatewayClient",
                GenerateSecret=False,  # For simplicity, no client secret
                ExplicitAuthFlows=[
                    'ALLOW_ADMIN_USER_PASSWORD_AUTH',
                    'ALLOW_USER_PASSWORD_AUTH',
                    'ALLOW_REFRESH_TOKEN_AUTH'
                ],
                TokenValidityUnits={
                    'AccessToken': 'hours',
                    'IdToken': 'hours',
                    'RefreshToken': 'days'
                },
                AccessTokenValidity=24,
                IdTokenValidity=24,
                RefreshTokenValidity=30
            )
            
            client_id = client_response['UserPoolClient']['ClientId']
            
            print(f"✅ Cognito User Pool Client created:")
            print(f"   Client ID: {client_id}")
            
            # Save Cognito configuration
            cognito_config = {
                "userPoolId": user_pool_id,
                "userPoolArn": user_pool_arn,
                "clientId": client_id,
                "region": "us-east-1",
                "jwksUrl": f"https://cognito-idp.us-east-1.amazonaws.com/{user_pool_id}/.well-known/jwks.json",
                "issuer": f"https://cognito-idp.us-east-1.amazonaws.com/{user_pool_id}",
                "created": datetime.now().isoformat()
            }
            
            with open('cognito-gateway-config.json', 'w') as f:
                json.dump(cognito_config, f, indent=2)
            
            return cognito_config
            
        except Exception as e:
            print(f"❌ Cognito User Pool creation failed: {e}")
            return None
    
    def create_test_user(self, cognito_config):
        """Create a test user in Cognito"""
        print("\n📋 STEP 2: Creating Test User")
        print("-" * 50)
        
        user_pool_id = cognito_config['userPoolId']
        test_email = "agentcore-test@example.com"
        test_password = "TempPassword123!"
        
        try:
            # Create test user
            self.cognito_client.admin_create_user(
                UserPoolId=user_pool_id,
                Username=test_email,
                UserAttributes=[
                    {
                        'Name': 'email',
                        'Value': test_email
                    },
                    {
                        'Name': 'email_verified',
                        'Value': 'true'
                    }
                ],
                TemporaryPassword=test_password,
                MessageAction='SUPPRESS'  # Don't send welcome email
            )
            
            print(f"✅ Test user created:")
            print(f"   Email: {test_email}")
            print(f"   Temp Password: {test_password}")
            
            # Set permanent password
            self.cognito_client.admin_set_user_password(
                UserPoolId=user_pool_id,
                Username=test_email,
                Password=test_password,
                Permanent=True
            )
            
            print(f"✅ Password set as permanent")
            
            return {
                "email": test_email,
                "password": test_password
            }
            
        except Exception as e:
            print(f"❌ Test user creation failed: {e}")
            return None
    
    def update_gateway_to_cognito(self, cognito_config):
        """Update AgentCore Gateway to use Cognito instead of Google OAuth"""
        print("\n📋 STEP 3: Updating Gateway to Use Cognito")
        print("-" * 50)
        
        try:
            # Create new authorizer configuration for Cognito
            # Use the correct Cognito discovery URL format
            cognito_authorizer_config = {
                "customJWTAuthorizer": {
                    "discoveryUrl": f"https://cognito-idp.us-east-1.amazonaws.com/{cognito_config['userPoolId']}/.well-known/openid-configuration",
                    "allowedAudience": [cognito_config['clientId']],
                    "allowedClients": ["agentcore-gateway", "tacnode-client"]
                }
            }
            
            print(f"New authorizer configuration:")
            print(json.dumps(cognito_authorizer_config, indent=2))
            
            # Update gateway with all required parameters
            response = self.bedrock_agentcore.update_gateway(
                gatewayIdentifier=self.gateway_id,
                name="TACNodeContextLakeGateway",
                description="AgentCore Gateway for TACNode Context Lake real-time data access",
                roleArn="arn:aws:iam::560155322832:role/AmazonBedrockAgentCoreGatewayServiceRole",
                protocolType="MCP",
                authorizerType="CUSTOM_JWT",
                authorizerConfiguration=cognito_authorizer_config
            )
            
            print(f"✅ Gateway updated to use Cognito:")
            print(f"   Gateway ID: {self.gateway_id}")
            print(f"   Authorizer: AWS Cognito")
            print(f"   Discovery URL: {cognito_authorizer_config['customJWTAuthorizer']['discoveryUrl']}")
            
            # Update gateway info file
            self.gateway_info['authorizerConfiguration'] = cognito_authorizer_config
            self.gateway_info['cognitoConfig'] = cognito_config
            self.gateway_info['updated'] = datetime.now().isoformat()
            
            with open('tacnode-agentcore-gateway.json', 'w') as f:
                json.dump(self.gateway_info, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"❌ Gateway update failed: {e}")
            return False
    
    def get_cognito_token(self, cognito_config, test_user):
        """Get Cognito JWT token for testing"""
        print("\n📋 STEP 4: Getting Cognito JWT Token")
        print("-" * 50)
        
        try:
            # Authenticate user and get tokens
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
            id_token = response['AuthenticationResult']['IdToken']
            
            print(f"✅ Cognito tokens obtained:")
            print(f"   Access Token: {access_token[:50]}...")
            print(f"   ID Token: {id_token[:50]}...")
            
            # Save tokens
            token_info = {
                "accessToken": access_token,
                "idToken": id_token,
                "userPoolId": cognito_config['userPoolId'],
                "clientId": cognito_config['clientId'],
                "obtained": datetime.now().isoformat()
            }
            
            with open('cognito-tokens.json', 'w') as f:
                json.dump(token_info, f, indent=2)
            
            print(f"\n🔑 GATEWAY_TOKEN for testing:")
            print(f"export GATEWAY_TOKEN='{access_token}'")
            
            return token_info
            
        except Exception as e:
            print(f"❌ Token generation failed: {e}")
            return None
    
    def show_final_aws_configuration(self, cognito_config, token_info):
        """Show final pure AWS configuration"""
        print("\n🎉 PURE AWS END-TO-END CONFIGURATION COMPLETE!")
        print("=" * 70)
        
        print("✅ AWS COMPONENTS:")
        print(f"   • AgentCore Gateway: {self.gateway_id}")
        print(f"   • Cognito User Pool: {cognito_config['userPoolId']}")
        print(f"   • Cognito Client: {cognito_config['clientId']}")
        print(f"   • Secrets Manager: TACNode API key")
        print(f"   • Region: us-east-1")
        
        print("\n🌐 EXTERNAL COMPONENTS:")
        print("   • TACNode: mcp-server.tacnode.io (ONLY external component)")
        
        print("\n🔑 AUTHENTICATION FLOW:")
        print("   User → Cognito JWT → AgentCore Gateway → TACNode → PostgreSQL")
        
        print("\n🧪 TESTING:")
        print(f"   export GATEWAY_TOKEN='{token_info['accessToken']}'")
        print("   python3 test_tacnode_rest_api_direct.py")
        
        print("\n📋 FILES CREATED:")
        print("   • cognito-gateway-config.json - Cognito configuration")
        print("   • cognito-tokens.json - JWT tokens")
        print("   • tacnode-agentcore-gateway.json - Updated gateway config")
        
        print("\n🎯 RESULT:")
        print("   ✅ Pure AWS solution (except TACNode)")
        print("   ✅ No Google OAuth")
        print("   ✅ AWS Cognito authentication")
        print("   ✅ Ready for testing")
    
    async def reconfigure_to_pure_aws(self):
        """Complete reconfiguration to pure AWS solution"""
        print("🔧 RECONFIGURING TO PURE AWS SOLUTION")
        print("=" * 70)
        print("🎯 Goal: AWS end-to-end (TACNode is only external component)")
        
        # Step 1: Create Cognito User Pool
        cognito_config = self.create_cognito_user_pool()
        if not cognito_config:
            print("❌ Cognito setup failed")
            return False
        
        # Step 2: Create test user
        test_user = self.create_test_user(cognito_config)
        if not test_user:
            print("❌ Test user creation failed")
            return False
        
        # Step 3: Update gateway to use Cognito
        gateway_updated = self.update_gateway_to_cognito(cognito_config)
        if not gateway_updated:
            print("❌ Gateway update failed")
            return False
        
        # Step 4: Get Cognito tokens
        token_info = self.get_cognito_token(cognito_config, test_user)
        if not token_info:
            print("❌ Token generation failed")
            return False
        
        # Step 5: Show final configuration
        self.show_final_aws_configuration(cognito_config, token_info)
        
        return True

async def main():
    print("🔧 AWS Cognito Gateway Reconfiguration")
    print("=" * 60)
    
    try:
        reconfigurator = AWSCognitoGatewayReconfiguration()
        success = await reconfigurator.reconfigure_to_pure_aws()
        
        if success:
            print("\n✅ RECONFIGURATION COMPLETE!")
            print("   Pure AWS solution ready")
        else:
            print("\n❌ RECONFIGURATION FAILED!")
            print("   Check configuration and retry")
            
    except Exception as e:
        print(f"❌ Reconfiguration error: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

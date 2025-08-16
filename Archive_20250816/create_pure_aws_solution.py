#!/usr/bin/env python3
"""
Create Pure AWS AgentCore Gateway Solution
Based on official AWS documentation and samples
"""

import boto3
import json
import time
from datetime import datetime

class PureAWSAgentCoreGateway:
    """Create pure AWS AgentCore Gateway following official AWS patterns"""
    
    def __init__(self):
        self.cognito_client = boto3.client('cognito-idp', region_name='us-east-1')
        self.bedrock_agentcore = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
        
        print("🔧 PURE AWS AGENTCORE GATEWAY SOLUTION")
        print("=" * 60)
        print("📋 Following official AWS documentation patterns")
        print("🌐 External: Only TACNode (as intended)")
    
    def create_cognito_user_pool_machine_to_machine(self):
        """Create Cognito User Pool for machine-to-machine auth (AWS official pattern)"""
        print("\n📋 STEP 1: Creating Cognito User Pool (Machine-to-Machine)")
        print("-" * 60)
        print("Following AWS documentation pattern for machine-to-machine auth")
        
        try:
            # Step 1: Create user pool (AWS official pattern)
            pool_response = self.cognito_client.create_user_pool(
                PoolName="gateway-user-pool",
                Policies={
                    'PasswordPolicy': {
                        'MinimumLength': 8
                    }
                }
            )
            
            user_pool_id = pool_response['UserPool']['Id']
            print(f"✅ User Pool created: {user_pool_id}")
            
            # Step 2: Create resource server (AWS official pattern)
            resource_response = self.cognito_client.create_resource_server(
                UserPoolId=user_pool_id,
                Identifier="gateway-resource-server",
                Name="GatewayResourceServer",
                Scopes=[
                    {"ScopeName": "read", "ScopeDescription": "Read access"},
                    {"ScopeName": "write", "ScopeDescription": "Write access"}
                ]
            )
            print(f"✅ Resource Server created: gateway-resource-server")
            
            # Step 3: Create client for user pool (AWS official pattern)
            client_response = self.cognito_client.create_user_pool_client(
                UserPoolId=user_pool_id,
                ClientName="gateway-client",
                GenerateSecret=True,  # Required for client_credentials flow
                AllowedOAuthFlows=["client_credentials"],
                AllowedOAuthScopes=[
                    "gateway-resource-server/read",
                    "gateway-resource-server/write"
                ],
                AllowedOAuthFlowsUserPoolClient=True,
                SupportedIdentityProviders=["COGNITO"]
            )
            
            client_id = client_response['UserPoolClient']['ClientId']
            client_secret = client_response['UserPoolClient']['ClientSecret']
            print(f"✅ Client created: {client_id}")
            
            # Step 4: Create domain (AWS official pattern)
            # Create valid domain name (lowercase, no underscores)
            domain_name = user_pool_id.lower().replace('_', '-')
            try:
                self.cognito_client.create_user_pool_domain(
                    Domain=domain_name,
                    UserPoolId=user_pool_id
                )
                print(f"✅ Domain created: {domain_name}")
            except Exception as e:
                if "already exists" in str(e):
                    print(f"✅ Domain already exists: {domain_name}")
                else:
                    raise e
            
            # Step 5: Construct discovery URL (AWS official pattern)
            discovery_url = f"https://cognito-idp.us-east-1.amazonaws.com/{user_pool_id}/.well-known/openid-configuration"
            
            cognito_config = {
                "userPoolId": user_pool_id,
                "clientId": client_id,
                "clientSecret": client_secret,
                "domain": domain_name,
                "discoveryUrl": discovery_url,
                "tokenEndpoint": f"https://{domain_name}.auth.us-east-1.amazoncognito.com/oauth2/token"
            }
            
            print(f"✅ Discovery URL: {discovery_url}")
            
            return cognito_config
            
        except Exception as e:
            print(f"❌ Cognito setup failed: {e}")
            return None
    
    def get_bearer_token(self, cognito_config):
        """Get bearer token using client credentials flow (AWS official pattern)"""
        print("\n📋 STEP 2: Getting Bearer Token (Client Credentials)")
        print("-" * 60)

        import requests
        import base64

        # Wait for domain to be ready
        print("⏳ Waiting for Cognito domain to be ready...")
        time.sleep(30)  # Cognito domains need time to propagate

        try:
            # Prepare client credentials (AWS official pattern)
            client_id = cognito_config['clientId']
            client_secret = cognito_config['clientSecret']
            token_endpoint = cognito_config['tokenEndpoint']

            # Create basic auth header
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

            print(f"Token endpoint: {token_endpoint}")

            # Retry logic for domain propagation
            for attempt in range(3):
                try:
                    response = requests.post(token_endpoint, headers=headers, data=data, timeout=10)

                    if response.status_code == 200:
                        token_data = response.json()
                        access_token = token_data['access_token']

                        print(f"✅ Bearer token obtained")
                        print(f"   Token: {access_token[:50]}...")
                        print(f"   Token type: {token_data.get('token_type', 'Bearer')}")
                        print(f"   Expires in: {token_data.get('expires_in', 'Unknown')} seconds")

                        return access_token
                    else:
                        print(f"❌ Token request failed: {response.status_code}")
                        print(f"   Response: {response.text}")
                        return None

                except requests.exceptions.RequestException as e:
                    print(f"   Attempt {attempt + 1}/3 failed: {e}")
                    if attempt < 2:
                        print("   Retrying in 30 seconds...")
                        time.sleep(30)
                    else:
                        print("   All attempts failed - domain may need more time")
                        return None

        except Exception as e:
            print(f"❌ Token generation failed: {e}")
            return None
    
    def delete_old_gateway_safely(self):
        """Delete old gateway and its targets safely"""
        print("\n📋 STEP 3: Cleaning Up Old Gateway")
        print("-" * 60)
        
        old_gateway_id = "tacnodecontextlakegateway-bkq6ozcvxp"
        
        try:
            # List and delete targets first
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
            
            # Delete gateway
            print(f"   Deleting gateway: {old_gateway_id}")
            self.bedrock_agentcore.delete_gateway(
                gatewayIdentifier=old_gateway_id
            )
            
            print(f"✅ Old gateway cleaned up")
            return True
            
        except Exception as e:
            print(f"⚠️  Old gateway cleanup: {e}")
            return False
    
    def create_pure_aws_gateway(self, cognito_config):
        """Create gateway with pure AWS Cognito auth (AWS official pattern)"""
        print("\n📋 STEP 4: Creating Pure AWS Gateway")
        print("-" * 60)
        
        try:
            # Gateway authorizer configuration (AWS official pattern)
            authorizer_config = {
                "customJWTAuthorizer": {
                    "discoveryUrl": cognito_config['discoveryUrl'],
                    "allowedClients": [cognito_config['clientId']]
                }
            }
            
            print(f"Authorizer config:")
            print(json.dumps(authorizer_config, indent=2))
            
            # Create gateway (AWS official pattern)
            response = self.bedrock_agentcore.create_gateway(
                name="PureAWSTACNodeGateway",
                description="Pure AWS AgentCore Gateway for TACNode with Cognito authentication",
                roleArn="arn:aws:iam::560155322832:role/AmazonBedrockAgentCoreGatewayServiceRole",
                protocolType="MCP",
                protocolConfiguration={
                    "mcp": {
                        "supportedVersions": ["2025-03-26"],
                        "instructions": "Pure AWS Gateway for TACNode Context Lake with Cognito machine-to-machine authentication",
                        "searchType": "SEMANTIC"
                    }
                },
                authorizerType="CUSTOM_JWT",
                authorizerConfiguration=authorizer_config
            )
            
            gateway_id = response['gatewayId']
            gateway_url = response['gatewayUrl']
            
            print(f"✅ Pure AWS Gateway created:")
            print(f"   Gateway ID: {gateway_id}")
            print(f"   Gateway URL: {gateway_url}")
            print(f"   Authentication: AWS Cognito (machine-to-machine)")
            
            gateway_config = {
                "gatewayId": gateway_id,
                "gatewayUrl": gateway_url,
                "name": "PureAWSTACNodeGateway",
                "authorizerType": "CUSTOM_JWT",
                "cognitoConfig": cognito_config,
                "created": datetime.now().isoformat()
            }
            
            with open('pure-aws-gateway-final.json', 'w') as f:
                json.dump(gateway_config, f, indent=2)
            
            return gateway_config
            
        except Exception as e:
            print(f"❌ Gateway creation failed: {e}")
            return None
    
    def create_tacnode_target(self, gateway_config):
        """Create TACNode target with credential provider"""
        print("\n📋 STEP 5: Creating TACNode Target")
        print("-" * 60)
        
        gateway_id = gateway_config['gatewayId']
        
        try:
            # Load TACNode OpenAPI spec
            with open('tacnode_openapi_spec.json', 'r') as f:
                openapi_spec = json.load(f)
            
            # Create API key credential provider
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
            
            with open('pure-aws-gateway-final.json', 'w') as f:
                json.dump(gateway_config, f, indent=2)
            
            return target_id
            
        except Exception as e:
            print(f"❌ Target creation failed: {e}")
            return None
    
    async def create_complete_solution(self):
        """Create complete pure AWS solution"""
        print("🔧 CREATING COMPLETE PURE AWS SOLUTION")
        print("=" * 70)
        print("📋 Following AWS official documentation patterns")
        
        # Step 1: Create Cognito (machine-to-machine pattern)
        cognito_config = self.create_cognito_user_pool_machine_to_machine()
        if not cognito_config:
            return False
        
        # Step 2: Get bearer token
        bearer_token = self.get_bearer_token(cognito_config)
        if not bearer_token:
            return False
        
        # Step 3: Clean up old gateway
        self.delete_old_gateway_safely()
        
        # Step 4: Create new gateway
        gateway_config = self.create_pure_aws_gateway(cognito_config)
        if not gateway_config:
            return False
        
        # Step 5: Create TACNode target
        target_id = self.create_tacnode_target(gateway_config)
        if not target_id:
            return False
        
        # Show final results
        print("\n🎉 PURE AWS SOLUTION COMPLETE!")
        print("=" * 70)
        print("✅ AWS COMPONENTS:")
        print(f"   • AgentCore Gateway: {gateway_config['gatewayId']}")
        print(f"   • Cognito User Pool: {cognito_config['userPoolId']}")
        print(f"   • Cognito Client: {cognito_config['clientId']}")
        print(f"   • Target: {target_id}")
        print(f"   • Secrets Manager: TACNode API key")
        
        print("\n🌐 EXTERNAL COMPONENTS:")
        print("   • TACNode: mcp-server.tacnode.io (ONLY external component)")
        
        print("\n🔑 AUTHENTICATION:")
        print("   • 100% AWS Cognito (machine-to-machine)")
        print("   • Client credentials flow")
        print("   • No Google OAuth")
        print("   • Pure AWS end-to-end")
        
        print(f"\n🧪 TEST COMMAND:")
        print(f"export GATEWAY_TOKEN='{bearer_token}'")
        print("python3 test_tacnode_rest_api_direct.py")
        
        # Save token for testing
        with open('aws-bearer-token.txt', 'w') as f:
            f.write(bearer_token)
        
        print(f"\n📋 FILES CREATED:")
        print("   • pure-aws-gateway-final.json - Gateway configuration")
        print("   • aws-bearer-token.txt - Bearer token for testing")
        
        return True

async def main():
    print("🔧 Pure AWS AgentCore Gateway Creator")
    print("=" * 60)
    print("📋 Based on official AWS documentation")
    
    try:
        creator = PureAWSAgentCoreGateway()
        success = await creator.create_complete_solution()
        
        if success:
            print("\n✅ PURE AWS SOLUTION READY!")
            print("🎯 100% AWS (except TACNode as intended)")
        else:
            print("\n❌ CREATION FAILED!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

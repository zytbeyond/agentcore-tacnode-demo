#!/usr/bin/env python3
"""
Create Pure AWS AgentCore Gateway Solution - Final Version
Based on official AWS documentation - creates gateway and provides token instructions
"""

import boto3
import json
from datetime import datetime

class PureAWSAgentCoreFinal:
    """Create pure AWS AgentCore Gateway following official AWS patterns"""
    
    def __init__(self):
        self.cognito_client = boto3.client('cognito-idp', region_name='us-east-1')
        self.bedrock_agentcore = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
        
        print("🔧 PURE AWS AGENTCORE GATEWAY - FINAL SOLUTION")
        print("=" * 60)
        print("📋 Following official AWS documentation")
        print("🌐 External: Only TACNode")
    
    def create_cognito_machine_to_machine(self):
        """Create Cognito for machine-to-machine auth (AWS official pattern)"""
        print("\n📋 STEP 1: Creating AWS Cognito (Machine-to-Machine)")
        print("-" * 60)
        
        try:
            # Create user pool
            pool_response = self.cognito_client.create_user_pool(
                PoolName="gateway-user-pool",
                Policies={'PasswordPolicy': {'MinimumLength': 8}}
            )
            user_pool_id = pool_response['UserPool']['Id']
            print(f"✅ User Pool: {user_pool_id}")
            
            # Create resource server
            self.cognito_client.create_resource_server(
                UserPoolId=user_pool_id,
                Identifier="gateway-resource-server",
                Name="GatewayResourceServer",
                Scopes=[
                    {"ScopeName": "read", "ScopeDescription": "Read access"},
                    {"ScopeName": "write", "ScopeDescription": "Write access"}
                ]
            )
            print(f"✅ Resource Server: gateway-resource-server")
            
            # Create client
            client_response = self.cognito_client.create_user_pool_client(
                UserPoolId=user_pool_id,
                ClientName="gateway-client",
                GenerateSecret=True,
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
            print(f"✅ Client: {client_id}")
            
            # Create domain
            domain_name = user_pool_id.lower().replace('_', '-')
            try:
                self.cognito_client.create_user_pool_domain(
                    Domain=domain_name,
                    UserPoolId=user_pool_id
                )
                print(f"✅ Domain: {domain_name}")
            except Exception as e:
                if "already exists" in str(e):
                    print(f"✅ Domain exists: {domain_name}")
                else:
                    raise e
            
            # Discovery URL
            discovery_url = f"https://cognito-idp.us-east-1.amazonaws.com/{user_pool_id}/.well-known/openid-configuration"
            
            return {
                "userPoolId": user_pool_id,
                "clientId": client_id,
                "clientSecret": client_secret,
                "domain": domain_name,
                "discoveryUrl": discovery_url,
                "tokenEndpoint": f"https://{domain_name}.auth.us-east-1.amazoncognito.com/oauth2/token"
            }
            
        except Exception as e:
            print(f"❌ Cognito setup failed: {e}")
            return None
    
    def create_pure_aws_gateway(self, cognito_config):
        """Create gateway with pure AWS Cognito auth"""
        print("\n📋 STEP 2: Creating Pure AWS Gateway")
        print("-" * 60)
        
        try:
            # Delete old gateway first
            try:
                old_gateway_id = "tacnodecontextlakegateway-bkq6ozcvxp"
                targets = self.bedrock_agentcore.list_gateway_targets(gatewayIdentifier=old_gateway_id)
                for target in targets.get('gatewayTargets', []):
                    self.bedrock_agentcore.delete_gateway_target(
                        gatewayIdentifier=old_gateway_id,
                        targetId=target['targetId']
                    )
                self.bedrock_agentcore.delete_gateway(gatewayIdentifier=old_gateway_id)
                print(f"✅ Old gateway cleaned up")
            except:
                print(f"⚠️  Old gateway cleanup skipped")
            
            # Create new gateway
            authorizer_config = {
                "customJWTAuthorizer": {
                    "discoveryUrl": cognito_config['discoveryUrl'],
                    "allowedClients": [cognito_config['clientId']]
                }
            }
            
            response = self.bedrock_agentcore.create_gateway(
                name="PureAWSTACNodeGateway",
                description="Pure AWS AgentCore Gateway for TACNode with Cognito authentication",
                roleArn="arn:aws:iam::560155322832:role/AmazonBedrockAgentCoreGatewayServiceRole",
                protocolType="MCP",
                protocolConfiguration={
                    "mcp": {
                        "supportedVersions": ["2025-03-26"],
                        "instructions": "Pure AWS Gateway for TACNode Context Lake",
                        "searchType": "SEMANTIC"
                    }
                },
                authorizerType="CUSTOM_JWT",
                authorizerConfiguration=authorizer_config
            )
            
            gateway_id = response['gatewayId']
            gateway_url = response['gatewayUrl']
            
            print(f"✅ Gateway created: {gateway_id}")
            print(f"✅ Gateway URL: {gateway_url}")
            
            return {
                "gatewayId": gateway_id,
                "gatewayUrl": gateway_url,
                "cognitoConfig": cognito_config
            }
            
        except Exception as e:
            print(f"❌ Gateway creation failed: {e}")
            return None
    
    def create_tacnode_target(self, gateway_config):
        """Create TACNode target"""
        print("\n📋 STEP 3: Creating TACNode Target")
        print("-" * 60)
        
        try:
            # Load OpenAPI spec
            with open('tacnode-agentcore-openapi-spec.json', 'r') as f:
                openapi_spec = json.load(f)
            
            # Create credential provider
            cred_response = self.bedrock_agentcore.create_api_key_credential_provider(
                name="TACNodeAPIKeyProvider",
                description="API Key provider for TACNode authentication",
                secretArn="arn:aws:secretsmanager:us-east-1:560155322832:secret:tacnode-api-key-final-8Lw7Ej"
            )
            cred_provider_id = cred_response['credentialProviderId']
            print(f"✅ Credential provider: {cred_provider_id}")
            
            # Create target
            target_response = self.bedrock_agentcore.create_gateway_target(
                gatewayIdentifier=gateway_config['gatewayId'],
                name="pure-aws-tacnode-target",
                description="TACNode Context Lake target with pure AWS authentication",
                targetType="OPENAPI",
                openAPIConfiguration={
                    "openAPISpecification": json.dumps(openapi_spec),
                    "credentialProviderId": cred_provider_id
                }
            )
            
            target_id = target_response['targetId']
            print(f"✅ Target created: {target_id}")
            
            return target_id
            
        except Exception as e:
            print(f"❌ Target creation failed: {e}")
            return None
    
    def show_token_instructions(self, cognito_config):
        """Show instructions for getting bearer token"""
        print("\n📋 STEP 4: Getting Bearer Token")
        print("-" * 60)
        print("⏳ Cognito domain needs 5-10 minutes to be ready")
        print("📋 Use this curl command to get bearer token:")
        
        client_id = cognito_config['clientId']
        client_secret = cognito_config['clientSecret']
        token_endpoint = cognito_config['tokenEndpoint']
        
        curl_command = f"""curl -X POST {token_endpoint} \\
  -H "Content-Type: application/x-www-form-urlencoded" \\
  -H "Authorization: Basic $(echo -n '{client_id}:{client_secret}' | base64)" \\
  -d "grant_type=client_credentials&scope=gateway-resource-server/read gateway-resource-server/write"
"""
        
        print(f"\n{curl_command}")
        
        print(f"\n📋 Alternative - Python script:")
        python_script = f"""
import requests
import base64

client_id = "{client_id}"
client_secret = "{client_secret}"
token_endpoint = "{token_endpoint}"

credentials = f"{{client_id}}:{{client_secret}}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()

headers = {{
    "Content-Type": "application/x-www-form-urlencoded",
    "Authorization": f"Basic {{encoded_credentials}}"
}}

data = {{
    "grant_type": "client_credentials",
    "scope": "gateway-resource-server/read gateway-resource-server/write"
}}

response = requests.post(token_endpoint, headers=headers, data=data)
if response.status_code == 200:
    token_data = response.json()
    print(f"Bearer token: {{token_data['access_token']}}")
else:
    print(f"Error: {{response.status_code}} - {{response.text}}")
"""
        
        print(python_script)
        
        return True
    
    def create_complete_solution(self):
        """Create complete pure AWS solution"""
        print("🔧 CREATING COMPLETE PURE AWS SOLUTION")
        print("=" * 70)
        
        # Step 1: Create Cognito
        cognito_config = self.create_cognito_machine_to_machine()
        if not cognito_config:
            return False
        
        # Step 2: Create gateway
        gateway_config = self.create_pure_aws_gateway(cognito_config)
        if not gateway_config:
            return False
        
        # Step 3: Create target
        target_id = self.create_tacnode_target(gateway_config)
        if not target_id:
            return False
        
        # Step 4: Show token instructions
        self.show_token_instructions(cognito_config)
        
        # Save configuration
        final_config = {
            "gatewayId": gateway_config['gatewayId'],
            "gatewayUrl": gateway_config['gatewayUrl'],
            "targetId": target_id,
            "cognitoConfig": cognito_config,
            "created": datetime.now().isoformat()
        }
        
        with open('pure-aws-gateway-complete.json', 'w') as f:
            json.dump(final_config, f, indent=2)
        
        print("\n🎉 PURE AWS SOLUTION COMPLETE!")
        print("=" * 70)
        print("✅ COMPONENTS CREATED:")
        print(f"   • AgentCore Gateway: {gateway_config['gatewayId']}")
        print(f"   • Cognito User Pool: {cognito_config['userPoolId']}")
        print(f"   • Cognito Client: {cognito_config['clientId']}")
        print(f"   • TACNode Target: {target_id}")
        print(f"   • Credential Provider: TACNode API key")
        
        print("\n🌐 ARCHITECTURE:")
        print("   User → MCP → AgentCore Gateway → TACNode → PostgreSQL")
        print("   ✅ 100% AWS (except TACNode as intended)")
        print("   ✅ AWS Cognito authentication")
        print("   ✅ Machine-to-machine flow")
        
        print("\n📋 NEXT STEPS:")
        print("1. Wait 5-10 minutes for Cognito domain to be ready")
        print("2. Use curl command above to get bearer token")
        print("3. Test: export GATEWAY_TOKEN='<token>' && python3 test_tacnode_rest_api_direct.py")
        
        print(f"\n📁 FILES CREATED:")
        print("   • pure-aws-gateway-complete.json - Complete configuration")
        
        return True

def main():
    print("🔧 Pure AWS AgentCore Gateway - Final Solution")
    print("=" * 60)
    
    try:
        creator = PureAWSAgentCoreFinal()
        success = creator.create_complete_solution()
        
        if success:
            print("\n✅ SUCCESS! Pure AWS solution created")
        else:
            print("\n❌ FAILED! Check errors above")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()

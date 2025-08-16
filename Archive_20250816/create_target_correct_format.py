#!/usr/bin/env python3
"""
Create TACNode target with correct API format for pure AWS gateway
"""

import boto3
import json

def create_tacnode_target_correct():
    """Create TACNode target using correct API format"""
    print("🔧 CREATING TACNODE TARGET - CORRECT FORMAT")
    print("=" * 60)
    
    bedrock_agentcore = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
    
    # Gateway ID from pure AWS gateway
    gateway_id = "pureawstacnodegateway-l0f1tg5t8o"
    
    try:
        # Load OpenAPI spec
        with open('tacnode-agentcore-openapi-spec.json', 'r') as f:
            openapi_spec = json.load(f)
        
        print(f"✅ OpenAPI spec loaded")
        
        # Target configuration using MCP with OpenAPI schema
        target_configuration = {
            "mcp": {
                "openApiSchema": {
                    "inlinePayload": json.dumps(openapi_spec)
                }
            }
        }
        
        # Credential provider configuration
        credential_provider_configurations = [
            {
                "credentialProviderType": "API_KEY",
                "credentialProvider": {
                    "apiKeyCredentialProvider": {
                        "providerArn": "arn:aws:bedrock-agentcore:us-east-1:560155322832:token-vault/default/apikeycredentialprovider/TACNodeAPIKeyProvider",
                        "credentialParameterName": "Authorization",
                        "credentialPrefix": "Bearer ",
                        "credentialLocation": "HEADER"
                    }
                }
            }
        ]
        
        print(f"Target configuration:")
        print(json.dumps(target_configuration, indent=2))
        print(f"\nCredential configuration:")
        print(json.dumps(credential_provider_configurations, indent=2))
        
        # Create target with correct format
        target_response = bedrock_agentcore.create_gateway_target(
            gatewayIdentifier=gateway_id,
            name="pure-aws-tacnode-target",
            description="TACNode Context Lake target with pure AWS authentication",
            targetConfiguration=target_configuration,
            credentialProviderConfigurations=credential_provider_configurations
        )
        
        target_id = target_response['targetId']
        print(f"\n✅ Target created successfully: {target_id}")
        
        # Save target info
        target_info = {
            "targetId": target_id,
            "gatewayId": gateway_id,
            "name": "pure-aws-tacnode-target",
            "targetConfiguration": target_configuration,
            "credentialProviderConfigurations": credential_provider_configurations,
            "created": target_response.get('createdAt', 'unknown')
        }
        
        with open('pure-aws-target-info.json', 'w') as f:
            json.dump(target_info, f, indent=2)
        
        print(f"\n🎉 PURE AWS TARGET CREATION COMPLETE!")
        print(f"   Gateway: {gateway_id}")
        print(f"   Target: {target_id}")
        print(f"   Configuration: pure-aws-target-info.json")
        
        return True
        
    except Exception as e:
        print(f"❌ Target creation failed: {e}")
        return False

if __name__ == "__main__":
    create_tacnode_target_correct()

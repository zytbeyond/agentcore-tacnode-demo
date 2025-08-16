#!/usr/bin/env python3
"""
Create corrected TACNode target with fixed OpenAPI spec
"""

import boto3
import json
import time

def create_corrected_target():
    """Create TACNode target with corrected OpenAPI spec"""
    print("🔧 CREATING CORRECTED TACNODE TARGET")
    print("=" * 60)
    
    bedrock_agentcore = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
    
    gateway_id = "pureawstacnodegateway-l0f1tg5t8o"
    
    # Wait for old target to be deleted
    print("⏳ Waiting for old target deletion...")
    time.sleep(10)
    
    try:
        # Load corrected OpenAPI spec
        with open('tacnode-corrected-openapi-spec.json', 'r') as f:
            openapi_spec = json.load(f)
        
        print(f"✅ Corrected OpenAPI spec loaded")
        
        # Target configuration using corrected OpenAPI schema
        target_configuration = {
            "mcp": {
                "openApiSchema": {
                    "inlinePayload": json.dumps(openapi_spec)
                }
            }
        }
        
        # Credential provider configuration (same as before)
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
        
        print(f"Creating target with corrected configuration...")
        
        # Create target with corrected format
        target_response = bedrock_agentcore.create_gateway_target(
            gatewayIdentifier=gateway_id,
            name="corrected-tacnode-target",
            description="TACNode target with corrected OpenAPI spec for proper JSON-RPC handling",
            targetConfiguration=target_configuration,
            credentialProviderConfigurations=credential_provider_configurations
        )
        
        target_id = target_response['targetId']
        print(f"✅ Corrected target created: {target_id}")
        
        # Save target info
        target_info = {
            "targetId": target_id,
            "gatewayId": gateway_id,
            "name": "corrected-tacnode-target",
            "targetConfiguration": target_configuration,
            "credentialProviderConfigurations": credential_provider_configurations,
            "created": target_response.get('createdAt', 'unknown')
        }
        
        with open('corrected-target-info.json', 'w') as f:
            json.dump(target_info, f, indent=2)
        
        print(f"\n🎉 CORRECTED TARGET CREATION COMPLETE!")
        print(f"   Gateway: {gateway_id}")
        print(f"   Target: {target_id}")
        print(f"   Configuration: corrected-target-info.json")
        
        return target_id
        
    except Exception as e:
        print(f"❌ Target creation failed: {e}")
        return None

if __name__ == "__main__":
    create_corrected_target()

#!/usr/bin/env python3
"""
Create TACNode target for the existing pure AWS gateway
"""

import boto3
import json

def create_tacnode_target():
    """Create TACNode target for existing gateway"""
    print("🔧 CREATING TACNODE TARGET FOR PURE AWS GATEWAY")
    print("=" * 60)
    
    bedrock_agentcore = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
    
    # Gateway ID from previous creation
    gateway_id = "pureawstacnodegateway-l0f1tg5t8o"
    
    try:
        # Load OpenAPI spec
        with open('tacnode-agentcore-openapi-spec.json', 'r') as f:
            openapi_spec = json.load(f)
        
        print(f"✅ OpenAPI spec loaded")
        
        # Use existing credential provider
        cred_provider_arn = "arn:aws:bedrock-agentcore:us-east-1:560155322832:token-vault/default/apikeycredentialprovider/TACNodeAPIKeyProvider"
        cred_provider_id = "TACNodeAPIKeyProvider"
        print(f"✅ Credential provider: {cred_provider_id}")
        
        # Create target
        target_response = bedrock_agentcore.create_gateway_target(
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
        print(f"✅ Target created: {target_id}")
        
        print("\n🎉 TARGET CREATION COMPLETE!")
        print(f"   Gateway: {gateway_id}")
        print(f"   Target: {target_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Target creation failed: {e}")
        return False

if __name__ == "__main__":
    create_tacnode_target()

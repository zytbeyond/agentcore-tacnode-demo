#!/usr/bin/env python3
"""
Create credential provider using AgentCore Identity service
"""

import boto3
import json
import time

def create_identity_credential_provider():
    """Create credential provider using AgentCore Identity"""
    print("🔧 CREATING CREDENTIAL PROVIDER WITH AGENTCORE IDENTITY")
    print("=" * 60)
    
    # Working TACNode token
    working_token = "eyJhbGciOiJSUzI1NiJ9.eyJlbmNyeXB0ZWRDb25uZWN0aW9uIjoiMk51V2lPTzJzaGdmbnZvdVQvanJlWjFxNTlSekZ0QmlORmJtRytUMXlUblJXVkFseE9keGFWYXRsbHpONmJJNkt1VERCYU5XTzlZeUk2UDBKeGFVZFJ3dnE5YklQWUlZM2c4QUt0MlNmV3RQd1RPOW1FWmVVTkJlOVl6czZMQ1JIR2NTMmpZUFlDbUZXblRrMjZTeFQ1Y0FmbkNGVXd2SUxHaGo1QTBucVFPeDAxTEwyUUlabWtWck5aY2xMTVVUNkEvMU55YUEzcVZZZFdHdUtFRmFmUmxlZlZMY2ppbjltbkYrT1dsQldFR01yRTRwMUZHSEN2R2VOM2dOWTJhZUdLbWdlZUVXMTdoOUdXSG9jOXBaeTFQKzRCc1U1eWhTdjlvOG1nbDNCV242TVFaVXVNV3ZndzU1U3NJZFQvNUJqWGFYL1lZaEszK3EyN0pYVzF5aC83dUhXZnliS0R3dFVRK3pDYnVxTjZNTmptRG5PYjlQM21wakJaNGlzT0ZGbnd3OVFJdnhrRHpReTNJaVhUSFZiQUNGTE96c2ptblZMV2diT1RKRFBTSHNaczNFZTUzNmQ4TnFtZzk0Q0VNNFo2YmtYSkx6Wkp1RUpsTUlnSDhjNm85NDVjM3JhZ1JwWmtmK3U4eTBXL3d1QlRMRCtqZ0dUM1ZsQzlGZ2NhWHlwWTBqNzVCaURqYVcrMUVRdzlEVmZHV29BZS9Mc2JtTXNBaVBqMXJBVEVyMFlsOWdwb2RhRWNQd0xRcThoeVZxWmxGUDZXeUJzMEhaV0RybmdKbWNxdGVXenMrblJER1dGSURNNnZvcXdKQ0JoT09aQVRwTFlYK3ByZTNKVFFLeUpyRjB1VExPUENsdkFsTStOQW02WDJKd2lOdGNhZVVhZ1VNb2pXVWY5QnlCaFFCc0FVTjQwTzAvaGtXa3NpbHBGQUp3RkZvVEVIQXcrNXc3RTV0bGl4QjJVTDVkVi85Y08vVk9oRFNud2cyTVpNTUJBSWNtWFZtVEdHdjJxc2p2MTNxenJxVm5BTzIxcmNsbm9BbTZzRmg2Sk5mSjc2MEdENXZId2V6N1FuNjhWSVlQa0RkN2h0TzBIRkJEWmREangxaXFtL0V5QkFIU0dlTk01cVI0c0R2TC9OL0RSK21BS1hQcW4yc0syQlU4RXJWYUNyQXlwS2UyWlVZcXoySDRTcmsvZ1BuN3FnZlZiaTluK2R3ZU1BUjhYNVZzWlF1WlNqTThmRXUvK1dUa1l4eTVKajFpdGhvbDl3OWIrb0E0cjFvaHgwMXFnaGFZQnFQcnNYSmFsSWZITG44MVU1MkdibStBSEs5a1ZNcnBMbHFHek1sbWJCMzVuRkQ3K2kwaWtoVVBMellFV09YNzV6dVVyQkUvYkc4MHFBeVAzaHNwIiwiaXNzIjoibWNwLXRva2VuLXNlcnZpY2UiLCJhdWQiOiJtY3AtY2xpZW50cyIsImlhdCI6MTc1NDI5NzY3MCwiZXhwIjoxNzY5ODQ5NjcwfQ.cScHS445lUq-jCvZWyww6iuukw8cNpFgQYMGMshTQDPgj-6Q7H2jBBlCAeWyoFcazNAIdDUwJ-vdZWhLBv4QTOM5v5fyz_H1OS7iN_54NUR0DOU99Nleu0KorUZWYV6NzZEa8Pt1M5iH5v_lIrLIhGS-Ya_hsDs3UvIrbzv32eM"
    
    print(f"Working Token: {working_token[:50]}...")
    
    try:
        # Try using the AgentCore Identity service instead
        # First, let's try using the CLI approach as shown in the documentation
        print(f"\n🔄 Creating credential provider using AWS CLI approach...")
        
        # Delete old providers first
        bedrock_agentcore = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
        
        try:
            bedrock_agentcore.delete_api_key_credential_provider(name="TACNodeWorkingToken")
            print(f"✅ Deleted old credential provider")
            time.sleep(5)
        except Exception as e:
            print(f"⚠️ Could not delete old provider: {e}")
        
        # Create new credential provider with correct configuration
        print(f"🔄 Creating new credential provider...")
        
        response = bedrock_agentcore.create_api_key_credential_provider(
            name="TACNodeIdentityProvider",
            apiKey=working_token
        )
        
        provider_arn = response['credentialProviderArn']
        print(f"✅ Identity credential provider created!")
        print(f"   Name: TACNodeIdentityProvider")
        print(f"   ARN: {provider_arn}")
        
        return provider_arn
        
    except Exception as e:
        print(f"❌ Failed to create identity credential provider: {e}")
        return None

def create_target_with_identity_provider():
    """Create target with identity-based credential provider"""
    print(f"\n🎯 CREATING TARGET WITH IDENTITY PROVIDER")
    print("-" * 60)
    
    # Create identity credential provider
    provider_arn = create_identity_credential_provider()
    if not provider_arn:
        return None
    
    bedrock_agentcore = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
    gateway_id = "pureawstacnodegateway-l0f1tg5t8o"
    
    # Delete old target first
    try:
        print(f"\n🗑️ Deleting old target...")
        bedrock_agentcore.delete_gateway_target(
            gatewayIdentifier=gateway_id,
            targetId="WXIO6JIDHI"
        )
        print(f"✅ Old target deleted")
        time.sleep(15)  # Wait for deletion
    except Exception as e:
        print(f"⚠️ Could not delete old target: {e}")
    
    try:
        # Load corrected OpenAPI spec
        with open('tacnode-corrected-openapi-spec.json', 'r') as f:
            openapi_spec = json.load(f)
        
        # Target configuration
        target_configuration = {
            "mcp": {
                "openApiSchema": {
                    "inlinePayload": json.dumps(openapi_spec)
                }
            }
        }
        
        # Credential provider configuration following AWS documentation format
        credential_provider_configurations = [
            {
                "credentialProviderType": "API_KEY",
                "credentialProvider": {
                    "apiKeyCredentialProvider": {
                        "providerArn": provider_arn,
                        "credentialParameterName": "Authorization",
                        "credentialPrefix": "Bearer ",
                        "credentialLocation": "HEADER"
                    }
                }
            }
        ]
        
        print(f"🔄 Creating target with identity provider...")
        print(f"Provider ARN: {provider_arn}")
        
        # Create target with identity credential provider
        target_response = bedrock_agentcore.create_gateway_target(
            gatewayIdentifier=gateway_id,
            name="identity-tacnode-target",
            description="TACNode target using AgentCore Identity credential provider",
            targetConfiguration=target_configuration,
            credentialProviderConfigurations=credential_provider_configurations
        )
        
        target_id = target_response['targetId']
        print(f"✅ Identity target created: {target_id}")
        
        # Save configuration
        config = {
            "gatewayId": gateway_id,
            "targetId": target_id,
            "credentialProviderArn": provider_arn,
            "credentialProviderName": "TACNodeIdentityProvider",
            "credentialLocation": "HEADER",
            "credentialParameterName": "Authorization",
            "credentialPrefix": "Bearer ",
            "status": "READY"
        }
        
        with open('identity-integration-config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"\n🎉 IDENTITY INTEGRATION COMPLETE!")
        print(f"   Gateway: {gateway_id}")
        print(f"   Target: {target_id}")
        print(f"   Credential Provider: TACNodeIdentityProvider")
        print(f"   Configuration: identity-integration-config.json")
        
        return target_id
        
    except Exception as e:
        print(f"❌ Target creation failed: {e}")
        return None

def main():
    """Create identity-based credential provider and target"""
    print("🎯 AGENTCORE IDENTITY INTEGRATION SETUP")
    print("=" * 70)
    print("🔧 Using AgentCore Identity service for credential management")
    print("🔧 Following AWS documentation best practices")
    
    target_id = create_target_with_identity_provider()
    
    if target_id:
        print(f"\n✅ IDENTITY INTEGRATION SETUP COMPLETE!")
        print(f"✅ Using AgentCore Identity for credential management")
        print(f"✅ Proper credential extraction configuration")
        print(f"🧪 Ready for final end-to-end test")
    else:
        print(f"\n❌ IDENTITY INTEGRATION SETUP FAILED")

if __name__ == "__main__":
    main()

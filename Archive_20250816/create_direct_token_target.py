#!/usr/bin/env python3
"""
Create target with direct token configuration
"""

import boto3
import json
import time

def create_direct_token_target():
    """Create target with direct token in secrets manager"""
    print("🔧 CREATING TARGET WITH DIRECT TOKEN CONFIGURATION")
    print("=" * 60)
    
    # Working TACNode token
    working_token = "eyJhbGciOiJSUzI1NiJ9.eyJlbmNyeXB0ZWRDb25uZWN0aW9uIjoiMk51V2lPTzJzaGdmbnZvdVQvanJlWjFxNTlSekZ0QmlORmJtRytUMXlUblJXVkFseE9keGFWYXRsbHpONmJJNkt1VERCYU5XTzlZeUk2UDBKeGFVZFJ3dnE5YklQWUlZM2c4QUt0MlNmV3RQd1RPOW1FWmVVTkJlOVl6czZMQ1JIR2NTMmpZUFlDbUZXblRrMjZTeFQ1Y0FmbkNGVXd2SUxHaGo1QTBucVFPeDAxTEwyUUlabWtWck5aY2xMTVVUNkEvMU55YUEzcVZZZFdHdUtFRmFmUmxlZlZMY2ppbjltbkYrT1dsQldFR01yRTRwMUZHSEN2R2VOM2dOWTJhZUdLbWdlZUVXMTdoOUdXSG9jOXBaeTFQKzRCc1U1eWhTdjlvOG1nbDNCV242TVFaVXVNV3ZndzU1U3NJZFQvNUJqWGFYL1lZaEszK3EyN0pYVzF5aC83dUhXZnliS0R3dFVRK3pDYnVxTjZNTmptRG5PYjlQM21wakJaNGlzT0ZGbnd3OVFJdnhrRHpReTNJaVhUSFZiQUNGTE96c2ptblZMV2diT1RKRFBTSHNaczNFZTUzNmQ4TnFtZzk0Q0VNNFo2YmtYSkx6Wkp1RUpsTUlnSDhjNm85NDVjM3JhZ1JwWmtmK3U4eTBXL3d1QlRMRCtqZ0dUM1ZsQzlGZ2NhWHlwWTBqNzVCaURqYVcrMUVRdzlEVmZHV29BZS9Mc2JtTXNBaVBqMXJBVEVyMFlsOWdwb2RhRWNQd0xRcThoeVZxWmxGUDZXeUJzMEhaV0RybmdKbWNxdGVXenMrblJER1dGSURNNnZvcXdKQ0JoT09aQVRwTFlYK3ByZTNKVFFLeUpyRjB1VExPUENsdkFsTStOQW02WDJKd2lOdGNhZVVhZ1VNb2pXVWY5QnlCaFFCc0FVTjQwTzAvaGtXa3NpbHBGQUp3RkZvVEVIQXcrNXc3RTV0bGl4QjJVTDVkVi85Y08vVk9oRFNud2cyTVpNTUJBSWNtWFZtVEdHdjJxc2p2MTNxenJxVm5BTzIxcmNsbm9BbTZzRmg2Sk5mSjc2MEdENXZId2V6N1FuNjhWSVlQa0RkN2h0TzBIRkJEWmREangxaXFtL0V5QkFIU0dlTk01cVI0c0R2TC9OL0RSK21BS1hQcW4yc0syQlU4RXJWYUNyQXlwS2UyWlVZcXoySDRTcmsvZ1BuN3FnZlZiaTluK2R3ZU1BUjhYNVZzWlF1WlNqTThmRXUvK1dUa1l4eTVKajFpdGhvbDl3OWIrb0E0cjFvaHgwMXFnaGFZQnFQcnNYSmFsSWZITG44MVU1MkdibStBSEs5a1ZNcnBMbHFHek1sbWJCMzVuRkQ3K2kwaWtoVVBMellFV09YNzV6dVVyQkUvYkc4MHFBeVAzaHNwIiwiaXNzIjoibWNwLXRva2VuLXNlcnZpY2UiLCJhdWQiOiJtY3AtY2xpZW50cyIsImlhdCI6MTc1NDI5NzY3MCwiZXhwIjoxNzY5ODQ5NjcwfQ.cScHS445lUq-jCvZWyww6iuukw8cNpFgQYMGMshTQDPgj-6Q7H2jBBlCAeWyoFcazNAIdDUwJ-vdZWhLBv4QTOM5v5fyz_H1OS7iN_54NUR0DOU99Nleu0KorUZWYV6NzZEa8Pt1M5iH5v_lIrLIhGS-Ya_hsDs3UvIrbzv32eM"
    
    bedrock_agentcore = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
    secrets_client = boto3.client('secretsmanager', region_name='us-east-1')
    
    print(f"Working Token: {working_token[:50]}...")
    
    try:
        # Create a secret directly in Secrets Manager with just the token
        secret_name = "tacnode-direct-token"
        
        print(f"\n🔄 Creating direct secret in Secrets Manager...")
        
        try:
            # Try to create the secret
            secret_response = secrets_client.create_secret(
                Name=secret_name,
                SecretString=working_token,
                Description="Direct TACNode token for AgentCore Gateway"
            )
            secret_arn = secret_response['ARN']
            print(f"✅ Secret created: {secret_arn}")
        except secrets_client.exceptions.ResourceExistsException:
            # Secret already exists, update it
            secret_response = secrets_client.update_secret(
                SecretId=secret_name,
                SecretString=working_token
            )
            secret_arn = secret_response['ARN']
            print(f"✅ Secret updated: {secret_arn}")
        
        # Delete old target first
        gateway_id = "pureawstacnodegateway-l0f1tg5t8o"
        
        try:
            print(f"\n🗑️ Deleting old target...")
            bedrock_agentcore.delete_gateway_target(
                gatewayIdentifier=gateway_id,
                targetId="UFA2BSOBV1"
            )
            print(f"✅ Old target deleted")
            time.sleep(15)  # Wait for deletion
        except Exception as e:
            print(f"⚠️ Could not delete old target: {e}")
        
        # Create new credential provider with direct secret
        print(f"\n🔄 Creating credential provider with direct secret...")
        
        # Delete old provider first
        try:
            bedrock_agentcore.delete_api_key_credential_provider(name="TACNodeIdentityProvider")
            print(f"✅ Deleted old provider")
            time.sleep(5)
        except Exception as e:
            print(f"⚠️ Could not delete old provider: {e}")
        
        # Create new provider
        provider_response = bedrock_agentcore.create_api_key_credential_provider(
            name="TACNodeDirectProvider",
            apiKey=working_token
        )
        
        provider_arn = provider_response['credentialProviderArn']
        print(f"✅ Direct credential provider created: {provider_arn}")
        
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
        
        # Credential provider configuration - try without prefix
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
        
        print(f"\n🔄 Creating target with direct credential provider...")
        
        # Create target
        target_response = bedrock_agentcore.create_gateway_target(
            gatewayIdentifier=gateway_id,
            name="direct-tacnode-target",
            description="TACNode target with direct token credential provider",
            targetConfiguration=target_configuration,
            credentialProviderConfigurations=credential_provider_configurations
        )
        
        target_id = target_response['targetId']
        print(f"✅ Direct target created: {target_id}")
        
        # Save configuration
        config = {
            "gatewayId": gateway_id,
            "targetId": target_id,
            "credentialProviderArn": provider_arn,
            "credentialProviderName": "TACNodeDirectProvider",
            "secretArn": secret_arn,
            "credentialLocation": "HEADER",
            "credentialParameterName": "Authorization",
            "credentialPrefix": "Bearer ",
            "status": "READY"
        }
        
        with open('direct-integration-config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"\n🎉 DIRECT INTEGRATION COMPLETE!")
        print(f"   Gateway: {gateway_id}")
        print(f"   Target: {target_id}")
        print(f"   Credential Provider: TACNodeDirectProvider")
        print(f"   Secret: {secret_arn}")
        print(f"   Configuration: direct-integration-config.json")
        
        return target_id
        
    except Exception as e:
        print(f"❌ Direct target creation failed: {e}")
        return None

def main():
    """Create direct token target"""
    print("🎯 DIRECT TOKEN INTEGRATION SETUP")
    print("=" * 70)
    print("🔧 Using direct token in Secrets Manager")
    print("🔧 Bypassing JSON wrapper issues")
    
    target_id = create_direct_token_target()
    
    if target_id:
        print(f"\n✅ DIRECT INTEGRATION SETUP COMPLETE!")
        print(f"✅ Direct token stored in Secrets Manager")
        print(f"✅ Credential provider configured for direct access")
        print(f"🧪 Ready for final test")
    else:
        print(f"\n❌ DIRECT INTEGRATION SETUP FAILED")

if __name__ == "__main__":
    main()

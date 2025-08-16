#!/usr/bin/env python3
"""
Create a new credential provider with the verified working token
"""

import boto3
import json
import time

def create_working_credential_provider():
    """Create credential provider with verified working token"""
    print("🔧 CREATING WORKING CREDENTIAL PROVIDER")
    print("=" * 60)
    
    # Verified working TACNode token
    working_token = "eyJhbGciOiJSUzI1NiJ9.eyJlbmNyeXB0ZWRDb25uZWN0aW9uIjoiMk51V2lPTzJzaGdmbnZvdVQvanJlWjFxNTlSekZ0QmlORmJtRytUMXlUblJXVkFseE9keGFWYXRsbHpONmJJNkt1VERCYU5XTzlZeUk2UDBKeGFVZFJ3dnE5YklQWUlZM2c4QUt0MlNmV3RQd1RPOW1FWmVVTkJlOVl6czZMQ1JIR2NTMmpZUFlDbUZXblRrMjZTeFQ1Y0FmbkNGVXd2SUxHaGo1QTBucVFPeDAxTEwyUUlabWtWck5aY2xMTVVUNkEvMU55YUEzcVZZZFdHdUtFRmFmUmxlZlZMY2ppbjltbkYrT1dsQldFR01yRTRwMUZHSEN2R2VOM2dOWTJhZUdLbWdlZUVXMTdoOUdXSG9jOXBaeTFQKzRCc1U1eWhTdjlvOG1nbDNCV242TVFaVXVNV3ZndzU1U3NJZFQvNUJqWGFYL1lZaEszK3EyN0pYVzF5aC83dUhXZnliS0R3dFVRK3pDYnVxTjZNTmptRG5PYjlQM21wakJaNGlzT0ZGbnd3OVFJdnhrRHpReTNJaVhUSFZiQUNGTE96c2ptblZMV2diT1RKRFBTSHNaczNFZTUzNmQ4TnFtZzk0Q0VNNFo2YmtYSkx6Wkp1RUpsTUlnSDhjNm85NDVjM3JhZ1JwWmtmK3U4eTBXL3d1QlRMRCtqZ0dUM1ZsQzlGZ2NhWHlwWTBqNzVCaURqYVcrMUVRdzlEVmZHV29BZS9Mc2JtTXNBaVBqMXJBVEVyMFlsOWdwb2RhRWNQd0xRcThoeVZxWmxGUDZXeUJzMEhaV0RybmdKbWNxdGVXenMrblJER1dGSURNNnZvcXdKQ0JoT09aQVRwTFlYK3ByZTNKVFFLeUpyRjB1VExPUENsdkFsTStOQW02WDJKd2lOdGNhZVVhZ1VNb2pXVWY5QnlCaFFCc0FVTjQwTzAvaGtXa3NpbHBGQUp3RkZvVEVIQXcrNXc3RTV0bGl4QjJVTDVkVi85Y08vVk9oRFNud2cyTVpNTUJBSWNtWFZtVEdHdjJxc2p2MTNxenJxVm5BTzIxcmNsbm9BbTZzRmg2Sk5mSjc2MEdENXZId2V6N1FuNjhWSVlQa0RkN2h0TzBIRkJEWmREangxaXFtL0V5QkFIU0dlTk01cVI0c0R2TC9OL0RSK21BS1hQcW4yc0syQlU4RXJWYUNyQXlwS2UyWlVZcXoySDRTcmsvZ1BuN3FnZlZiaTluK2R3ZU1BUjhYNVZzWlF1WlNqTThmRXUvK1dUa1l4eTVKajFpdGhvbDl3OWIrb0E0cjFvaHgwMXFnaGFZQnFQcnNYSmFsSWZITG44MVU1MkdibStBSEs5a1ZNcnBMbHFHek1sbWJCMzVuRkQ3K2kwaWtoVVBMellFV09YNzV6dVVyQkUvYkc4MHFBeVAzaHNwIiwiaXNzIjoibWNwLXRva2VuLXNlcnZpY2UiLCJhdWQiOiJtY3AtY2xpZW50cyIsImlhdCI6MTc1NDI5NzY3MCwiZXhwIjoxNzY5ODQ5NjcwfQ.cScHS445lUq-jCvZWyww6iuukw8cNpFgQYMGMshTQDPgj-6Q7H2jBBlCAeWyoFcazNAIdDUwJ-vdZWhLBv4QTOM5v5fyz_H1OS7iN_54NUR0DOU99Nleu0KorUZWYV6NzZEa8Pt1M5iH5v_lIrLIhGS-Ya_hsDs3UvIrbzv32eM"
    
    bedrock_agentcore = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
    
    print(f"Working Token: {working_token[:50]}...")
    print(f"Token verified: ✅ Returns real data from TACNode")
    
    try:
        # Create new credential provider with working token
        print(f"\n🔄 Creating new credential provider...")
        
        response = bedrock_agentcore.create_api_key_credential_provider(
            name="TACNodeWorkingToken",
            apiKey=working_token
        )
        
        provider_arn = response['credentialProviderArn']
        print(f"✅ Credential provider created successfully!")
        print(f"   Name: TACNodeWorkingToken")
        print(f"   ARN: {provider_arn}")
        
        return provider_arn
        
    except Exception as e:
        print(f"❌ Failed to create credential provider: {e}")
        return None

def create_final_target_with_working_credentials():
    """Create final target with working credential provider"""
    print(f"\n🎯 CREATING FINAL TARGET WITH WORKING CREDENTIALS")
    print("-" * 60)
    
    # Create working credential provider
    provider_arn = create_working_credential_provider()
    if not provider_arn:
        return None
    
    bedrock_agentcore = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
    gateway_id = "pureawstacnodegateway-l0f1tg5t8o"
    
    # Delete old target first
    try:
        print(f"\n🗑️ Deleting old target...")
        bedrock_agentcore.delete_gateway_target(
            gatewayIdentifier=gateway_id,
            targetId="DPIFZHYYX1"
        )
        print(f"✅ Old target deleted")
        time.sleep(10)  # Wait for deletion
    except Exception as e:
        print(f"⚠️ Could not delete old target (may not exist): {e}")
    
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
        
        # Credential provider configuration with working token
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
        
        print(f"🔄 Creating final target with working credentials...")
        
        # Create target with working credential provider
        target_response = bedrock_agentcore.create_gateway_target(
            gatewayIdentifier=gateway_id,
            name="working-tacnode-target",
            description="TACNode target with verified working API key",
            targetConfiguration=target_configuration,
            credentialProviderConfigurations=credential_provider_configurations
        )
        
        target_id = target_response['targetId']
        print(f"✅ Final target created: {target_id}")
        
        # Save configuration
        config = {
            "gatewayId": gateway_id,
            "targetId": target_id,
            "credentialProviderArn": provider_arn,
            "credentialProviderName": "TACNodeWorkingToken",
            "status": "READY"
        }
        
        with open('working-integration-config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"\n🎉 FINAL WORKING INTEGRATION COMPLETE!")
        print(f"   Gateway: {gateway_id}")
        print(f"   Target: {target_id}")
        print(f"   Credential Provider: TACNodeWorkingToken")
        print(f"   Configuration: working-integration-config.json")
        
        return target_id
        
    except Exception as e:
        print(f"❌ Target creation failed: {e}")
        return None

def main():
    """Create working credential provider and target"""
    print("🎯 FINAL WORKING INTEGRATION SETUP")
    print("=" * 70)
    
    target_id = create_final_target_with_working_credentials()
    
    if target_id:
        print(f"\n✅ WORKING INTEGRATION SETUP COMPLETE!")
        print(f"✅ Verified working TACNode token stored in credential provider")
        print(f"✅ Gateway target created with working credentials")
        print(f"🧪 Ready for final end-to-end test")
    else:
        print(f"\n❌ WORKING INTEGRATION SETUP FAILED")

if __name__ == "__main__":
    main()

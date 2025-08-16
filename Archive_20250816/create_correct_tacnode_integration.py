#!/usr/bin/env python3
"""
Create the correct TACNode integration following the exact instructions
"""

import boto3
import json
import time

def create_correct_tacnode_integration():
    """Create TACNode integration using the exact format from instructions"""
    print("🎯 CREATING CORRECT TACNODE INTEGRATION")
    print("=" * 70)
    print("🔧 Following exact instructions from TACNode documentation")
    
    bedrock_agentcore = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
    
    # Working TACNode token
    working_token = "eyJhbGciOiJSUzI1NiJ9.eyJlbmNyeXB0ZWRDb25uZWN0aW9uIjoiMk51V2lPTzJzaGdmbnZvdVQvanJlWjFxNTlSekZ0QmlORmJtRytUMXlUblJXVkFseE9keGFWYXRsbHpONmJJNkt1VERCYU5XTzlZeUk2UDBKeGFVZFJ3dnE5YklQWUlZM2c4QUt0MlNmV3RQd1RPOW1FWmVVTkJlOVl6czZMQ1JIR2NTMmpZUFlDbUZXblRrMjZTeFQ1Y0FmbkNGVXd2SUxHaGo1QTBucVFPeDAxTEwyUUlabWtWck5aY2xMTVVUNkEvMU55YUEzcVZZZFdHdUtFRmFmUmxlZlZMY2ppbjltbkYrT1dsQldFR01yRTRwMUZHSEN2R2VOM2dOWTJhZUdLbWdlZUVXMTdoOUdXSG9jOXBaeTFQKzRCc1U1eWhTdjlvOG1nbDNCV242TVFaVXVNV3ZndzU1U3NJZFQvNUJqWGFYL1lZaEszK3EyN0pYVzF5aC83dUhXZnliS0R3dFVRK3pDYnVxTjZNTmptRG5PYjlQM21wakJaNGlzT0ZGbnd3OVFJdnhrRHpReTNJaVhUSFZiQUNGTE96c2ptblZMV2diT1RKRFBTSHNaczNFZTUzNmQ4TnFtZzk0Q0VNNFo2YmtYSkx6Wkp1RUpsTUlnSDhjNm85NDVjM3JhZ1JwWmtmK3U4eTBXL3d1QlRMRCtqZ0dUM1ZsQzlGZ2NhWHlwWTBqNzVCaURqYVcrMUVRdzlEVmZHV29BZS9Mc2JtTXNBaVBqMXJBVEVyMFlsOWdwb2RhRWNQd0xRcThoeVZxWmxGUDZXeUJzMEhaV0RybmdKbWNxdGVXenMrblJER1dGSURNNnZvcXdKQ0JoT09aQVRwTFlYK3ByZTNKVFFLeUpyRjB1VExPUENsdkFsTStOQW02WDJKd2lOdGNhZVVhZ1VNb2pXVWY5QnlCaFFCc0FVTjQwTzAvaGtXa3NpbHBGQUp3RkZvVEVIQXcrNXc3RTV0bGl4QjJVTDVkVi85Y08vVk9oRFNud2cyTVpNTUJBSWNtWFZtVEdHdjJxc2p2MTNxenJxVm5BTzIxcmNsbm9BbTZzRmg2Sk5mSjc2MEdENXZId2V6N1FuNjhWSVlQa0RkN2h0TzBIRkJEWmREangxaXFtL0V5QkFIU0dlTk01cVI0c0R2TC9OL0RSK21BS1hQcW4yc0syQlU4RXJWYUNyQXlwS2UyWlVZcXoySDRTcmsvZ1BuN3FnZlZiaTluK2R3ZU1BUjhYNVZzWlF1WlNqTThmRXUvK1dUa1l4eTVKajFpdGhvbDl3OWIrb0E0cjFvaHgwMXFnaGFZQnFQcnNYSmFsSWZITG44MVU1MkdibStBSEs5a1ZNcnBMbHFHek1sbWJCMzVuRkQ3K2kwaWtoVVBMellFV09YNzV6dVVyQkUvYkc4MHFBeVAzaHNwIiwiaXNzIjoibWNwLXRva2VuLXNlcnZpY2UiLCJhdWQiOiJtY3AtY2xpZW50cyIsImlhdCI6MTc1NDI5NzY3MCwiZXhwIjoxNzY5ODQ5NjcwfQ.cScHS445lUq-jCvZWyww6iuukw8cNpFgQYMGMshTQDPgj-6Q7H2jBBlCAeWyoFcazNAIdDUwJ-vdZWhLBv4QTOM5v5fyz_H1OS7iN_54NUR0DOU99Nleu0KorUZWYV6NzZEa8Pt1M5iH5v_lIrLIhGS-Ya_hsDs3UvIrbzv32eM"
    
    gateway_id = "pureawstacnodegateway-l0f1tg5t8o"
    
    print(f"Working Token: {working_token[:50]}...")
    print(f"Gateway ID: {gateway_id}")
    
    try:
        # Step 1: Create API Key Credential Provider (exactly as instructed)
        print(f"\n📋 STEP 1: Creating API Key Credential Provider")
        print("-" * 50)
        
        # Delete old providers first
        try:
            bedrock_agentcore.delete_api_key_credential_provider(name="TACNodeDirectProvider")
            print(f"✅ Deleted old provider")
            time.sleep(5)
        except Exception as e:
            print(f"⚠️ Could not delete old provider: {e}")
        
        # Create new provider with exact name from instructions
        provider_response = bedrock_agentcore.create_api_key_credential_provider(
            name="tacnode-mcp-token",
            apiKey=working_token
        )
        
        provider_arn = provider_response['credentialProviderArn']
        print(f"✅ API Key Credential Provider created!")
        print(f"   Name: tacnode-mcp-token")
        print(f"   ARN: {provider_arn}")
        
        # Step 2: Create Gateway Target with EXACT OpenAPI schema from instructions
        print(f"\n📋 STEP 2: Creating Gateway Target with Correct OpenAPI")
        print("-" * 50)
        
        # Delete old target first
        try:
            bedrock_agentcore.delete_gateway_target(
                gatewayIdentifier=gateway_id,
                targetId="OWU4CASS93"
            )
            print(f"✅ Deleted old target")
            time.sleep(15)
        except Exception as e:
            print(f"⚠️ Could not delete old target: {e}")
        
        # EXACT OpenAPI schema from the instructions (simplified)
        openapi_schema = {
            "openapi": "3.0.1",
            "info": {
                "title": "Tacnode MCP",
                "version": "1"
            },
            "servers": [
                {
                    "url": "https://mcp-server.tacnode.io"
                }
            ],
            "paths": {
                "/mcp": {
                    "post": {
                        "operationId": "tools_call",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object"
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "OK",
                                "content": {
                                    "application/json": {}
                                }
                            }
                        }
                    }
                }
            }
        }
        
        # Target configuration with EXACT format from instructions
        target_configuration = {
            "mcp": {
                "openApiSchema": {
                    "inlinePayload": json.dumps(openapi_schema)
                }
            }
        }
        
        # Credential provider configuration with EXACT format from instructions
        credential_provider_configurations = [
            {
                "credentialProviderType": "API_KEY",
                "credentialProvider": {
                    "apiKeyCredentialProvider": {
                        "providerArn": provider_arn,
                        "credentialLocation": "HEADER",
                        "credentialParameterName": "Authorization",
                        "credentialPrefix": "Bearer "
                    }
                }
            }
        ]
        
        print(f"🔄 Creating target with EXACT configuration from instructions...")
        print(f"OpenAPI Schema: {json.dumps(openapi_schema, indent=2)}")
        
        # Create target with EXACT format
        target_response = bedrock_agentcore.create_gateway_target(
            gatewayIdentifier=gateway_id,
            name="tacnode-mcp",
            description="TACNode MCP target following exact instructions",
            targetConfiguration=target_configuration,
            credentialProviderConfigurations=credential_provider_configurations
        )
        
        target_id = target_response['targetId']
        print(f"✅ Gateway target created: {target_id}")
        
        # Save configuration
        config = {
            "gatewayId": gateway_id,
            "targetId": target_id,
            "credentialProviderArn": provider_arn,
            "credentialProviderName": "tacnode-mcp-token",
            "openApiSchema": openapi_schema,
            "credentialConfiguration": {
                "credentialLocation": "HEADER",
                "credentialParameterName": "Authorization",
                "credentialPrefix": "Bearer "
            },
            "status": "READY"
        }
        
        with open('correct-tacnode-integration.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"\n🎉 CORRECT TACNODE INTEGRATION COMPLETE!")
        print(f"   Gateway: {gateway_id}")
        print(f"   Target: {target_id}")
        print(f"   Credential Provider: tacnode-mcp-token")
        print(f"   OpenAPI: Simplified schema as per instructions")
        print(f"   Configuration: correct-tacnode-integration.json")
        
        return target_id
        
    except Exception as e:
        print(f"❌ Integration creation failed: {e}")
        return None

def main():
    """Create correct TACNode integration"""
    print("🎯 CORRECT TACNODE INTEGRATION SETUP")
    print("=" * 70)
    print("🔧 Following EXACT instructions from TACNode documentation")
    print("🔧 Using simplified OpenAPI schema")
    print("🔧 Proper credential provider configuration")
    
    target_id = create_correct_tacnode_integration()
    
    if target_id:
        print(f"\n✅ CORRECT INTEGRATION SETUP COMPLETE!")
        print(f"✅ Following exact TACNode instructions")
        print(f"✅ Simplified OpenAPI schema")
        print(f"✅ Proper credential injection configuration")
        print(f"🧪 Ready for final test")
    else:
        print(f"\n❌ CORRECT INTEGRATION SETUP FAILED")

if __name__ == "__main__":
    main()

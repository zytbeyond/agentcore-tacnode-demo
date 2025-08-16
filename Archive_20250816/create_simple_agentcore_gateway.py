#!/usr/bin/env python3
"""
Create simple AgentCore Gateway for TACNode with SSE support
"""

import boto3
import json
import time
import os

def get_tacnode_token():
    """Get TACNode token"""
    if os.path.exists('tacnode_token.txt'):
        with open('tacnode_token.txt', 'r') as f:
            token = f.read().strip()
        if token:
            return token
    return None

def create_simple_gateway():
    """Create a simple AgentCore Gateway"""
    print("🏗️ CREATING SIMPLE AGENTCORE GATEWAY")
    print("=" * 70)
    
    bedrock_agentcore = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
    
    try:
        gateway_name = "augment-simple-tacnode-gateway"
        
        print(f"📋 Creating simple gateway: {gateway_name}")
        
        # Try the simplest possible gateway creation
        gateway_response = bedrock_agentcore.create_gateway(
            name=gateway_name
        )
        
        gateway_id = gateway_response['gatewayId']
        print(f"✅ Gateway created: {gateway_id}")
        
        # Wait for gateway to be ready
        print(f"⏳ Waiting for gateway to be ready...")
        time.sleep(30)
        
        # Get gateway details
        gateway_details = bedrock_agentcore.get_gateway(gatewayIdentifier=gateway_id)
        gateway_url = gateway_details['gateway']['gatewayUrl']
        
        print(f"✅ Gateway status: {gateway_details['gateway']['status']}")
        print(f"✅ Gateway URL: {gateway_url}")
        
        return gateway_id, gateway_url
        
    except Exception as e:
        print(f"❌ Error creating gateway: {e}")
        print(f"🔍 Let's check what parameters are required...")
        
        # Try to get more information about the error
        try:
            # List available gateways to see the format
            gateways = bedrock_agentcore.list_gateways()
            print(f"📊 Existing gateways: {json.dumps(gateways, indent=2, default=str)}")
        except Exception as list_error:
            print(f"❌ Could not list gateways: {list_error}")
        
        return None, None

def create_api_key_provider(tacnode_token):
    """Create API key credential provider"""
    print(f"\n🔑 CREATING API KEY CREDENTIAL PROVIDER")
    print("-" * 50)
    
    bedrock_agentcore = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
    
    try:
        provider_name = "augment-tacnode-simple-key"
        
        print(f"📋 Creating credential provider: {provider_name}")
        
        provider_response = bedrock_agentcore.create_api_key_credential_provider(
            name=provider_name,
            apiKey=tacnode_token
        )
        
        provider_arn = provider_response['credentialProviderArn']
        print(f"✅ Credential provider created: {provider_arn}")
        
        return provider_arn
        
    except Exception as e:
        print(f"❌ Error creating credential provider: {e}")
        return None

def create_tacnode_target_with_sse(gateway_id, provider_arn):
    """Create TACNode target with SSE support"""
    print(f"\n🎯 CREATING TACNODE TARGET WITH SSE SUPPORT")
    print("-" * 50)
    
    bedrock_agentcore = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
    
    try:
        # OpenAPI schema that supports SSE responses
        openapi_schema = {
            "openapi": "3.0.1",
            "info": {
                "title": "TACNode MCP Server with SSE",
                "version": "1.0.0",
                "description": "TACNode MCP Server with Server-Sent Events support"
            },
            "servers": [
                {
                    "url": "https://mcp-server.tacnode.io"
                }
            ],
            "paths": {
                "/mcp": {
                    "post": {
                        "operationId": "mcp_sse_call",
                        "summary": "Execute MCP calls with SSE response",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "jsonrpc": {
                                                "type": "string",
                                                "example": "2.0"
                                            },
                                            "method": {
                                                "type": "string",
                                                "example": "tools/call"
                                            },
                                            "params": {
                                                "type": "object"
                                            },
                                            "id": {
                                                "type": "integer",
                                                "example": 1
                                            }
                                        },
                                        "required": ["jsonrpc", "method", "id"]
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "SSE response from TACNode",
                                "content": {
                                    "text/event-stream": {
                                        "schema": {
                                            "type": "string",
                                            "description": "Server-Sent Events stream"
                                        }
                                    },
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "description": "Fallback JSON response"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        target_name = "augment-tacnode-sse"
        
        print(f"📋 Creating target: {target_name}")
        print(f"📊 Using TACNode endpoint: https://mcp-server.tacnode.io/mcp")
        print(f"📊 Supporting SSE responses")
        
        # Target configuration
        target_configuration = {
            "mcp": {
                "openApiSchema": {
                    "inlinePayload": json.dumps(openapi_schema)
                }
            }
        }
        
        # Credential provider configuration
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
        
        # Create target
        target_response = bedrock_agentcore.create_gateway_target(
            gatewayIdentifier=gateway_id,
            name=target_name,
            description="TACNode MCP Server with SSE support - Created by Augment Agent",
            targetConfiguration=target_configuration,
            credentialProviderConfigurations=credential_provider_configurations
        )
        
        target_id = target_response['targetId']
        print(f"✅ Target created: {target_id}")
        
        # Wait for target to be ready
        print(f"⏳ Waiting for target to be ready...")
        time.sleep(30)
        
        return target_id
        
    except Exception as e:
        print(f"❌ Error creating target: {e}")
        return None

def save_simple_configuration(gateway_id, gateway_url, provider_arn, target_id):
    """Save simple configuration"""
    config = {
        "gateway": {
            "id": gateway_id,
            "url": gateway_url,
            "name": "augment-simple-tacnode-gateway"
        },
        "credentialProvider": {
            "arn": provider_arn,
            "name": "augment-tacnode-simple-key"
        },
        "target": {
            "id": target_id,
            "name": "augment-tacnode-sse"
        },
        "tacnode": {
            "endpoint": "https://mcp-server.tacnode.io/mcp",
            "database": "postgres",
            "table": "test",
            "responseFormat": "text/event-stream"
        },
        "cognito": {
            "userPoolId": "us-east-1_qVOK14gn5",
            "clientId": "629cm5j58a7o0lhh1qph1re0l5",
            "clientSecret": "t7uo744afdgrlasjgqe0rsdasdm8ovg91otr12guk4jq79c3d64",
            "tokenEndpoint": "https://us-east-1-qvok14gn5.auth.us-east-1.amazoncognito.com/oauth2/token"
        },
        "created_by": "Augment Agent",
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "notes": "TACNode returns SSE responses that need special handling"
    }
    
    with open('augment-simple-tacnode-config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Configuration saved to: augment-simple-tacnode-config.json")
    
    return config

def main():
    """Main setup function"""
    print("🚀 SIMPLE AGENTCORE GATEWAY + TACNODE SETUP")
    print("=" * 70)
    print("🎯 Creating simple AgentCore Gateway for TACNode")
    print("🎯 Supporting SSE (Server-Sent Events) responses")
    print("🎯 All resources prefixed with 'augment-' for identification")
    
    # Get TACNode token
    tacnode_token = get_tacnode_token()
    if not tacnode_token:
        print("❌ No TACNode token found. Exiting.")
        return
    
    print(f"✅ TACNode token loaded")
    
    # Step 1: Create simple gateway
    gateway_id, gateway_url = create_simple_gateway()
    if not gateway_id:
        print("❌ Failed to create gateway. Exiting.")
        return
    
    # Step 2: Create credential provider
    provider_arn = create_api_key_provider(tacnode_token)
    if not provider_arn:
        print("❌ Failed to create credential provider. Exiting.")
        return
    
    # Step 3: Create TACNode target with SSE support
    target_id = create_tacnode_target_with_sse(gateway_id, provider_arn)
    if not target_id:
        print("❌ Failed to create TACNode target. Exiting.")
        return
    
    # Step 4: Save configuration
    config = save_simple_configuration(gateway_id, gateway_url, provider_arn, target_id)
    
    print(f"\n" + "=" * 70)
    print(f"🎉 SIMPLE AGENTCORE GATEWAY SETUP COMPLETE!")
    print(f"✅ Gateway ID: {gateway_id}")
    print(f"✅ Gateway URL: {gateway_url}")
    print(f"✅ Target ID: {target_id}")
    print(f"✅ SSE support configured")
    print(f"✅ Configuration saved")
    
    print(f"\n🧪 NEXT STEPS:")
    print(f"1. Test the gateway integration")
    print(f"2. Verify SSE response handling")
    print(f"3. Query the TACNode database")

if __name__ == "__main__":
    main()

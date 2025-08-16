#!/usr/bin/env python3
"""
Recreate the target with enhanced debugging and different configurations
"""

import boto3
import json
import time

def recreate_target_with_debug():
    """Recreate the target with enhanced configuration"""
    print("🔧 RECREATING TARGET WITH ENHANCED CONFIGURATION")
    print("=" * 70)
    
    bedrock_agentcore = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
    
    gateway_id = "pureawstacnodegateway-l0f1tg5t8o"
    credential_provider_arn = "arn:aws:bedrock-agentcore:us-east-1:560155322832:token-vault/default/apikeycredentialprovider/tacnode-mcp-token"
    
    try:
        # Delete existing target
        print(f"📋 STEP 1: Deleting existing target")
        print("-" * 50)
        
        try:
            bedrock_agentcore.delete_gateway_target(
                gatewayIdentifier=gateway_id,
                targetId="XXVXVNHOV9"
            )
            print(f"✅ Deleted existing target")
            time.sleep(15)
        except Exception as e:
            print(f"⚠️ Could not delete existing target: {e}")
        
        # Create enhanced OpenAPI schema with more explicit configuration
        print(f"\n📋 STEP 2: Creating enhanced OpenAPI schema")
        print("-" * 50)
        
        enhanced_openapi_schema = {
            "openapi": "3.0.1",
            "info": {
                "title": "TACNode MCP Server",
                "version": "1.0.0",
                "description": "TACNode Managed MCP Server API"
            },
            "servers": [
                {
                    "url": "https://mcp-server.tacnode.io",
                    "description": "TACNode MCP Server"
                }
            ],
            "paths": {
                "/mcp": {
                    "post": {
                        "operationId": "tools_call",
                        "summary": "Execute MCP tool call",
                        "description": "Execute a tool call on the TACNode MCP server",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "jsonrpc": {
                                                "type": "string",
                                                "enum": ["2.0"]
                                            },
                                            "method": {
                                                "type": "string",
                                                "enum": ["tools/call"]
                                            },
                                            "params": {
                                                "type": "object",
                                                "properties": {
                                                    "name": {
                                                        "type": "string"
                                                    },
                                                    "arguments": {
                                                        "type": "object"
                                                    }
                                                },
                                                "required": ["name", "arguments"]
                                            },
                                            "id": {
                                                "type": ["string", "number"]
                                            }
                                        },
                                        "required": ["jsonrpc", "method", "params", "id"]
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "Successful response",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object"
                                        }
                                    }
                                }
                            }
                        },
                        "security": [
                            {
                                "bearerAuth": []
                            }
                        ]
                    }
                }
            },
            "components": {
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                }
            }
        }
        
        print(f"✅ Enhanced OpenAPI schema created")
        print(f"📊 Schema includes explicit security configuration")
        
        # Target configuration
        target_configuration = {
            "mcp": {
                "openApiSchema": {
                    "inlinePayload": json.dumps(enhanced_openapi_schema)
                }
            }
        }
        
        # Enhanced credential provider configuration
        credential_provider_configurations = [
            {
                "credentialProviderType": "API_KEY",
                "credentialProvider": {
                    "apiKeyCredentialProvider": {
                        "providerArn": credential_provider_arn,
                        "credentialLocation": "HEADER",
                        "credentialParameterName": "Authorization",
                        "credentialPrefix": "Bearer "
                    }
                }
            }
        ]
        
        print(f"\n📋 STEP 3: Creating enhanced target")
        print("-" * 50)
        
        # Create target with enhanced configuration
        target_response = bedrock_agentcore.create_gateway_target(
            gatewayIdentifier=gateway_id,
            name="tacnode-mcp-enhanced",
            description="Enhanced TACNode MCP target with explicit security configuration",
            targetConfiguration=target_configuration,
            credentialProviderConfigurations=credential_provider_configurations
        )
        
        target_id = target_response['targetId']
        print(f"✅ Enhanced target created: {target_id}")
        
        # Wait for target to be ready
        print(f"⏳ Waiting for target to be ready...")
        time.sleep(30)
        
        # Test the enhanced target
        print(f"\n📋 STEP 4: Testing enhanced target")
        print("-" * 50)
        
        import asyncio
        import httpx
        import requests
        import base64
        
        # Get Cognito token
        cognito_config = {
            "userPoolId": "us-east-1_qVOK14gn5",
            "clientId": "629cm5j58a7o0lhh1qph1re0l5",
            "clientSecret": "t7uo744afdgrlasjgqe0rsdasdm8ovg91otr12guk4jq79c3d64",
            "tokenEndpoint": "https://us-east-1-qvok14gn5.auth.us-east-1.amazoncognito.com/oauth2/token"
        }
        
        client_id = cognito_config['clientId']
        client_secret = cognito_config['clientSecret']
        token_endpoint = cognito_config['tokenEndpoint']
        
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
        
        response = requests.post(token_endpoint, headers=headers, data=data, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Failed to get Cognito token: {response.status_code}")
            return False
        
        token_data = response.json()
        access_token = token_data['access_token']
        print(f"✅ Got Cognito token")
        
        gateway_url = "https://pureawstacnodegateway-l0f1tg5t8o.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp"
        
        gateway_headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        async def test_enhanced_target():
            async with httpx.AsyncClient(timeout=30.0) as client:
                
                # Check tools list
                list_request = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/list"
                }
                
                response = await client.post(gateway_url, json=list_request, headers=gateway_headers)
                print(f"Tools list status: {response.status_code}")
                
                if response.status_code == 200:
                    response_json = response.json()
                    if 'result' in response_json and not response_json['result'].get('isError', False):
                        tools = response_json['result'].get('tools', [])
                        print(f"✅ Found {len(tools)} tools:")
                        
                        enhanced_tool_name = None
                        for tool in tools:
                            tool_name = tool.get('name', 'Unknown')
                            print(f"  - {tool_name}")
                            if 'tacnode-mcp-enhanced' in tool_name:
                                enhanced_tool_name = tool_name
                        
                        if enhanced_tool_name:
                            print(f"\n🧪 Testing enhanced tool: {enhanced_tool_name}")
                            
                            # Test with proper JSON-RPC format
                            test_request = {
                                "jsonrpc": "2.0",
                                "id": 1,
                                "method": "tools/call",
                                "params": {
                                    "name": enhanced_tool_name,
                                    "arguments": {
                                        "jsonrpc": "2.0",
                                        "method": "tools/call",
                                        "params": {
                                            "name": "query",
                                            "arguments": {
                                                "sql": "SELECT 'ENHANCED_TARGET' as test_type, 'EXPLICIT_SECURITY' as config_type, NOW() as test_time"
                                            }
                                        },
                                        "id": 1
                                    }
                                }
                            }
                            
                            response = await client.post(gateway_url, json=test_request, headers=gateway_headers)
                            print(f"Enhanced test status: {response.status_code}")
                            
                            if response.status_code == 200:
                                response_json = response.json()
                                print(f"Enhanced test response: {json.dumps(response_json, indent=2)}")
                                
                                if 'result' in response_json:
                                    result = response_json['result']
                                    if result.get('isError', False):
                                        error_content = result.get('content', [{}])[0].get('text', '')
                                        print(f"\n❌ Enhanced target still failed: {error_content}")
                                        
                                        if 'internal error' in error_content.lower():
                                            print(f"🔍 Still getting internal error - this may be a service limitation")
                                            return False
                                        else:
                                            print(f"🔍 Different error - progress made")
                                            return False
                                    else:
                                        content = result.get('content', [])
                                        if content and len(content) > 0:
                                            text_content = content[0].get('text', '')
                                            print(f"\n🎉 ENHANCED TARGET SUCCESS!")
                                            print(f"📊 Data: {text_content}")
                                            return True
                                        else:
                                            print(f"❌ No content in result")
                                            return False
                                else:
                                    print(f"❌ No result in response")
                                    return False
                            else:
                                print(f"❌ Enhanced test HTTP error: {response.status_code}")
                                return False
                        else:
                            print(f"❌ Enhanced tool not found")
                            return False
                    else:
                        print(f"❌ Tools list failed")
                        return False
                else:
                    print(f"❌ Tools list HTTP error: {response.status_code}")
                    return False
        
        success = asyncio.run(test_enhanced_target())
        
        # Save configuration
        config = {
            "gatewayId": gateway_id,
            "targetId": target_id,
            "credentialProviderArn": credential_provider_arn,
            "openApiSchema": enhanced_openapi_schema,
            "status": "ENHANCED" if success else "FAILED"
        }
        
        with open('enhanced-tacnode-integration.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        return success
        
    except Exception as e:
        print(f"❌ Error recreating target: {e}")
        return False

def main():
    """Recreate target with enhanced configuration"""
    print("🔧 ENHANCED TARGET RECREATION")
    print("=" * 70)
    print("🎯 Creating target with explicit security configuration")
    print("🎯 Enhanced OpenAPI schema with proper authentication")
    
    success = recreate_target_with_debug()
    
    print(f"\n" + "=" * 70)
    if success:
        print(f"🎉 ENHANCED TARGET SUCCESSFUL!")
        print(f"✅ Enhanced OpenAPI schema working")
        print(f"✅ Explicit security configuration")
        print(f"✅ Real data retrieved from TACNode")
    else:
        print(f"❌ ENHANCED TARGET FAILED")
        print(f"🔍 This suggests a fundamental service limitation")
        print(f"💡 Consider contacting AWS support for AgentCore Gateway issues")

if __name__ == "__main__":
    main()

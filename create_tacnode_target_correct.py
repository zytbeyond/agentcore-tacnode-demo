#!/usr/bin/env python3
"""
Create TACNode target with correct configuration structure
"""

import boto3
import json
import subprocess
import os

def create_api_key_credential_provider():
    """Create API key credential provider for TACNode token"""
    try:
        token = os.getenv('TACNODE_TOKEN')
        if not token:
            print("❌ TACNODE_TOKEN not found")
            return None
        
        print("🔑 Creating API Key Credential Provider...")
        
        # Create credential provider configuration
        provider_config = {
            "name": "TACNodeAPIKeyProvider",
            "description": "API Key provider for TACNode MCP Server authentication",
            "credentialType": "API_KEY",
            "credentialValue": token
        }
        
        # Save config to file
        with open('/tmp/credential-provider-config.json', 'w') as f:
            json.dump(provider_config, f, indent=2)
        
        # Use AWS CLI to create credential provider
        cmd = [
            'aws', 'bedrock-agentcore-control', 'create-api-key-credential-provider',
            '--cli-input-json', 'file:///tmp/credential-provider-config.json',
            '--region', 'us-east-1'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            response = json.loads(result.stdout)
            print(f"✅ Credential provider created: {response['providerArn']}")
            return response['providerArn']
        else:
            print(f"❌ Credential provider creation failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating credential provider: {str(e)}")
        return None

def create_tacnode_target_correct():
    """Create TACNode target with correct structure"""
    try:
        # Get gateway ID from saved file
        with open('tacnode-agentcore-gateway.json', 'r') as f:
            gateway_data = json.load(f)
            gateway_id = gateway_data['gatewayId']
        
        print(f"🎯 Creating TACNode target for gateway: {gateway_id}")
        
        # Create credential provider first
        provider_arn = create_api_key_credential_provider()
        if not provider_arn:
            print("❌ Cannot create target without credential provider")
            return None
        
        # Create target configuration with correct structure
        target_config = {
            "gatewayIdentifier": gateway_id,
            "name": "TACNodeContextLake",
            "description": "TACNode Context Lake MCP Server for real-time data analytics",
            "targetConfiguration": {
                "mcp": {
                    "lambda": {
                        "lambdaArn": "arn:aws:lambda:us-east-1:560155322832:function:tacnode-mcp-proxy",
                        "toolSchema": {
                            "inlinePayload": [
                                {
                                    "name": "query",
                                    "description": "Execute read-only SQL queries on TACNode Context Lake",
                                    "inputSchema": {
                                        "type": "object",
                                        "properties": {
                                            "sql": {
                                                "type": "string",
                                                "description": "SQL query to execute"
                                            }
                                        },
                                        "required": ["sql"]
                                    },
                                    "outputSchema": {
                                        "type": "object",
                                        "properties": {
                                            "result": {
                                                "type": "array",
                                                "description": "Query results as JSON array"
                                            },
                                            "isError": {
                                                "type": "boolean",
                                                "description": "Whether the query resulted in an error"
                                            }
                                        }
                                    }
                                }
                            ]
                        }
                    }
                }
            },
            "credentialProviderConfigurations": [
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
        }
        
        # Save config to file
        with open('/tmp/target-config-correct.json', 'w') as f:
            json.dump(target_config, f, indent=2)
        
        print(f"   Target Name: {target_config['name']}")
        print(f"   Configuration Type: MCP Lambda")
        print(f"   Credential Provider: {provider_arn}")
        
        # Use AWS CLI to create target
        cmd = [
            'aws', 'bedrock-agentcore-control', 'create-gateway-target',
            '--cli-input-json', 'file:///tmp/target-config-correct.json',
            '--region', 'us-east-1'
        ]
        
        print("\n🚀 Executing target creation...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            response = json.loads(result.stdout)
            print("✅ TACNode target created successfully!")
            print(f"   Target ID: {response['targetId']}")
            print(f"   Status: {response['status']}")
            
            # Save target details
            with open('tacnode-agentcore-target.json', 'w') as f:
                json.dump(response, f, indent=2)
            
            return response
        else:
            print(f"❌ Target creation failed:")
            print(f"   Error: {result.stderr}")
            print(f"   Output: {result.stdout}")
            
            # Try alternative approach without Lambda
            return create_tacnode_target_alternative()
            
    except Exception as e:
        print(f"❌ Error creating target: {str(e)}")
        return None

def create_tacnode_target_alternative():
    """Create TACNode target with OpenAPI schema approach"""
    try:
        print("\n🔄 Trying alternative approach with OpenAPI schema...")
        
        # Get gateway ID
        with open('tacnode-agentcore-gateway.json', 'r') as f:
            gateway_data = json.load(f)
            gateway_id = gateway_data['gatewayId']
        
        # Create simple OpenAPI schema for TACNode MCP
        openapi_schema = {
            "openapi": "3.0.0",
            "info": {
                "title": "TACNode MCP Server API",
                "version": "1.0.0",
                "description": "TACNode Context Lake MCP Server for real-time data analytics"
            },
            "servers": [
                {
                    "url": "https://mcp-server.tacnode.io/mcp",
                    "description": "TACNode MCP Server"
                }
            ],
            "paths": {
                "/": {
                    "post": {
                        "summary": "Execute MCP query",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "jsonrpc": {"type": "string"},
                                            "method": {"type": "string"},
                                            "params": {"type": "object"},
                                            "id": {"type": "integer"}
                                        }
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
                        }
                    }
                }
            }
        }
        
        # Alternative target configuration
        target_config = {
            "gatewayIdentifier": gateway_id,
            "name": "TACNodeContextLakeSimple",
            "description": "TACNode Context Lake MCP Server (Simple Configuration)",
            "targetConfiguration": {
                "mcp": {
                    "openApiSchema": {
                        "inlinePayload": json.dumps(openapi_schema)
                    }
                }
            },
            "credentialProviderConfigurations": [
                {
                    "credentialProviderType": "GATEWAY_IAM_ROLE",
                    "credentialProvider": {}
                }
            ]
        }
        
        # Save config to file
        with open('/tmp/target-config-simple.json', 'w') as f:
            json.dump(target_config, f, indent=2)
        
        print(f"   Target Name: {target_config['name']}")
        print(f"   Configuration Type: MCP OpenAPI")
        print(f"   Credential Provider: Gateway IAM Role")
        
        # Use AWS CLI to create target
        cmd = [
            'aws', 'bedrock-agentcore-control', 'create-gateway-target',
            '--cli-input-json', 'file:///tmp/target-config-simple.json',
            '--region', 'us-east-1'
        ]
        
        print("\n🚀 Executing alternative target creation...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            response = json.loads(result.stdout)
            print("✅ TACNode target created successfully (alternative)!")
            print(f"   Target ID: {response['targetId']}")
            print(f"   Status: {response['status']}")
            
            # Save target details
            with open('tacnode-agentcore-target-simple.json', 'w') as f:
                json.dump(response, f, indent=2)
            
            return response
        else:
            print(f"❌ Alternative target creation also failed:")
            print(f"   Error: {result.stderr}")
            print(f"   Output: {result.stdout}")
            return None
            
    except Exception as e:
        print(f"❌ Error with alternative approach: {str(e)}")
        return None

def main():
    print("🚀 Creating TACNode Target with Correct Configuration")
    print("=" * 70)
    
    try:
        # Check if gateway exists
        if not os.path.exists('tacnode-agentcore-gateway.json'):
            print("❌ Gateway not found. Please create gateway first.")
            return
        
        # Create target
        target = create_tacnode_target_correct()
        
        if target:
            print("\n✅ TACNode target creation successful!")
            print("\n🎯 Integration Status:")
            print("   ✅ Gateway: Created")
            print("   ✅ Target: Created")
            print("   ✅ Authentication: Configured")
            print("   ✅ Ready for AI agent integration")
        else:
            print("\n❌ Target creation failed")
            print("   Manual configuration may be required")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()

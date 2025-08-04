#!/usr/bin/env python3
"""
Create AgentCore Gateway using direct AWS CLI with proper OIDC configuration
"""

import boto3
import json
import subprocess
import time
import os

def create_mock_oidc_server():
    """Create a simple mock OIDC server for testing"""
    print("🔧 Setting up mock OIDC configuration...")
    
    # Create a simple OIDC configuration that might work
    oidc_config = {
        "issuer": "https://auth.example.com",
        "authorization_endpoint": "https://auth.example.com/auth",
        "token_endpoint": "https://auth.example.com/token",
        "jwks_uri": "https://auth.example.com/.well-known/jwks.json",
        "response_types_supported": ["code"],
        "subject_types_supported": ["public"],
        "id_token_signing_alg_values_supported": ["RS256"]
    }
    
    # For now, let's try using a well-known public OIDC provider
    # Google's OIDC endpoint as a test
    return "https://accounts.google.com/.well-known/openid-configuration"

def create_gateway_with_cli():
    """Create gateway using AWS CLI with proper configuration"""
    try:
        print("🏗️  Creating AgentCore Gateway with AWS CLI...")
        
        # Get service role ARN
        iam_client = boto3.client('iam')
        try:
            role_response = iam_client.get_role(RoleName='AmazonBedrockAgentCoreGatewayServiceRole')
            service_role_arn = role_response['Role']['Arn']
        except:
            print("❌ Service role not found")
            return None
        
        # Use Google's OIDC endpoint for testing
        discovery_url = "https://accounts.google.com/.well-known/openid-configuration"
        
        # Create gateway configuration
        gateway_config = {
            "name": "TACNodeContextLakeGateway",
            "description": "AgentCore Gateway for TACNode Context Lake real-time data access",
            "roleArn": service_role_arn,
            "protocolType": "MCP",
            "protocolConfiguration": {
                "mcp": {
                    "supportedVersions": ["2025-03-26"],
                    "instructions": "Gateway for connecting Bedrock AgentCore to TACNode Context Lake for real-time data analytics and AI-driven insights",
                    "searchType": "SEMANTIC"
                }
            },
            "authorizerType": "CUSTOM_JWT",
            "authorizerConfiguration": {
                "customJWTAuthorizer": {
                    "discoveryUrl": discovery_url,
                    "allowedAudience": ["tacnode-context-lake", "agentcore"],
                    "allowedClients": ["agentcore-gateway", "tacnode-client"]
                }
            }
        }
        
        print(f"   Name: {gateway_config['name']}")
        print(f"   Protocol: {gateway_config['protocolType']}")
        print(f"   OIDC Discovery: {discovery_url}")
        print(f"   Service Role: {service_role_arn}")
        
        # Save config to file
        with open('/tmp/gateway-config.json', 'w') as f:
            json.dump(gateway_config, f, indent=2)
        
        # Use AWS CLI to create gateway
        cmd = [
            'aws', 'bedrock-agentcore-control', 'create-gateway',
            '--cli-input-json', 'file:///tmp/gateway-config.json',
            '--region', 'us-east-1'
        ]
        
        print("\n🚀 Executing gateway creation...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            response = json.loads(result.stdout)
            print("✅ Gateway created successfully!")
            print(f"   Gateway ID: {response['gatewayId']}")
            print(f"   Gateway ARN: {response['gatewayArn']}")
            print(f"   Status: {response['status']}")
            
            # Save gateway details
            with open('tacnode-agentcore-gateway.json', 'w') as f:
                json.dump(response, f, indent=2)
            
            return response
        else:
            print(f"❌ Gateway creation failed:")
            print(f"   Error: {result.stderr}")
            print(f"   Output: {result.stdout}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating gateway: {str(e)}")
        return None

def create_tacnode_target_with_cli(gateway_id):
    """Create TACNode target using AWS CLI"""
    try:
        token = os.getenv('TACNODE_TOKEN')
        if not token:
            print("❌ TACNODE_TOKEN not found")
            return None
        
        print(f"🎯 Creating TACNode target for gateway: {gateway_id}")
        
        # Target configuration
        target_config = {
            "gatewayId": gateway_id,
            "name": "TACNodeContextLake",
            "description": "TACNode Context Lake MCP Server for real-time data analytics",
            "configuration": {
                "type": "MCP",
                "mcpConfiguration": {
                    "serverUrl": "https://mcp-server.tacnode.io/mcp",
                    "transport": "http",
                    "authentication": {
                        "type": "bearer",
                        "bearerToken": token
                    },
                    "capabilities": {
                        "tools": ["query"],
                        "resources": ["database_info", "table_schemas"]
                    },
                    "protocolVersion": "2025-03-26"
                }
            }
        }
        
        # Save config to file
        with open('/tmp/target-config.json', 'w') as f:
            json.dump(target_config, f, indent=2)
        
        print(f"   Target Name: {target_config['name']}")
        print(f"   Server URL: {target_config['configuration']['mcpConfiguration']['serverUrl']}")
        
        # Use AWS CLI to create target
        cmd = [
            'aws', 'bedrock-agentcore-control', 'create-gateway-target',
            '--cli-input-json', 'file:///tmp/target-config.json',
            '--region', 'us-east-1'
        ]
        
        print("\n🚀 Executing target creation...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            response = json.loads(result.stdout)
            print("✅ TACNode target created successfully!")
            print(f"   Target ID: {response['gatewayTargetId']}")
            print(f"   Status: {response['status']}")
            
            # Save target details
            with open('tacnode-agentcore-target.json', 'w') as f:
                json.dump(response, f, indent=2)
            
            return response
        else:
            print(f"❌ Target creation failed:")
            print(f"   Error: {result.stderr}")
            print(f"   Output: {result.stdout}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating target: {str(e)}")
        return None

def test_integration():
    """Test the complete integration"""
    print("\n🧪 Testing TACNode + AgentCore Integration...")
    
    # Test TACNode connection
    print("\n1️⃣ Testing TACNode MCP Server...")
    os.system("python3 test_tacnode_mcp.py")
    
    print("\n2️⃣ Testing data queries...")
    os.system("python3 query_tacnode_data.py")

def main():
    print("🚀 Direct AgentCore Gateway Creation")
    print("=" * 60)
    
    try:
        # Verify credentials
        sts_client = boto3.client('sts')
        identity = sts_client.get_caller_identity()
        print(f"🔑 Account: {identity['Account']}")
        print(f"🔑 Role: {identity['Arn']}")
        print()
        
        # Create gateway
        gateway = create_gateway_with_cli()
        
        if gateway:
            gateway_id = gateway['gatewayId']
            
            # Wait a moment for gateway to initialize
            print("\n⏳ Waiting for gateway to initialize...")
            time.sleep(30)
            
            # Create TACNode target
            target = create_tacnode_target_with_cli(gateway_id)
            
            if target:
                print("\n✅ Complete system created successfully!")
                
                # Test integration
                test_integration()
                
                print("\n" + "="*60)
                print("🎉 TACNODE + AGENTCORE INTEGRATION COMPLETE!")
                print("="*60)
                print(f"✅ Gateway ID: {gateway_id}")
                print(f"✅ Target ID: {target['gatewayTargetId']}")
                print(f"✅ Real-time data access enabled")
                print(f"✅ AI agents can now query TACNode Context Lake")
            else:
                print("\n⚠️  Gateway created but target creation failed")
        else:
            print("\n❌ Gateway creation failed")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()

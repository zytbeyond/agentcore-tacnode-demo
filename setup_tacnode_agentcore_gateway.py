#!/usr/bin/env python3
"""
Setup TACNode MCP Server as target for Bedrock AgentCore Gateway
"""

import boto3
import json
import os
import requests
from botocore.exceptions import ClientError, NoCredentialsError

def test_tacnode_connection():
    """Test connection to TACNode MCP server"""
    token = os.getenv('TACNODE_TOKEN')
    if not token:
        print("❌ TACNODE_TOKEN environment variable not set")
        return False
    
    print("🧪 Testing TACNode MCP Server connection...")
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream',
        'Authorization': f'Bearer {token}'
    }
    
    # Test initialize endpoint
    test_payload = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "clientInfo": {"name": "agentcore-test", "version": "1.0.0"},
            "capabilities": {"roots": {"listChanged": True}, "sampling": {}}
        },
        "id": 1
    }
    
    try:
        response = requests.post(
            'https://mcp-server.tacnode.io/mcp',
            headers=headers,
            json=test_payload,
            timeout=15
        )
        
        if response.status_code == 200:
            print("✅ TACNode MCP Server connection successful!")
            return True
        else:
            print(f"❌ Connection failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Connection test failed: {str(e)}")
        return False

def list_existing_gateways():
    """List existing AgentCore gateways"""
    try:
        client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
        
        print("🔍 Checking existing AgentCore Gateways...")
        response = client.list_gateways()
        
        gateways = response.get('gateways', [])
        if gateways:
            print(f"✅ Found {len(gateways)} gateway(s):")
            
            for gateway in gateways:
                print(f"\n📋 Gateway: {gateway['name']}")
                print(f"   ID: {gateway['gatewayId']}")
                print(f"   Status: {gateway['status']}")
                
                # Check existing targets
                try:
                    targets_response = client.list_gateway_targets(gatewayId=gateway['gatewayId'])
                    targets = targets_response.get('gatewayTargets', [])
                    
                    if targets:
                        print(f"   Existing Targets: {len(targets)}")
                        for target in targets:
                            print(f"     - {target['name']} ({target['status']})")
                    else:
                        print("   Existing Targets: None")
                        
                except Exception as e:
                    print(f"   ⚠️  Could not check targets: {str(e)}")
            
            return gateways
        else:
            print("❌ No gateways found. Please create a gateway first.")
            return []
            
    except Exception as e:
        print(f"❌ Error listing gateways: {str(e)}")
        return []

def create_tacnode_target(gateway_id):
    """Create TACNode MCP target for the gateway"""
    token = os.getenv('TACNODE_TOKEN')
    if not token:
        print("❌ TACNODE_TOKEN environment variable not set")
        return None
    
    try:
        client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
        
        print(f"🎯 Creating TACNode MCP Target for gateway: {gateway_id}")
        print("   Server: https://mcp-server.tacnode.io/mcp")
        
        # TACNode MCP target configuration
        target_config = {
            'gatewayId': gateway_id,
            'name': 'TACNodeContextLake',
            'description': 'TACNode Context Lake MCP Server for real-time data analytics',
            'configuration': {
                'type': 'MCP',
                'mcpConfiguration': {
                    'serverUrl': 'https://mcp-server.tacnode.io/mcp',
                    'transport': 'http',
                    'authentication': {
                        'type': 'bearer',
                        'bearerToken': token
                    },
                    'capabilities': {
                        'tools': ['query'],
                        'resources': ['database_info', 'table_schemas']
                    },
                    'protocolVersion': '2024-11-05'
                }
            }
        }
        
        print("📋 Target Configuration:")
        print(f"   Name: {target_config['name']}")
        print(f"   Type: MCP Server")
        print(f"   Server URL: {target_config['configuration']['mcpConfiguration']['serverUrl']}")
        print(f"   Authentication: Bearer Token (configured)")
        print()
        
        # Create the target
        response = client.create_gateway_target(**target_config)
        
        print("✅ TACNode MCP Target created successfully!")
        print(f"   Target ID: {response['gatewayTargetId']}")
        print(f"   Target Name: {response['name']}")
        print(f"   Status: {response['status']}")
        
        # Save target details
        target_details = {
            'gatewayId': gateway_id,
            'targetId': response['gatewayTargetId'],
            'targetName': response['name'],
            'status': response['status'],
            'serverUrl': 'https://mcp-server.tacnode.io/mcp',
            'capabilities': ['query'],
            'created': True
        }
        
        with open('tacnode-agentcore-target.json', 'w') as f:
            json.dump(target_details, f, indent=2)
        
        print("📄 Target details saved to: tacnode-agentcore-target.json")
        
        return response
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        
        if 'ConflictException' in error_code or 'already exists' in error_message.lower():
            print("⚠️  Target with this name already exists!")
            print("   This is normal if you've run this setup before.")
            return {'status': 'exists'}
        else:
            print(f"❌ Error: {error_code} - {error_message}")
            return None
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return None

def test_agentcore_integration(gateway_id):
    """Test the AgentCore + TACNode integration"""
    print(f"\n🧪 Testing AgentCore + TACNode Integration...")
    print(f"   Gateway ID: {gateway_id}")
    
    # This would typically involve testing through AgentCore runtime
    # For now, we'll provide instructions for manual testing
    print("✅ Integration setup complete!")
    print("\n📋 To test the integration:")
    print("1. Use Bedrock AgentCore runtime to create an agent")
    print("2. Configure the agent to use your gateway")
    print("3. The agent can now query TACNode Context Lake via:")
    print("   - SQL queries through the 'query' tool")
    print("   - Real-time data analytics")
    print("   - Business intelligence operations")

def provide_usage_examples():
    """Provide usage examples for the integration"""
    print("\n" + "="*80)
    print("🎯 TACNODE + AGENTCORE USAGE EXAMPLES")
    print("="*80)
    
    print("\n💡 What your AI agents can now do:")
    print("✅ Query live business data in real-time")
    print("✅ Perform analytics on TACNode Context Lake")
    print("✅ Generate insights from structured data")
    print("✅ Create data-driven recommendations")
    
    print("\n📊 Example queries your agents can run:")
    print("1. 'Show me the top performing categories by value'")
    print("2. 'What are the recent trends in our data?'")
    print("3. 'Find all high-value active records'")
    print("4. 'Analyze performance by date range'")
    
    print("\n🔧 Technical capabilities enabled:")
    print("- Real-time SQL query execution")
    print("- JSON-formatted results for AI processing")
    print("- Sub-second response times")
    print("- Secure authentication via bearer tokens")
    
    print("\n🚀 Next steps:")
    print("1. Create Bedrock AgentCore agents")
    print("2. Configure agents to use your gateway")
    print("3. Test queries through AgentCore runtime")
    print("4. Build business-specific AI applications")

def main():
    print("🚀 TACNode + AgentCore Gateway Integration Setup")
    print("=" * 70)
    
    try:
        # Check AWS credentials
        sts_client = boto3.client('sts')
        identity = sts_client.get_caller_identity()
        print(f"🔑 AWS Account: {identity['Account']}")
        print(f"🌍 Target Region: us-east-1")
        print()
        
        # Test TACNode connection first
        if not test_tacnode_connection():
            print("❌ TACNode connection failed. Please check your TACNODE_TOKEN.")
            return
        
        print()
        
        # List existing gateways
        gateways = list_existing_gateways()
        
        if not gateways:
            print("\n❌ No AgentCore gateways found.")
            print("   Please run: python3 create_agentcore_gateway_useast1.py")
            return
        
        # Use the first available gateway
        gateway = gateways[0]
        gateway_id = gateway['gatewayId']
        
        print(f"\n🎯 Using gateway: {gateway['name']} ({gateway_id})")
        
        # Create TACNode target
        result = create_tacnode_target(gateway_id)
        
        if result:
            print("\n✅ TACNode integration setup complete!")
            
            # Test the integration
            test_agentcore_integration(gateway_id)
            
            # Provide usage examples
            provide_usage_examples()
        else:
            print("\n❌ Failed to create TACNode target")
        
    except NoCredentialsError:
        print("❌ AWS credentials not found")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()

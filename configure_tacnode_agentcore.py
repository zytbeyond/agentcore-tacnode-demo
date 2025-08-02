#!/usr/bin/env python3
"""
Configure Tacnode as MCP target for Bedrock AgentCore Gateway
"""

import boto3
import json
import time
import os
from botocore.exceptions import ClientError, NoCredentialsError

def create_tacnode_mcp_target(gateway_id, tacnode_token):
    """Create Tacnode MCP target for AgentCore Gateway"""
    try:
        client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
        
        print("🎯 Creating Tacnode MCP Target for AgentCore Gateway...")
        print(f"   Gateway ID: {gateway_id}")
        print(f"   Tacnode MCP Server: https://mcp-server.tacnode.io/mcp")
        print()
        
        # Tacnode MCP target configuration
        target_config = {
            'gatewayId': gateway_id,
            'name': 'TacnodeMCPServer',
            'description': 'Tacnode Managed MCP Server for enterprise AI database operations',
            'configuration': {
                'type': 'MCP',
                'mcpConfiguration': {
                    'serverUrl': 'https://mcp-server.tacnode.io/mcp',
                    'transport': 'http',
                    'authentication': {
                        'type': 'bearer',
                        'bearerToken': tacnode_token
                    },
                    'capabilities': {
                        'tools': ['query'],
                        'resources': ['schemas', 'tables_in_schema', 'table_structure_in_schema', 'indexes_in_table', 'procedures_in_schema']
                    }
                }
            }
        }
        
        print("📋 Target Configuration:")
        print(f"   Name: {target_config['name']}")
        print(f"   Type: MCP Server")
        print(f"   Server URL: {target_config['configuration']['mcpConfiguration']['serverUrl']}")
        print(f"   Authentication: Bearer Token")
        print()
        
        # Create the target
        response = client.create_gateway_target(**target_config)
        
        print("✅ Tacnode MCP Target created successfully!")
        print(f"   Target ID: {response['gatewayTargetId']}")
        print(f"   Target Name: {response['name']}")
        print(f"   Status: {response['status']}")
        
        return response
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        
        print(f"❌ Error: {error_code} - {error_message}")
        return None
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return None

def test_tacnode_mcp_connection(tacnode_token):
    """Test connection to Tacnode MCP server"""
    try:
        import requests
        
        print("🧪 Testing Tacnode MCP Server connection...")
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream',
            'Authorization': f'Bearer {tacnode_token}'
        }
        
        # Test tools/list endpoint
        test_payload = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 1
        }
        
        response = requests.post(
            'https://mcp-server.tacnode.io/mcp',
            headers=headers,
            json=test_payload,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Tacnode MCP Server connection successful!")
            return True
        else:
            print(f"❌ Connection failed: HTTP {response.status_code}")
            return False
            
    except ImportError:
        print("⚠️  requests library not available, skipping connection test")
        return True
    except Exception as e:
        print(f"❌ Connection test failed: {str(e)}")
        return False

def discover_existing_gateways():
    """Discover existing AgentCore gateways"""
    try:
        client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
        
        print("🔍 Discovering existing AgentCore Gateways...")
        response = client.list_gateways()
        
        gateways = response.get('gateways', [])
        if gateways:
            print(f"✅ Found {len(gateways)} gateway(s):")
            
            for gateway in gateways:
                print(f"\n📋 Gateway: {gateway['name']}")
                print(f"   ID: {gateway['gatewayId']}")
                print(f"   Status: {gateway['status']}")
            
            return gateways
        else:
            print("❌ No gateways found")
            return []
            
    except Exception as e:
        print(f"❌ Error discovering gateways: {str(e)}")
        return []

def provide_manual_setup_instructions():
    """Provide manual setup instructions"""
    print("\n" + "="*80)
    print("🎯 TACNODE + AGENTCORE MANUAL SETUP INSTRUCTIONS")
    print("="*80)
    
    print("\n📋 Prerequisites:")
    print("1. ✅ AgentCore Gateway created")
    print("2. ✅ Tacnode Data Cloud and Nodegroup set up")
    print("3. ✅ Tacnode MCP Token generated")
    
    print("\n🔧 Manual Setup Steps:")
    print("1. Go to AWS Bedrock Console → AgentCore → Gateways")
    print("2. Select your gateway")
    print("3. Add Target:")
    print("   - Target Name: TacnodeMCPServer")
    print("   - Target Type: MCP Server")
    print("   - Server URL: https://mcp-server.tacnode.io/mcp")
    print("   - Authentication: Bearer Token")
    print("   - Token: [Your Tacnode MCP Token]")
    
    print("\n🎯 Expected Capabilities:")
    print("   Tools: query (Execute read-only SQL queries)")
    print("   Resources: schemas, tables, table_structure, indexes, procedures")
    
    print("\n💡 Benefits of Tacnode Integration:")
    print("   ✅ Vector embeddings for semantic search")
    print("   ✅ Graph relationships for context understanding")
    print("   ✅ Real-time analytics and performance optimization")
    print("   ✅ Sub-second query performance")
    print("   ✅ Multi-modal data integration")

def main():
    print("🚀 Tacnode + AgentCore Integration Setup")
    print("=" * 60)
    
    try:
        # Check AWS credentials
        sts_client = boto3.client('sts')
        identity = sts_client.get_caller_identity()
        print(f"🔑 AWS Account: {identity['Account']}")
        print(f"🌍 Target Region: us-east-1")
        print()
        
        # Get Tacnode token
        tacnode_token = os.getenv('TACNODE_MCP_TOKEN')
        if not tacnode_token:
            print("⚠️  TACNODE_MCP_TOKEN environment variable not set")
            print("   To get your token:")
            print("   1. Go to Tacnode Console → Nodegroup → MCP Tokens")
            print("   2. Create Token for your target database")
            print("   3. Copy the token")
            print()
            tacnode_token = input("Enter your Tacnode MCP token (or press Enter to skip): ").strip()
        
        if tacnode_token:
            # Test Tacnode connection
            test_tacnode_mcp_connection(tacnode_token)
            print()
        
        # Discover existing gateways
        gateways = discover_existing_gateways()
        
        if gateways and tacnode_token:
            # Try to create Tacnode target for the first gateway
            gateway_id = gateways[0]['gatewayId']
            print(f"\n🎯 Attempting to add Tacnode target to gateway: {gateway_id}")
            
            result = create_tacnode_mcp_target(gateway_id, tacnode_token)
            
            if result:
                print("\n✅ Tacnode integration setup complete!")
                print("   Your AgentCore Gateway now has access to Tacnode's AI database capabilities")
            else:
                print("\n⚠️  Automated setup failed, please use manual setup instructions")
        
        # Always provide manual instructions
        provide_manual_setup_instructions()
        
    except NoCredentialsError:
        print("❌ AWS credentials not found")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()

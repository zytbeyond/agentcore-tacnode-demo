#!/usr/bin/env python3
"""
Check existing AgentCore gateways and their configuration
"""

import boto3
import json
from botocore.exceptions import ClientError, NoCredentialsError

def list_gateways():
    """List all existing gateways"""
    try:
        client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
        
        print("🔍 Checking AgentCore Gateways in us-east-1...")
        response = client.list_gateways()
        
        gateways = response.get('gateways', [])
        if gateways:
            print(f"✅ Found {len(gateways)} gateway(s):")
            
            for gateway in gateways:
                print(f"\n📋 Gateway: {gateway['name']}")
                print(f"   ID: {gateway['gatewayId']}")
                print(f"   Status: {gateway['status']}")
                print(f"   Protocol: {gateway.get('protocolType', 'Unknown')}")
                
                # Get detailed gateway info
                try:
                    detail_response = client.get_gateway(gatewayId=gateway['gatewayId'])
                    detail = detail_response
                    
                    print(f"   Description: {detail.get('description', 'N/A')}")
                    print(f"   Role ARN: {detail.get('roleArn', 'N/A')}")
                    
                    if 'protocolConfiguration' in detail:
                        protocol_config = detail['protocolConfiguration']
                        if 'mcp' in protocol_config:
                            mcp_config = protocol_config['mcp']
                            print(f"   MCP Versions: {mcp_config.get('supportedVersions', [])}")
                            print(f"   Instructions: {mcp_config.get('instructions', 'N/A')[:100]}...")
                    
                    # Check targets
                    try:
                        targets_response = client.list_gateway_targets(gatewayId=gateway['gatewayId'])
                        targets = targets_response.get('gatewayTargets', [])
                        
                        if targets:
                            print(f"   Targets: {len(targets)} configured")
                            for target in targets:
                                print(f"     - {target['name']} ({target['status']})")
                        else:
                            print("   Targets: None configured")
                            
                    except Exception as e:
                        print(f"   ⚠️  Could not check targets: {str(e)}")
                        
                except Exception as e:
                    print(f"   ⚠️  Could not get gateway details: {str(e)}")
            
            return gateways
        else:
            print("📋 No gateways found")
            return []
            
    except Exception as e:
        print(f"❌ Error listing gateways: {str(e)}")
        return []

def check_service_roles():
    """Check available service roles"""
    try:
        iam_client = boto3.client('iam', region_name='us-east-1')
        
        print("\n🔍 Checking available service roles...")
        
        # Look for AgentCore related roles
        response = iam_client.list_roles()
        agentcore_roles = []
        
        for role in response['Roles']:
            if 'AgentCore' in role['RoleName'] or 'agentcore' in role['RoleName'].lower():
                agentcore_roles.append(role)
                print(f"✅ Found role: {role['RoleName']}")
                print(f"   ARN: {role['Arn']}")
        
        if not agentcore_roles:
            print("⚠️  No AgentCore service roles found")
            
        return agentcore_roles
        
    except Exception as e:
        print(f"❌ Error checking service roles: {str(e)}")
        return []

def check_bedrock_agentcore_availability():
    """Check if Bedrock AgentCore is available in the region"""
    try:
        client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
        
        print("\n🔍 Testing Bedrock AgentCore service availability...")
        
        # Try to list gateways to test service availability
        response = client.list_gateways()
        print("✅ Bedrock AgentCore service is available in us-east-1")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'UnauthorizedOperation':
            print("⚠️  Service available but insufficient permissions")
            print("   Required permissions: bedrock-agentcore:ListGateways")
        else:
            print(f"❌ Service error: {error_code}")
        return False
    except Exception as e:
        print(f"❌ Service not available: {str(e)}")
        return False

def provide_next_steps(gateways):
    """Provide next steps based on current state"""
    print("\n" + "="*60)
    print("🎯 NEXT STEPS")
    print("="*60)
    
    if gateways:
        print("\n✅ You have existing gateways!")
        print("   You can proceed to add TACNode as a target:")
        print("   python3 setup_tacnode_agentcore_gateway.py")
        
        # Check if any gateway already has TACNode target
        print("\n💡 To add TACNode target manually:")
        print("1. Go to AWS Bedrock Console → AgentCore → Gateways")
        print("2. Select a gateway")
        print("3. Add Target:")
        print("   - Name: TACNodeContextLake")
        print("   - Type: MCP Server")
        print("   - URL: https://mcp-server.tacnode.io/mcp")
        print("   - Auth: Bearer token (use TACNODE_TOKEN)")
    else:
        print("\n❌ No gateways found")
        print("   You need to create a gateway first.")
        print("   This might require:")
        print("   1. Proper IAM permissions")
        print("   2. Service role configuration")
        print("   3. Manual creation via AWS Console")
        
        print("\n🔧 Manual Gateway Creation:")
        print("1. Go to AWS Bedrock Console → AgentCore → Gateways")
        print("2. Create Gateway:")
        print("   - Name: TACNodeContextLakeGateway")
        print("   - Protocol: MCP")
        print("   - Version: 2025-03-26")
        print("   - Service Role: AmazonBedrockAgentCoreGatewayDefaultServiceRole*")

def main():
    print("🚀 AgentCore Gateway Status Check")
    print("=" * 60)
    
    try:
        # Check AWS credentials
        sts_client = boto3.client('sts')
        identity = sts_client.get_caller_identity()
        print(f"🔑 AWS Account: {identity['Account']}")
        print(f"🔑 User/Role: {identity['Arn']}")
        print(f"🌍 Target Region: us-east-1")
        
        # Check service availability
        service_available = check_bedrock_agentcore_availability()
        
        if service_available:
            # List existing gateways
            gateways = list_gateways()
            
            # Check service roles
            check_service_roles()
            
            # Provide next steps
            provide_next_steps(gateways)
        else:
            print("\n❌ Cannot proceed - Bedrock AgentCore service not available")
        
    except NoCredentialsError:
        print("❌ AWS credentials not found")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()

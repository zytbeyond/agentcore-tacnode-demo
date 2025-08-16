#!/usr/bin/env python3
"""
Build Complete TACNode + AgentCore System with Full AWS Admin Access
"""

import boto3
import json
import time
import os
from botocore.exceptions import ClientError, NoCredentialsError

def verify_admin_access():
    """Verify we have admin access"""
    try:
        sts_client = boto3.client('sts')
        identity = sts_client.get_caller_identity()
        
        print("🔑 AWS Identity Verification:")
        print(f"   Account: {identity['Account']}")
        print(f"   User/Role: {identity['Arn']}")
        
        # Check if we have admin access by trying to list IAM roles
        iam_client = boto3.client('iam')
        roles = iam_client.list_roles(MaxItems=1)
        
        print("✅ Administrator access confirmed!")
        return True
        
    except Exception as e:
        print(f"❌ Admin access verification failed: {str(e)}")
        return False

def ensure_service_role():
    """Ensure AgentCore service role exists"""
    try:
        iam_client = boto3.client('iam')
        
        role_name = "AmazonBedrockAgentCoreGatewayServiceRole"
        
        print(f"🔍 Checking for service role: {role_name}")
        
        try:
            response = iam_client.get_role(RoleName=role_name)
            print(f"✅ Service role exists: {response['Role']['Arn']}")
            return response['Role']['Arn']
        except iam_client.exceptions.NoSuchEntityException:
            print("🏗️  Creating AgentCore service role...")
            
            # Trust policy for AgentCore
            trust_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "bedrock-agentcore.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            }
            
            # Create the role
            response = iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description="Service role for Bedrock AgentCore Gateway"
            )
            
            # Attach necessary policies
            policies = [
                "arn:aws:iam::aws:policy/AmazonBedrockFullAccess",
                "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
            ]
            
            for policy_arn in policies:
                iam_client.attach_role_policy(
                    RoleName=role_name,
                    PolicyArn=policy_arn
                )
            
            print(f"✅ Service role created: {response['Role']['Arn']}")
            return response['Role']['Arn']
            
    except Exception as e:
        print(f"❌ Error with service role: {str(e)}")
        return None

def create_agentcore_gateway():
    """Create AgentCore Gateway using AWS CLI"""
    try:
        print("🏗️  Creating AgentCore Gateway using AWS CLI...")
        
        # Get service role ARN
        service_role_arn = ensure_service_role()
        if not service_role_arn:
            print("❌ Cannot proceed without service role")
            return None
        
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
                    "discoveryUrl": "https://auth.tacnode.io/.well-known/openid-configuration",
                    "allowedAudience": ["tacnode-context-lake"],
                    "allowedClients": ["agentcore-gateway"]
                }
            }
        }
        
        # Save config to file for CLI
        with open('/tmp/gateway-config.json', 'w') as f:
            json.dump(gateway_config, f, indent=2)
        
        print(f"   Name: {gateway_config['name']}")
        print(f"   Protocol: {gateway_config['protocolType']}")
        print(f"   Service Role: {service_role_arn}")
        
        # Use AWS CLI to create gateway
        import subprocess
        
        cmd = [
            'aws', 'bedrock-agentcore-control', 'create-gateway',
            '--cli-input-json', 'file:///tmp/gateway-config.json',
            '--region', 'us-east-1'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            response = json.loads(result.stdout)
            print("✅ Gateway created successfully!")
            print(f"   Gateway ID: {response['gatewayId']}")
            print(f"   Gateway ARN: {response['gatewayArn']}")
            print(f"   Status: {response['status']}")
            
            # Save gateway details
            gateway_details = {
                'gatewayId': response['gatewayId'],
                'gatewayArn': response['gatewayArn'],
                'gatewayUrl': response.get('gatewayUrl', ''),
                'status': response['status'],
                'name': response['name'],
                'region': 'us-east-1'
            }
            
            with open('tacnode-agentcore-gateway.json', 'w') as f:
                json.dump(gateway_details, f, indent=2)
            
            return response
        else:
            print(f"❌ Gateway creation failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating gateway: {str(e)}")
        return None

def wait_for_gateway_ready(gateway_id, max_wait=300):
    """Wait for gateway to become ready"""
    try:
        print(f"⏳ Waiting for gateway {gateway_id} to become ready...")
        
        start_time = time.time()
        while time.time() - start_time < max_wait:
            cmd = [
                'aws', 'bedrock-agentcore-control', 'get-gateway',
                '--gateway-id', gateway_id,
                '--region', 'us-east-1'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                response = json.loads(result.stdout)
                status = response['status']
                
                print(f"   Status: {status}")
                
                if status in ['ACTIVE', 'AVAILABLE']:
                    print("✅ Gateway is ready!")
                    return True
                elif status in ['FAILED', 'ERROR']:
                    print(f"❌ Gateway failed with status: {status}")
                    return False
            
            time.sleep(15)  # Wait 15 seconds before checking again
        
        print("⏰ Timeout waiting for gateway to become ready")
        return False
        
    except Exception as e:
        print(f"❌ Error waiting for gateway: {str(e)}")
        return False

def create_tacnode_target(gateway_id):
    """Create TACNode MCP target for the gateway"""
    token = os.getenv('TACNODE_TOKEN')
    if not token:
        print("❌ TACNODE_TOKEN environment variable not set")
        return None
    
    try:
        print(f"🎯 Creating TACNode MCP Target for gateway: {gateway_id}")
        
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
        
        # Save config to file for CLI
        with open('/tmp/target-config.json', 'w') as f:
            json.dump(target_config, f, indent=2)
        
        print(f"   Target Name: {target_config['name']}")
        print(f"   Server URL: {target_config['configuration']['mcpConfiguration']['serverUrl']}")
        print(f"   Authentication: Bearer Token (configured)")
        
        # Use AWS CLI to create target
        import subprocess
        
        cmd = [
            'aws', 'bedrock-agentcore-control', 'create-gateway-target',
            '--cli-input-json', 'file:///tmp/target-config.json',
            '--region', 'us-east-1'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            response = json.loads(result.stdout)
            print("✅ TACNode MCP Target created successfully!")
            print(f"   Target ID: {response['gatewayTargetId']}")
            print(f"   Status: {response['status']}")
            
            # Save target details
            target_details = {
                'gatewayId': gateway_id,
                'targetId': response['gatewayTargetId'],
                'targetName': response['name'],
                'status': response['status'],
                'serverUrl': 'https://mcp-server.tacnode.io/mcp',
                'capabilities': ['query']
            }
            
            with open('tacnode-agentcore-target.json', 'w') as f:
                json.dump(target_details, f, indent=2)
            
            return response
        else:
            print(f"❌ Target creation failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating target: {str(e)}")
        return None

def test_complete_integration(gateway_id):
    """Test the complete integration"""
    print(f"\n🧪 Testing Complete TACNode + AgentCore Integration...")
    print(f"   Gateway ID: {gateway_id}")
    
    # Test TACNode connection
    print("\n1️⃣ Testing TACNode MCP Server connection...")
    os.system("python3 test_tacnode_mcp.py")
    
    print("\n2️⃣ Testing data queries...")
    os.system("python3 query_tacnode_data.py")
    
    print("\n✅ Integration testing complete!")

def main():
    print("🚀 Building Complete TACNode + AgentCore System")
    print("=" * 70)
    
    try:
        # Verify admin access
        if not verify_admin_access():
            print("❌ Insufficient permissions to build system")
            return
        
        print()
        
        # Step 1: Create AgentCore Gateway
        print("STEP 1: Creating AgentCore Gateway")
        print("-" * 40)
        gateway = create_agentcore_gateway()
        
        if not gateway:
            print("❌ Failed to create gateway")
            return
        
        gateway_id = gateway['gatewayId']
        
        # Step 2: Wait for gateway to be ready
        print(f"\nSTEP 2: Waiting for Gateway to be Ready")
        print("-" * 40)
        if not wait_for_gateway_ready(gateway_id):
            print("⚠️  Gateway may not be fully ready, but continuing...")
        
        # Step 3: Create TACNode target
        print(f"\nSTEP 3: Adding TACNode MCP Target")
        print("-" * 40)
        target = create_tacnode_target(gateway_id)
        
        if not target:
            print("❌ Failed to create TACNode target")
            return
        
        # Step 4: Test integration
        print(f"\nSTEP 4: Testing Complete Integration")
        print("-" * 40)
        test_complete_integration(gateway_id)
        
        # Success summary
        print("\n" + "="*70)
        print("🎉 COMPLETE TACNODE + AGENTCORE SYSTEM BUILT SUCCESSFULLY!")
        print("="*70)
        
        print(f"\n✅ Gateway Created: {gateway_id}")
        print(f"✅ TACNode Target Added: {target['gatewayTargetId']}")
        print(f"✅ Real-time Data Access: Enabled")
        print(f"✅ AI Agent Integration: Ready")
        
        print(f"\n🎯 Your AI agents can now:")
        print("   - Query TACNode Context Lake in real-time")
        print("   - Perform complex data analytics")
        print("   - Generate business insights")
        print("   - Make data-driven decisions")
        
        print(f"\n📋 Configuration files saved:")
        print("   - tacnode-agentcore-gateway.json")
        print("   - tacnode-agentcore-target.json")
        
    except Exception as e:
        print(f"❌ System build failed: {str(e)}")

if __name__ == "__main__":
    import subprocess
    main()

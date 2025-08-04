#!/usr/bin/env python3
"""
Create AgentCore Gateway specifically for TACNode integration
"""

import boto3
import json
import time
from botocore.exceptions import ClientError, NoCredentialsError

def create_tacnode_agentcore_gateway():
    """Create AgentCore Gateway for TACNode integration"""
    try:
        client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
        
        # Use the existing service role
        service_role_arn = "arn:aws:iam::560155322832:role/service-role/AmazonBedrockAgentCoreGatewayDefaultServiceRole1754124199105"
        
        print("🏗️  Creating TACNode AgentCore Gateway in us-east-1...")
        print(f"   Using service role: {service_role_arn}")
        
        # Gateway configuration for TACNode
        gateway_config = {
            'name': 'TACNodeContextLakeGateway',
            'description': 'AgentCore Gateway for TACNode Context Lake real-time data access',
            'roleArn': service_role_arn,
            'protocolType': 'MCP',
            'protocolConfiguration': {
                'mcp': {
                    'supportedVersions': ['2025-03-26'],
                    'instructions': 'Gateway for connecting Bedrock AgentCore to TACNode Context Lake for real-time data analytics and AI-driven insights',
                    'searchType': 'SEMANTIC'
                }
            }
        }
        
        print(f"   Name: {gateway_config['name']}")
        print(f"   Protocol: {gateway_config['protocolType']}")
        print(f"   MCP Version: {gateway_config['protocolConfiguration']['mcp']['supportedVersions'][0]}")
        print()
        
        # Create the gateway
        response = client.create_gateway(**gateway_config)
        
        print("✅ TACNode Gateway created successfully!")
        print(f"   Gateway ID: {response['gatewayId']}")
        print(f"   Gateway ARN: {response['gatewayArn']}")
        print(f"   Gateway URL: {response['gatewayUrl']}")
        print(f"   Status: {response['status']}")
        print()
        
        # Save gateway details
        gateway_details = {
            'gatewayId': response['gatewayId'],
            'gatewayArn': response['gatewayArn'],
            'gatewayUrl': response['gatewayUrl'],
            'status': response['status'],
            'name': response['name'],
            'description': response['description'],
            'region': 'us-east-1',
            'purpose': 'TACNode Context Lake Integration'
        }
        
        with open('tacnode-agentcore-gateway.json', 'w') as f:
            json.dump(gateway_details, f, indent=2)
        
        print("📄 Gateway details saved to: tacnode-agentcore-gateway.json")
        
        return response
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        
        if error_code == 'ConflictException':
            print("⚠️  Gateway with this name already exists!")
            print("   Checking existing gateways...")
            return check_existing_gateways()
        elif error_code == 'UnauthorizedOperation':
            print("❌ Error: Insufficient permissions to create AgentCore Gateway")
            print("   Required permissions: bedrock-agentcore:CreateGateway")
        else:
            print(f"❌ Error: {error_code} - {error_message}")
        
        return None
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return None

def check_existing_gateways():
    """Check for existing gateways"""
    try:
        client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
        
        print("🔍 Checking existing gateways...")
        response = client.list_gateways()
        
        gateways = response.get('gateways', [])
        if gateways:
            print(f"✅ Found {len(gateways)} existing gateway(s):")
            
            for gateway in gateways:
                print(f"\n📋 Gateway: {gateway['name']}")
                print(f"   ID: {gateway['gatewayId']}")
                print(f"   Status: {gateway['status']}")
                
                # Return the first gateway for use
                if gateway['status'] in ['ACTIVE', 'AVAILABLE']:
                    return gateway
            
            return gateways[0] if gateways else None
        else:
            print("📋 No existing gateways found")
            return None
            
    except Exception as e:
        print(f"❌ Error checking gateways: {str(e)}")
        return None

def wait_for_gateway_ready(gateway_id, max_wait=300):
    """Wait for gateway to become ready"""
    try:
        client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
        
        print(f"⏳ Waiting for gateway {gateway_id} to become ready...")
        
        start_time = time.time()
        while time.time() - start_time < max_wait:
            try:
                response = client.get_gateway(gatewayId=gateway_id)
                status = response['status']
                
                print(f"   Status: {status}")
                
                if status in ['ACTIVE', 'AVAILABLE']:
                    print("✅ Gateway is ready!")
                    return True
                elif status in ['FAILED', 'ERROR']:
                    print(f"❌ Gateway failed with status: {status}")
                    return False
                
                time.sleep(10)  # Wait 10 seconds before checking again
                
            except Exception as e:
                print(f"   Error checking status: {str(e)}")
                time.sleep(10)
        
        print("⏰ Timeout waiting for gateway to become ready")
        return False
        
    except Exception as e:
        print(f"❌ Error waiting for gateway: {str(e)}")
        return False

def main():
    print("🚀 TACNode AgentCore Gateway Creator")
    print("=" * 60)
    
    try:
        # Check AWS credentials
        sts_client = boto3.client('sts')
        identity = sts_client.get_caller_identity()
        print(f"🔑 AWS Account: {identity['Account']}")
        print(f"🔑 User/Role: {identity['Arn']}")
        print(f"🌍 Target Region: us-east-1")
        print()
        
        # Create or check gateway
        gateway = create_tacnode_agentcore_gateway()
        
        if gateway:
            gateway_id = gateway.get('gatewayId')
            if gateway_id:
                # Wait for gateway to be ready
                if wait_for_gateway_ready(gateway_id):
                    print(f"\n✅ Gateway {gateway_id} is ready for TACNode integration!")
                    print("\n🎯 Next step: Run the TACNode target setup:")
                    print("   python3 setup_tacnode_agentcore_gateway.py")
                else:
                    print(f"\n⚠️  Gateway may not be fully ready yet. You can check status later.")
            else:
                print("\n✅ Using existing gateway for TACNode integration")
                print("\n🎯 Next step: Run the TACNode target setup:")
                print("   python3 setup_tacnode_agentcore_gateway.py")
        else:
            print("\n❌ Failed to create or find gateway")
        
    except NoCredentialsError:
        print("❌ AWS credentials not found")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()

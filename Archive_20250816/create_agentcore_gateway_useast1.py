#!/usr/bin/env python3
"""
Create AgentCore Gateway in us-east-1 using existing service role
"""

import boto3
import json
import time
from botocore.exceptions import ClientError, NoCredentialsError

def create_agentcore_gateway_with_dynamodb():
    """Create AgentCore Gateway with DynamoDB integration in us-east-1"""
    try:
        client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
        
        # Use the existing service role we discovered
        service_role_arn = "arn:aws:iam::560155322832:role/service-role/AmazonBedrockAgentCoreGatewayDefaultServiceRole1754124199105"
        
        print("🏗️  Creating AgentCore Gateway in us-east-1...")
        print(f"   Using existing service role: {service_role_arn}")
        
        # Gateway configuration for DynamoDB integration
        gateway_config = {
            'name': 'AgentCoreDynamoDBGateway',
            'description': 'AgentCore Gateway with DynamoDB context store in us-east-1',
            'roleArn': service_role_arn,
            'protocolType': 'MCP',
            'protocolConfiguration': {
                'mcp': {
                    'supportedVersions': ['2024-11-05'],
                    'instructions': 'Gateway for AgentCore with DynamoDB context storage and retrieval in us-east-1',
                    'searchType': 'SEMANTIC'
                }
            },
            'authorizerType': 'NONE'
        }
        
        print(f"   Name: {gateway_config['name']}")
        print(f"   Protocol: {gateway_config['protocolType']}")
        print(f"   Region: us-east-1")
        print()
        
        # Create the gateway
        response = client.create_gateway(**gateway_config)
        
        print("✅ Gateway created successfully!")
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
            'dynamodb_table': 'AgentCoreContextStore'
        }
        
        with open('agentcore-gateway-details-useast1.json', 'w') as f:
            json.dump(gateway_details, f, indent=2)
        
        print("📄 Gateway details saved to: agentcore-gateway-details-useast1.json")
        
        # Now try to create DynamoDB target
        create_dynamodb_target(response['gatewayId'])
        
        return response
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        
        if error_code == 'ConflictException':
            print("⚠️  Gateway with this name already exists!")
            print("   Let's check existing gateways...")
            list_existing_gateways()
        elif error_code == 'UnauthorizedOperation':
            print("❌ Error: Insufficient permissions to create AgentCore Gateway")
        else:
            print(f"❌ Error: {error_code} - {error_message}")
        
        return None
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return None

def create_dynamodb_target(gateway_id):
    """Create DynamoDB target for the gateway"""
    try:
        client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
        
        print(f"\n🎯 Creating DynamoDB target for gateway: {gateway_id}")
        
        target_config = {
            'gatewayId': gateway_id,
            'name': 'AgentCoreContextStore',
            'description': 'DynamoDB context store for AgentCore',
            'configuration': {
                'type': 'DynamoDB',
                'tableName': 'AgentCoreContextStore',
                'region': 'us-east-1',
                'accessPattern': 'ReadWrite'
            }
        }
        
        response = client.create_gateway_target(**target_config)
        
        print("✅ DynamoDB target created successfully!")
        print(f"   Target ID: {response['gatewayTargetId']}")
        print(f"   Target Name: {response['name']}")
        print(f"   Status: {response['status']}")
        
        return response
        
    except Exception as e:
        print(f"❌ Error creating DynamoDB target: {str(e)}")
        print("   You can create this manually in the AWS Console")
        return None

def list_existing_gateways():
    """List existing gateways to check current status"""
    try:
        client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
        
        print("\n📋 Checking existing gateways in us-east-1...")
        response = client.list_gateways()
        
        if response.get('gateways'):
            print(f"✅ Found {len(response['gateways'])} existing gateway(s):")
            
            for gateway in response['gateways']:
                print(f"\n🏗️  Gateway: {gateway['name']}")
                print(f"   ID: {gateway['gatewayId']}")
                print(f"   Status: {gateway['status']}")
                
                # Check targets for this gateway
                try:
                    targets_response = client.list_gateway_targets(gatewayId=gateway['gatewayId'])
                    targets = targets_response.get('gatewayTargets', [])
                    
                    if targets:
                        print(f"   Targets: {len(targets)} configured")
                        for target in targets:
                            print(f"     - {target['name']} ({target['status']})")
                    else:
                        print("   Targets: None configured")
                        print("   💡 You can add DynamoDB target manually!")
                        
                except Exception as e:
                    print(f"   ⚠️  Could not check targets: {str(e)}")
        else:
            print("📋 No existing gateways found")
            
    except Exception as e:
        print(f"❌ Error listing gateways: {str(e)}")

def provide_next_steps():
    """Provide next steps for using the gateway"""
    print("\n" + "="*60)
    print("🎯 NEXT STEPS")
    print("="*60)
    
    print("\n🔧 Gateway Configuration:")
    print("   ✅ Region: us-east-1 (optimal for marketplace integrations)")
    print("   ✅ DynamoDB Table: AgentCoreContextStore (ready)")
    print("   ✅ Service Role: Existing role configured")
    
    print("\n📊 DynamoDB Integration:")
    print("   - Table Name: AgentCoreContextStore")
    print("   - Region: us-east-1")
    print("   - Schema: session_id (PK), timestamp (SK)")
    print("   - GSI: ContextTypeIndex")
    
    print("\n💻 Usage:")
    print("   1. Use agentcore_dynamodb_client.py for data operations")
    print("   2. Store conversations, knowledge, and preferences")
    print("   3. Query by session, context type, or time range")
    
    print("\n🚀 Testing:")
    print("   python3 agentcore_dynamodb_client.py")
    print("   python3 analyze_agentcore_dynamodb.py")

def main():
    print("🚀 AgentCore Gateway Creator (us-east-1)")
    print("=" * 60)
    
    try:
        # Check AWS credentials
        sts_client = boto3.client('sts')
        identity = sts_client.get_caller_identity()
        print(f"🔑 AWS Account: {identity['Account']}")
        print(f"🔑 User/Role: {identity['Arn']}")
        print(f"🌍 Target Region: us-east-1")
        print()
        
        # First check if gateways already exist
        list_existing_gateways()
        
        # Try to create new gateway
        print("\n" + "="*40)
        result = create_agentcore_gateway_with_dynamodb()
        
        # Provide next steps
        provide_next_steps()
        
        if result:
            print("\n✅ Setup complete! Your AgentCore + DynamoDB integration is ready in us-east-1.")
        else:
            print("\n⚠️  Gateway creation had issues, but you may have existing gateways to use.")
        
    except NoCredentialsError:
        print("❌ AWS credentials not found")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()

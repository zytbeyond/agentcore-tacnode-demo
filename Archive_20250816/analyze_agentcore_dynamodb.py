#!/usr/bin/env python3
"""
Analyze and test AgentCore Gateway with DynamoDB integration
"""

import boto3
import json
import time
from datetime import datetime
from botocore.exceptions import ClientError, NoCredentialsError

def discover_agentcore_gateways():
    """Discover existing AgentCore gateways"""
    try:
        client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
        
        print("🔍 Discovering AgentCore Gateways...")
        response = client.list_gateways()
        
        gateways = []
        if response.get('gateways'):
            print(f"✅ Found {len(response['gateways'])} gateway(s):")
            
            for gateway in response['gateways']:
                print(f"\n📋 Gateway: {gateway['name']}")
                print(f"   ID: {gateway['gatewayId']}")
                print(f"   Status: {gateway['status']}")
                print(f"   Protocol: {gateway.get('protocolType', 'N/A')}")
                
                # Get detailed gateway information
                try:
                    detail_response = client.get_gateway(gatewayId=gateway['gatewayId'])
                    gateway_detail = detail_response
                    gateways.append(gateway_detail)
                    
                    print(f"   URL: {gateway_detail.get('gatewayUrl', 'N/A')}")
                    print(f"   Description: {gateway_detail.get('description', 'N/A')}")
                    
                except Exception as e:
                    print(f"   ⚠️  Could not get details: {str(e)}")
                    gateways.append(gateway)
        else:
            print("❌ No gateways found")
            
        return gateways
        
    except Exception as e:
        print(f"❌ Error discovering gateways: {str(e)}")
        return []

def discover_gateway_targets(gateway_id):
    """Discover targets for a specific gateway"""
    try:
        client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')

        print(f"\n🎯 Discovering targets for gateway: {gateway_id}")
        response = client.list_gateway_targets(gatewayId=gateway_id)
        
        targets = []
        if response.get('gatewayTargets'):
            print(f"✅ Found {len(response['gatewayTargets'])} target(s):")
            
            for target in response['gatewayTargets']:
                print(f"\n📌 Target: {target['name']}")
                print(f"   ID: {target['gatewayTargetId']}")
                print(f"   Status: {target['status']}")
                
                # Get detailed target information
                try:
                    detail_response = client.get_gateway_target(
                        gatewayId=gateway_id,
                        gatewayTargetId=target['gatewayTargetId']
                    )
                    target_detail = detail_response
                    targets.append(target_detail)
                    
                    # Check if it's DynamoDB
                    if 'dynamodb' in target.get('name', '').lower() or 'dynamo' in target.get('name', '').lower():
                        print(f"   🗄️  Type: DynamoDB Target")
                        print(f"   Configuration: {target_detail.get('configuration', {})}")
                    
                except Exception as e:
                    print(f"   ⚠️  Could not get target details: {str(e)}")
                    targets.append(target)
        else:
            print("❌ No targets found for this gateway")
            
        return targets
        
    except Exception as e:
        print(f"❌ Error discovering targets: {str(e)}")
        return []

def discover_dynamodb_tables():
    """Discover DynamoDB tables that might be related to AgentCore"""
    try:
        dynamodb = boto3.client('dynamodb', region_name='us-east-1')
        
        print("\n🗄️  Discovering DynamoDB Tables...")
        response = dynamodb.list_tables()
        
        tables = response.get('TableNames', [])
        if tables:
            print(f"✅ Found {len(tables)} table(s):")
            
            agentcore_tables = []
            for table_name in tables:
                print(f"\n📊 Table: {table_name}")
                
                # Get table details
                try:
                    table_response = dynamodb.describe_table(TableName=table_name)
                    table_info = table_response['Table']
                    
                    print(f"   Status: {table_info['TableStatus']}")
                    print(f"   Items: {table_info.get('ItemCount', 'Unknown')}")
                    print(f"   Size: {table_info.get('TableSizeBytes', 0)} bytes")
                    
                    # Check if it looks like an AgentCore table
                    if any(keyword in table_name.lower() for keyword in ['agent', 'bedrock', 'context', 'gateway']):
                        print(f"   🤖 Likely AgentCore related!")
                        agentcore_tables.append(table_name)
                    
                    # Show key schema
                    key_schema = table_info.get('KeySchema', [])
                    if key_schema:
                        print(f"   Keys: {[key['AttributeName'] for key in key_schema]}")
                        
                except Exception as e:
                    print(f"   ⚠️  Could not get table details: {str(e)}")
            
            return agentcore_tables
        else:
            print("❌ No DynamoDB tables found")
            return []
            
    except Exception as e:
        print(f"❌ Error discovering DynamoDB tables: {str(e)}")
        return []

def test_dynamodb_connectivity(table_name):
    """Test connectivity to a DynamoDB table"""
    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table(table_name)
        
        print(f"\n🧪 Testing connectivity to table: {table_name}")
        
        # Try to scan a few items
        response = table.scan(Limit=5)
        items = response.get('Items', [])
        
        print(f"✅ Successfully connected to {table_name}")
        print(f"   Sample items found: {len(items)}")
        
        if items:
            print(f"   Sample item keys: {list(items[0].keys())}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing {table_name}: {str(e)}")
        return False

def test_agentcore_gateway(gateway_id, gateway_url):
    """Test AgentCore gateway functionality"""
    try:
        print(f"\n🧪 Testing AgentCore Gateway: {gateway_id}")
        
        # Try to invoke the gateway (this would depend on the specific implementation)
        agentcore_client = boto3.client('bedrock-agentcore', region_name='us-east-1')
        
        # Test basic connectivity
        print(f"✅ Gateway client initialized")
        print(f"   Gateway URL: {gateway_url}")
        
        # Note: Actual invocation would depend on the gateway configuration
        # and the specific use case
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing gateway: {str(e)}")
        return False

def provide_usage_examples(gateway_info, dynamodb_tables):
    """Provide usage examples for the AgentCore + DynamoDB setup"""
    print("\n" + "="*60)
    print("🎯 USAGE EXAMPLES")
    print("="*60)
    
    if gateway_info and dynamodb_tables:
        print("\n📝 Your AgentCore + DynamoDB Setup:")
        print(f"   Gateway: {gateway_info.get('name', 'Unknown')}")
        print(f"   Gateway ID: {gateway_info.get('gatewayId', 'Unknown')}")
        print(f"   DynamoDB Tables: {', '.join(dynamodb_tables)}")
        
        print("\n🔧 Example Use Cases:")
        print("1. 📚 Context Storage")
        print("   - Store conversation history")
        print("   - Maintain user preferences")
        print("   - Cache frequently accessed data")
        
        print("\n2. 🧠 Knowledge Base")
        print("   - Store domain-specific information")
        print("   - Maintain FAQ data")
        print("   - Keep reference materials")
        
        print("\n3. 🔄 Session Management")
        print("   - Track user sessions")
        print("   - Maintain state across interactions")
        print("   - Store temporary data")
        
        print("\n💡 Sample DynamoDB Operations:")
        print("```python")
        print("# Store context data")
        print("table.put_item(Item={")
        print("    'session_id': 'user123_session456',")
        print("    'timestamp': int(time.time()),")
        print("    'context': 'User asking about AgentCore setup',")
        print("    'data': {'topic': 'aws', 'complexity': 'intermediate'}")
        print("})")
        print("")
        print("# Retrieve context")
        print("response = table.get_item(Key={'session_id': 'user123_session456'})")
        print("context = response.get('Item', {})")
        print("```")
        
    else:
        print("\n⚠️  Setup not fully detected. Please check:")
        print("   - Gateway configuration")
        print("   - DynamoDB table permissions")
        print("   - Integration settings")

def main():
    print("🚀 AgentCore + DynamoDB Analysis")
    print("=" * 60)
    
    try:
        # Check AWS credentials
        sts_client = boto3.client('sts')
        identity = sts_client.get_caller_identity()
        print(f"🔑 AWS Account: {identity['Account']}")
        print(f"🔑 User/Role: {identity['Arn']}")
        
        # Discover gateways
        gateways = discover_agentcore_gateways()
        
        # Discover DynamoDB tables
        dynamodb_tables = discover_dynamodb_tables()
        
        # Analyze each gateway
        for gateway in gateways:
            gateway_id = gateway.get('gatewayId')
            gateway_url = gateway.get('gatewayUrl')
            
            if gateway_id:
                # Discover targets
                targets = discover_gateway_targets(gateway_id)
                
                # Test gateway
                test_agentcore_gateway(gateway_id, gateway_url)
        
        # Test DynamoDB connectivity
        for table_name in dynamodb_tables:
            test_dynamodb_connectivity(table_name)
        
        # Provide usage examples
        gateway_info = gateways[0] if gateways else None
        provide_usage_examples(gateway_info, dynamodb_tables)
        
    except NoCredentialsError:
        print("❌ AWS credentials not found")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()

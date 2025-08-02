#!/usr/bin/env python3
"""
Setup AgentCore Gateway with DynamoDB integration
"""

import boto3
import json
import time
from datetime import datetime
from botocore.exceptions import ClientError, NoCredentialsError

def create_dynamodb_table_for_agentcore():
    """Create a DynamoDB table optimized for AgentCore usage"""
    try:
        dynamodb = boto3.client('dynamodb', region_name='us-east-1')
        
        table_name = 'AgentCoreContextStore'
        
        print(f"🗄️  Creating DynamoDB table: {table_name}")
        
        # Check if table already exists
        try:
            response = dynamodb.describe_table(TableName=table_name)
            print(f"✅ Table {table_name} already exists!")
            return table_name
        except ClientError as e:
            if e.response['Error']['Code'] != 'ResourceNotFoundException':
                raise e
        
        # Create table with optimized schema for AgentCore
        table_config = {
            'TableName': table_name,
            'KeySchema': [
                {
                    'AttributeName': 'session_id',
                    'KeyType': 'HASH'  # Partition key
                },
                {
                    'AttributeName': 'timestamp',
                    'KeyType': 'RANGE'  # Sort key
                }
            ],
            'AttributeDefinitions': [
                {
                    'AttributeName': 'session_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'timestamp',
                    'AttributeType': 'N'
                },
                {
                    'AttributeName': 'context_type',
                    'AttributeType': 'S'
                }
            ],
            'GlobalSecondaryIndexes': [
                {
                    'IndexName': 'ContextTypeIndex',
                    'KeySchema': [
                        {
                            'AttributeName': 'context_type',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'timestamp',
                            'KeyType': 'RANGE'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                }
            ],
            'BillingMode': 'PAY_PER_REQUEST',
            'Tags': [
                {
                    'Key': 'Purpose',
                    'Value': 'AgentCoreContextStore'
                },
                {
                    'Key': 'Service',
                    'Value': 'BedrockAgentCore'
                }
            ]
        }
        
        response = dynamodb.create_table(**table_config)
        
        print(f"✅ Table creation initiated. Status: {response['TableDescription']['TableStatus']}")
        
        # Wait for table to be active
        print("⏳ Waiting for table to become active...")
        waiter = dynamodb.get_waiter('table_exists')
        waiter.wait(TableName=table_name)
        
        print(f"✅ Table {table_name} is now active!")
        return table_name
        
    except Exception as e:
        print(f"❌ Error creating DynamoDB table: {str(e)}")
        return None

def create_agentcore_gateway_with_dynamodb(table_name):
    """Create AgentCore Gateway with DynamoDB target"""
    try:
        client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
        
        print(f"🏗️  Creating AgentCore Gateway with DynamoDB target...")
        
        # First, let's try to create a basic gateway
        gateway_config = {
            'name': 'AgentCoreDynamoDBGateway',
            'description': 'AgentCore Gateway with DynamoDB context store integration',
            'protocolType': 'MCP',
            'protocolConfiguration': {
                'mcp': {
                    'supportedVersions': ['2024-11-05'],
                    'instructions': 'Gateway for AgentCore with DynamoDB context storage and retrieval',
                    'searchType': 'SEMANTIC'
                }
            },
            'authorizerType': 'CUSTOM_JWT',
            'authorizerConfiguration': {
                'customJWTAuthorizer': {
                    'discoveryUrl': 'https://bedrock-agentcore.amazonaws.com/.well-known/openid_configuration',
                    'allowedAudience': ['agentcore-dynamodb'],
                    'allowedClients': ['agentcore-client']
                }
            }
        }
        
        # We'll need to handle the role requirement
        print("⚠️  Note: Gateway creation requires an IAM role.")
        print("   Please create the gateway manually in the AWS Console with these settings:")
        print(f"   - Name: {gateway_config['name']}")
        print(f"   - Description: {gateway_config['description']}")
        print(f"   - Protocol: {gateway_config['protocolType']}")
        print(f"   - DynamoDB Table: {table_name}")
        
        return None
        
    except Exception as e:
        print(f"❌ Error creating gateway: {str(e)}")
        return None

def populate_sample_data(table_name):
    """Populate the DynamoDB table with sample context data"""
    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table(table_name)
        
        print(f"📝 Populating sample data in {table_name}...")
        
        sample_data = [
            {
                'session_id': 'demo_session_001',
                'timestamp': int(time.time()),
                'context_type': 'conversation',
                'content': 'User is asking about AWS AgentCore setup and configuration',
                'metadata': {
                    'topic': 'aws_agentcore',
                    'complexity': 'intermediate',
                    'user_intent': 'setup_help'
                }
            },
            {
                'session_id': 'demo_session_001',
                'timestamp': int(time.time()) + 1,
                'context_type': 'knowledge',
                'content': 'AgentCore is a service for building AI agents with context awareness',
                'metadata': {
                    'source': 'aws_documentation',
                    'confidence': 0.95,
                    'category': 'technical_definition'
                }
            },
            {
                'session_id': 'demo_session_002',
                'timestamp': int(time.time()) + 2,
                'context_type': 'user_preference',
                'content': 'User prefers detailed technical explanations with code examples',
                'metadata': {
                    'preference_type': 'communication_style',
                    'learned_from': 'interaction_history'
                }
            }
        ]
        
        for item in sample_data:
            table.put_item(Item=item)
            print(f"   ✅ Added: {item['context_type']} - {item['content'][:50]}...")
        
        print(f"✅ Sample data populated successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error populating sample data: {str(e)}")
        return False

def demonstrate_dynamodb_operations(table_name):
    """Demonstrate common DynamoDB operations for AgentCore"""
    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table(table_name)
        
        print(f"\n🧪 Demonstrating DynamoDB operations for {table_name}:")
        
        # 1. Query by session
        print("\n1. 📋 Query by session ID:")
        response = table.query(
            KeyConditionExpression='session_id = :sid',
            ExpressionAttributeValues={':sid': 'demo_session_001'}
        )
        items = response.get('Items', [])
        print(f"   Found {len(items)} items for demo_session_001")
        for item in items:
            print(f"   - {item['context_type']}: {item['content'][:50]}...")
        
        # 2. Query by context type using GSI
        print("\n2. 🔍 Query by context type (using GSI):")
        response = table.query(
            IndexName='ContextTypeIndex',
            KeyConditionExpression='context_type = :ct',
            ExpressionAttributeValues={':ct': 'knowledge'}
        )
        items = response.get('Items', [])
        print(f"   Found {len(items)} knowledge items")
        for item in items:
            print(f"   - {item['content'][:50]}...")
        
        # 3. Scan for recent items
        print("\n3. ⏰ Scan for recent items:")
        current_time = int(time.time())
        response = table.scan(
            FilterExpression='#ts > :recent_time',
            ExpressionAttributeNames={'#ts': 'timestamp'},
            ExpressionAttributeValues={':recent_time': current_time - 3600}  # Last hour
        )
        items = response.get('Items', [])
        print(f"   Found {len(items)} recent items")
        
        return True
        
    except Exception as e:
        print(f"❌ Error demonstrating operations: {str(e)}")
        return False

def provide_integration_guide(table_name):
    """Provide guidance on integrating with AgentCore"""
    print("\n" + "="*60)
    print("🎯 AGENTCORE + DYNAMODB INTEGRATION GUIDE")
    print("="*60)
    
    print(f"\n📊 Your DynamoDB Table: {table_name}")
    print("   Schema: session_id (PK), timestamp (SK)")
    print("   GSI: ContextTypeIndex (context_type, timestamp)")
    print("   Billing: Pay-per-request")
    
    print("\n🔧 Manual Gateway Setup Steps:")
    print("1. Go to AWS Bedrock Console → AgentCore → Gateways")
    print("2. Create New Gateway:")
    print("   - Name: AgentCoreDynamoDBGateway")
    print("   - Protocol: MCP")
    print("   - Description: Gateway with DynamoDB context store")
    
    print("\n3. Add DynamoDB Target:")
    print(f"   - Target Name: {table_name}")
    print("   - Target Type: DynamoDB")
    print(f"   - Table Name: {table_name}")
    print("   - Access Pattern: Read/Write")
    
    print("\n💡 Usage Patterns:")
    print("```python")
    print("# Store conversation context")
    print("table.put_item(Item={")
    print("    'session_id': f'user_{user_id}_session_{session_id}',")
    print("    'timestamp': int(time.time()),")
    print("    'context_type': 'conversation',")
    print("    'content': 'User message and agent response',")
    print("    'metadata': {'intent': 'question', 'topic': 'aws'}")
    print("})")
    print("")
    print("# Retrieve session history")
    print("response = table.query(")
    print("    KeyConditionExpression='session_id = :sid',")
    print("    ExpressionAttributeValues={':sid': session_id},")
    print("    ScanIndexForward=False,  # Latest first")
    print("    Limit=10")
    print(")")
    print("```")
    
    print("\n🚀 Benefits of This Setup:")
    print("   ✅ Persistent context storage")
    print("   ✅ Fast retrieval by session or type")
    print("   ✅ Scalable and cost-effective")
    print("   ✅ Integrated with AWS ecosystem")
    print("   ✅ No marketplace dependencies")

def main():
    print("🚀 AgentCore + DynamoDB Setup")
    print("=" * 60)
    
    try:
        # Check AWS credentials
        sts_client = boto3.client('sts')
        identity = sts_client.get_caller_identity()
        print(f"🔑 AWS Account: {identity['Account']}")
        print(f"🔑 User/Role: {identity['Arn']}")
        
        # Create DynamoDB table
        table_name = create_dynamodb_table_for_agentcore()
        
        if table_name:
            # Populate sample data
            populate_sample_data(table_name)
            
            # Demonstrate operations
            demonstrate_dynamodb_operations(table_name)
            
            # Provide integration guide
            provide_integration_guide(table_name)
            
            print(f"\n✅ Setup complete! DynamoDB table '{table_name}' is ready for AgentCore integration.")
        else:
            print("❌ Setup failed. Please check permissions and try again.")
        
    except NoCredentialsError:
        print("❌ AWS credentials not found")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()

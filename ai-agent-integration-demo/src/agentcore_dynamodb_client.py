#!/usr/bin/env python3
"""
AgentCore DynamoDB Client - Practical usage examples
"""

import boto3
import json
import time
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from botocore.exceptions import ClientError

class AgentCoreDynamoDBClient:
    """Client for interacting with AgentCore DynamoDB context store"""
    
    def __init__(self, table_name='AgentCoreContextStore', region='us-east-1'):
        self.dynamodb = boto3.resource('dynamodb', region_name=region)
        self.table = self.dynamodb.Table(table_name)
        self.table_name = table_name
    
    def store_conversation_context(self, session_id, user_message, agent_response, metadata=None):
        """Store conversation context in DynamoDB"""
        try:
            timestamp = int(time.time())
            
            item = {
                'session_id': session_id,
                'timestamp': timestamp,
                'context_type': 'conversation',
                'content': {
                    'user_message': user_message,
                    'agent_response': agent_response,
                    'interaction_id': str(uuid.uuid4())
                },
                'metadata': metadata or {}
            }
            
            self.table.put_item(Item=item)
            print(f"✅ Stored conversation context for session: {session_id}")
            return timestamp
            
        except Exception as e:
            print(f"❌ Error storing conversation: {str(e)}")
            return None
    
    def store_knowledge_item(self, content, category, source=None, confidence=1.0):
        """Store knowledge base item"""
        try:
            timestamp = int(time.time())
            knowledge_id = f"knowledge_{int(timestamp)}_{str(uuid.uuid4())[:8]}"
            
            item = {
                'session_id': knowledge_id,
                'timestamp': timestamp,
                'context_type': 'knowledge',
                'content': content,
                'metadata': {
                    'category': category,
                    'source': source or 'manual_entry',
                    'confidence': Decimal(str(confidence)),
                    'created_at': datetime.now().isoformat()
                }
            }
            
            self.table.put_item(Item=item)
            print(f"✅ Stored knowledge item: {category}")
            return knowledge_id
            
        except Exception as e:
            print(f"❌ Error storing knowledge: {str(e)}")
            return None
    
    def store_user_preference(self, user_id, preference_type, preference_value):
        """Store user preferences"""
        try:
            timestamp = int(time.time())
            session_id = f"user_pref_{user_id}"
            
            item = {
                'session_id': session_id,
                'timestamp': timestamp,
                'context_type': 'user_preference',
                'content': {
                    'preference_type': preference_type,
                    'preference_value': preference_value
                },
                'metadata': {
                    'user_id': user_id,
                    'updated_at': datetime.now().isoformat()
                }
            }
            
            self.table.put_item(Item=item)
            print(f"✅ Stored user preference: {preference_type} for user {user_id}")
            return timestamp
            
        except Exception as e:
            print(f"❌ Error storing preference: {str(e)}")
            return None
    
    def get_conversation_history(self, session_id, limit=10):
        """Retrieve conversation history for a session"""
        try:
            response = self.table.query(
                KeyConditionExpression='session_id = :sid AND context_type = :ct',
                FilterExpression='context_type = :ct',
                ExpressionAttributeValues={
                    ':sid': session_id,
                    ':ct': 'conversation'
                },
                ScanIndexForward=False,  # Latest first
                Limit=limit
            )
            
            conversations = response.get('Items', [])
            print(f"📋 Retrieved {len(conversations)} conversation items for {session_id}")
            return conversations
            
        except Exception as e:
            print(f"❌ Error retrieving conversations: {str(e)}")
            return []
    
    def search_knowledge_by_category(self, category, limit=10):
        """Search knowledge items by category"""
        try:
            response = self.table.query(
                IndexName='ContextTypeIndex',
                KeyConditionExpression='context_type = :ct',
                FilterExpression='metadata.category = :cat',
                ExpressionAttributeValues={
                    ':ct': 'knowledge',
                    ':cat': category
                },
                ScanIndexForward=False,
                Limit=limit
            )
            
            knowledge_items = response.get('Items', [])
            print(f"🔍 Found {len(knowledge_items)} knowledge items for category: {category}")
            return knowledge_items
            
        except Exception as e:
            print(f"❌ Error searching knowledge: {str(e)}")
            return []
    
    def get_user_preferences(self, user_id):
        """Get all preferences for a user"""
        try:
            session_id = f"user_pref_{user_id}"
            response = self.table.query(
                KeyConditionExpression='session_id = :sid',
                ExpressionAttributeValues={':sid': session_id},
                ScanIndexForward=False
            )
            
            preferences = response.get('Items', [])
            print(f"👤 Retrieved {len(preferences)} preferences for user {user_id}")
            return preferences
            
        except Exception as e:
            print(f"❌ Error retrieving preferences: {str(e)}")
            return []
    
    def get_recent_activity(self, hours=24):
        """Get recent activity across all context types"""
        try:
            cutoff_time = int(time.time()) - (hours * 3600)
            
            response = self.table.scan(
                FilterExpression='#ts > :cutoff',
                ExpressionAttributeNames={'#ts': 'timestamp'},
                ExpressionAttributeValues={':cutoff': cutoff_time}
            )
            
            items = response.get('Items', [])
            print(f"⏰ Found {len(items)} items from the last {hours} hours")
            return items
            
        except Exception as e:
            print(f"❌ Error retrieving recent activity: {str(e)}")
            return []

def demonstrate_usage():
    """Demonstrate practical usage of the AgentCore DynamoDB client"""
    print("🚀 AgentCore DynamoDB Client Demo")
    print("=" * 50)
    
    client = AgentCoreDynamoDBClient()
    
    # 1. Store conversation context
    print("\n1. 💬 Storing Conversation Context:")
    session_id = f"demo_session_{int(time.time())}"
    client.store_conversation_context(
        session_id=session_id,
        user_message="How do I set up AgentCore with DynamoDB?",
        agent_response="I'll help you set up AgentCore with DynamoDB. First, you need to create a gateway...",
        metadata={
            'topic': 'agentcore_setup',
            'complexity': 'intermediate',
            'user_intent': 'setup_help'
        }
    )
    
    # 2. Store knowledge items
    print("\n2. 📚 Storing Knowledge Items:")
    client.store_knowledge_item(
        content="AgentCore is AWS Bedrock's service for building context-aware AI agents",
        category="aws_services",
        source="aws_documentation",
        confidence=0.95
    )
    
    client.store_knowledge_item(
        content="DynamoDB is a NoSQL database service that provides fast performance at any scale",
        category="aws_services",
        source="aws_documentation",
        confidence=0.98
    )
    
    # 3. Store user preferences
    print("\n3. 👤 Storing User Preferences:")
    user_id = "user_123"
    client.store_user_preference(user_id, "response_style", "detailed_with_examples")
    client.store_user_preference(user_id, "preferred_language", "python")
    
    # 4. Retrieve data
    print("\n4. 📖 Retrieving Data:")
    
    # Get conversation history
    conversations = client.get_conversation_history(session_id)
    if conversations:
        print(f"   Latest conversation: {conversations[0]['content']['user_message'][:50]}...")
    
    # Search knowledge
    knowledge = client.search_knowledge_by_category("aws_services")
    if knowledge:
        print(f"   Knowledge items found: {len(knowledge)}")
    
    # Get user preferences
    preferences = client.get_user_preferences(user_id)
    if preferences:
        print(f"   User preferences: {len(preferences)} items")
    
    # Get recent activity
    recent = client.get_recent_activity(hours=1)
    print(f"   Recent activity: {len(recent)} items in the last hour")

def create_integration_example():
    """Create an example of how to integrate with AgentCore"""
    print("\n" + "="*60)
    print("🔧 AGENTCORE INTEGRATION EXAMPLE")
    print("="*60)
    
    print("""
# Example: AgentCore Integration Class
class AgentCoreContextManager:
    def __init__(self):
        self.db_client = AgentCoreDynamoDBClient()
    
    def process_user_message(self, user_id, session_id, message):
        # 1. Get user preferences
        preferences = self.db_client.get_user_preferences(user_id)
        
        # 2. Get conversation history for context
        history = self.db_client.get_conversation_history(session_id, limit=5)
        
        # 3. Search relevant knowledge
        # (You would implement semantic search here)
        
        # 4. Generate response using AgentCore
        response = self.generate_response(message, history, preferences)
        
        # 5. Store the interaction
        self.db_client.store_conversation_context(
            session_id, message, response,
            metadata={'timestamp': time.time()}
        )
        
        return response
    
    def generate_response(self, message, history, preferences):
        # This would integrate with your AgentCore gateway
        return "Generated response based on context..."
""")

def main():
    try:
        demonstrate_usage()
        create_integration_example()
        
        print("\n✅ Demo completed successfully!")
        print("\n🎯 Next Steps:")
        print("   1. Create AgentCore Gateway in AWS Console")
        print("   2. Add DynamoDB target pointing to 'AgentCoreContextStore'")
        print("   3. Use this client to manage context data")
        print("   4. Integrate with your AgentCore application")
        
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")

if __name__ == "__main__":
    main()

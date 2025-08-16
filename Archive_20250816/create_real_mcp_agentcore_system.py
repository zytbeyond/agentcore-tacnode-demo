#!/usr/bin/env python3
"""
Create REAL MCP AgentCore System - NO SIMULATION!
Everything must be real connections to TACNode Context Lake
"""

import boto3
import json
import os
import time
import httpx
import asyncio
from datetime import datetime

class RealMCPAgentCoreSystem:
    """Create real MCP system with actual TACNode connections"""
    
    def __init__(self):
        self.bedrock_agentcore = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
        self.ecr = boto3.client('ecr', region_name='us-east-1')
        
        # Real environment variables - NO DEFAULTS
        self.tacnode_token = os.getenv('TACNODE_TOKEN')
        if not self.tacnode_token:
            raise ValueError("❌ TACNODE_TOKEN environment variable REQUIRED - no simulation!")
        
        print("🔧 CREATING REAL MCP AGENTCORE SYSTEM")
        print("=" * 60)
        print("✅ TACNode Token: Available")
        print("🚫 NO SIMULATION - Everything will be REAL!")
    
    def create_real_mcp_target_config(self):
        """Create real MCP target configuration for TACNode"""
        print("\n📋 STEP 1: Creating REAL MCP Target Configuration")
        print("-" * 50)
        
        # Real MCP target configuration
        mcp_target_config = {
            "targetName": "tacnode-mcp-server",
            "targetConfiguration": {
                "type": "MCP",
                "mcpConfiguration": {
                    "serverUrl": "https://mcp-server.tacnode.io/mcp",
                    "authentication": {
                        "type": "bearer",
                        "token": self.tacnode_token
                    },
                    "tools": [
                        "execute_sql",
                        "list_tables",
                        "describe_table"
                    ]
                }
            }
        }
        
        # Save real configuration
        with open('real-mcp-target-config.json', 'w') as f:
            json.dump(mcp_target_config, f, indent=2)
        
        print("✅ Real MCP target configuration created")
        print(f"   Server URL: https://mcp-server.tacnode.io/mcp")
        print(f"   Authentication: Bearer token (real)")
        print(f"   Tools: execute_sql, list_tables, describe_table")
        
        return mcp_target_config
    
    def create_real_agent_code(self):
        """Create agent with REAL MCP calls - NO SIMULATION"""
        print("\n📋 STEP 2: Creating REAL Agent Code")
        print("-" * 50)
        
        real_agent_code = '''#!/usr/bin/env python3
"""
REAL Business Intelligence Agent - NO SIMULATION!
Makes actual MCP calls to TACNode Context Lake via AgentCore Gateway
"""

import asyncio
import httpx
import json
import os
import logging
import time
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealBusinessIntelligenceAgent:
    """REAL agent with actual MCP calls to TACNode - NO SIMULATION"""
    
    def __init__(self):
        # Real environment variables - REQUIRED
        self.gateway_id = os.getenv('GATEWAY_ID')
        self.gateway_token = os.getenv('GATEWAY_TOKEN') 
        self.tacnode_token = os.getenv('TACNODE_TOKEN')
        
        if not all([self.gateway_id, self.gateway_token, self.tacnode_token]):
            raise ValueError("❌ Missing REQUIRED environment variables: GATEWAY_ID, GATEWAY_TOKEN, TACNODE_TOKEN")
        
        logger.info("🔧 REAL Business Intelligence Agent initialized")
        logger.info(f"   Gateway ID: {self.gateway_id}")
        logger.info("   🚫 NO SIMULATION - All calls will be REAL!")
    
    async def make_real_mcp_call(self, sql_query: str) -> Optional[Dict[str, Any]]:
        """Make REAL MCP call to TACNode via AgentCore Gateway"""
        try:
            logger.info("🌉 Making REAL MCP call to AgentCore Gateway...")
            
            # Real MCP request - JSON-RPC 2.0
            mcp_request = {
                "jsonrpc": "2.0",
                "id": int(time.time()),
                "method": "tools/call",
                "params": {
                    "name": "execute_sql",
                    "arguments": {
                        "query": sql_query
                    }
                }
            }
            
            # Real AgentCore Gateway endpoint
            gateway_endpoint = f"https://gateway-{self.gateway_id}.bedrock-agentcore.us-east-1.amazonaws.com"
            target_url = f"{gateway_endpoint}/targets/tacnode-mcp-server/invoke"
            
            logger.info(f"   Target URL: {target_url}")
            logger.info(f"   MCP Request: {json.dumps(mcp_request)}")
            
            # Real HTTP call to AgentCore Gateway
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    target_url,
                    json=mcp_request,
                    headers={
                        "Authorization": f"Bearer {self.gateway_token}",
                        "Content-Type": "application/json",
                        "User-Agent": "RealBusinessIntelligenceAgent/1.0"
                    }
                )
                
                logger.info(f"   Response Status: {response.status_code}")
                
                if response.status_code != 200:
                    logger.error(f"❌ Gateway call failed: {response.status_code} - {response.text}")
                    return None
                
                # Parse real MCP response
                mcp_response = response.json()
                logger.info(f"   MCP Response: {json.dumps(mcp_response)}")
                
                if 'result' in mcp_response and 'content' in mcp_response['result']:
                    # Extract real business data from TACNode
                    business_data_text = mcp_response['result']['content'][0]['text']
                    business_records = json.loads(business_data_text)
                    
                    logger.info(f"✅ Retrieved {len(business_records)} REAL records from TACNode")
                    
                    return {
                        "records": business_records,
                        "source": "TACNode Context Lake (REAL)",
                        "method": "Real MCP via AgentCore Gateway",
                        "timestamp": datetime.now().isoformat(),
                        "query": sql_query
                    }
                else:
                    logger.error("❌ Invalid MCP response format")
                    return None
                    
        except httpx.HTTPError as e:
            logger.error(f"❌ HTTP error calling AgentCore Gateway: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON decode error: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return None
    
    async def get_real_business_data(self, query_context: str) -> Optional[Dict[str, Any]]:
        """Get REAL business data from TACNode Context Lake"""
        
        # Real SQL query for business data
        sql_query = """
        SELECT 
            id, 
            name, 
            description, 
            value, 
            category, 
            created_date, 
            is_active 
        FROM test 
        WHERE is_active = true 
        ORDER BY created_date DESC
        """
        
        logger.info("📊 Fetching REAL business data from TACNode...")
        return await self.make_real_mcp_call(sql_query)
    
    def should_access_business_data(self, user_input: str) -> bool:
        """Determine if user question requires business data"""
        business_keywords = [
            'business', 'performance', 'metrics', 'analytics', 'revenue',
            'sales', 'category', 'value', 'financial', 'trends', 'insights',
            'total', 'summary', 'overview', 'report', 'data'
        ]
        
        user_lower = user_input.lower()
        return any(keyword in user_lower for keyword in business_keywords)
    
    async def process_user_question(self, user_question: str) -> Dict[str, Any]:
        """Process user question with REAL business data"""
        
        if self.should_access_business_data(user_question):
            logger.info(f"🧠 Business question detected: {user_question}")
            
            # Get REAL business data via MCP
            business_data = await self.get_real_business_data(user_question)
            
            if business_data and business_data['records']:
                records = business_data['records']
                
                # Calculate REAL metrics from REAL data
                total_value = sum(float(record.get('value', 0)) for record in records)
                categories = {}
                
                for record in records:
                    category = record.get('category', 'Unknown')
                    if category not in categories:
                        categories[category] = {'count': 0, 'total': 0}
                    categories[category]['count'] += 1
                    categories[category]['total'] += float(record.get('value', 0))
                
                # Find top performing category
                top_category = max(categories.items(), key=lambda x: x[1]['total']) if categories else None
                
                # Generate response with REAL data
                response_message = f"""Based on REAL-TIME data from TACNode Context Lake:

📊 BUSINESS PERFORMANCE SUMMARY:
• Total Business Value: ${total_value:,.2f}
• Active Records: {len(records)}
• Categories Analyzed: {len(categories)}

🏆 TOP PERFORMING CATEGORY:
• {top_category[0]}: ${top_category[1]['total']:,.2f} ({top_category[1]['count']} records)

📈 CATEGORY BREAKDOWN:"""
                
                for category, data in sorted(categories.items(), key=lambda x: x[1]['total'], reverse=True):
                    response_message += f"\\n• {category}: ${data['total']:,.2f} ({data['count']} records)"
                
                response_message += f"""

🔍 DATA SOURCE: TACNode Context Lake (PostgreSQL)
🌉 METHOD: Real MCP via AgentCore Gateway
⏰ TIMESTAMP: {business_data['timestamp']}

This analysis is based on REAL business data - no simulation!"""
                
                return {
                    "message": response_message,
                    "data_accessed": True,
                    "gateway_used": True,
                    "records_analyzed": len(records),
                    "total_value": total_value,
                    "categories": categories,
                    "source": "TACNode Context Lake (REAL)",
                    "method": "Real MCP via AgentCore Gateway",
                    "timestamp": business_data['timestamp']
                }
            else:
                return {
                    "message": "❌ Unable to access REAL business data from TACNode Context Lake. Please check MCP configuration.",
                    "data_accessed": False,
                    "error": "Real MCP call failed"
                }
        else:
            # General response for non-business questions
            return {
                "message": "I'm a business intelligence agent that accesses REAL data from TACNode Context Lake. Ask me about business performance, metrics, or data analysis.",
                "data_accessed": False,
                "gateway_used": False
            }

# Test the REAL agent
async def test_real_agent():
    """Test the REAL agent with actual TACNode data"""
    print("🧪 TESTING REAL BUSINESS INTELLIGENCE AGENT")
    print("=" * 60)
    
    try:
        agent = RealBusinessIntelligenceAgent()
        
        # Test business question
        test_question = "What is our total business value and which category is performing best?"
        print(f"\\n❓ Test Question: {test_question}")
        
        result = await agent.process_user_question(test_question)
        
        print(f"\\n📋 REAL AGENT RESPONSE:")
        print("-" * 40)
        print(result['message'])
        
        print(f"\\n📊 METADATA:")
        print(f"   Data Accessed: {result['data_accessed']}")
        print(f"   Gateway Used: {result['gateway_used']}")
        print(f"   Records Analyzed: {result.get('records_analyzed', 0)}")
        print(f"   Source: {result.get('source', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    print("🔧 REAL Business Intelligence Agent")
    print("🚫 NO SIMULATION - All data is REAL!")
    print("=" * 50)
    
    # Run test
    asyncio.run(test_real_agent())
'''
        
        # Save real agent code
        with open('real_business_intelligence_agent.py', 'w') as f:
            f.write(real_agent_code)
        
        print("✅ REAL agent code created - NO SIMULATION!")
        print("   File: real_business_intelligence_agent.py")
        print("   Features: Real MCP calls, Real TACNode data, Real business intelligence")
        
        return True
    
    def configure_real_gateway_target(self):
        """Configure REAL MCP target in AgentCore Gateway"""
        print("\n📋 STEP 3: Configuring REAL MCP Target in Gateway")
        print("-" * 50)
        
        try:
            # Load existing gateway info
            with open('tacnode-agentcore-gateway.json', 'r') as f:
                gateway_info = json.load(f)
                gateway_id = gateway_info['gatewayId']
            
            print(f"   Gateway ID: {gateway_id}")
            
            # Real MCP target configuration
            target_config = {
                "type": "MCP",
                "mcpConfiguration": {
                    "serverUrl": "https://mcp-server.tacnode.io/mcp",
                    "authentication": {
                        "type": "bearer",
                        "token": self.tacnode_token
                    }
                }
            }
            
            print(f"   Target: tacnode-mcp-server")
            print(f"   URL: https://mcp-server.tacnode.io/mcp")
            print(f"   Auth: Bearer token (real)")
            
            # Create REAL MCP target
            print("\n🔧 Creating REAL MCP target...")

            response = self.bedrock_agentcore.create_gateway_target(
                gatewayIdentifier=gateway_id,
                name='tacnode-mcp-server',
                targetConfiguration=target_config,
                credentialProviderConfigurations=[
                    {
                        'credentialProviderType': 'BEARER_TOKEN',
                        'credentialProvider': {
                            'bearerTokenCredentialProvider': {
                                'token': self.tacnode_token
                            }
                        }
                    }
                ]
            )
            
            print("✅ REAL MCP target created successfully!")
            print(f"   Target ID: {response.get('targetId', 'N/A')}")
            print(f"   Status: {response.get('status', 'N/A')}")

            # Save target info
            target_info = {
                "targetName": "tacnode-mcp-server",
                "targetId": response.get('targetId'),
                "gatewayId": gateway_id,
                "serverUrl": "https://mcp-server.tacnode.io/mcp",
                "status": response.get('status'),
                "created": datetime.now().isoformat()
            }
            
            with open('real-mcp-target.json', 'w') as f:
                json.dump(target_info, f, indent=2)
            
            return target_info
            
        except Exception as e:
            print(f"❌ Failed to create REAL MCP target: {e}")
            return None
    
    def test_real_mcp_connection(self):
        """Test REAL MCP connection to TACNode"""
        print("\n📋 STEP 4: Testing REAL MCP Connection")
        print("-" * 50)
        
        try:
            # Test direct MCP call to TACNode
            print("🧪 Testing direct MCP call to TACNode...")
            
            import asyncio
            
            async def test_direct_mcp():
                mcp_request = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": "execute_sql",
                        "arguments": {
                            "query": "SELECT COUNT(*) as record_count FROM test WHERE is_active = true"
                        }
                    }
                }
                
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        "https://mcp-server.tacnode.io/mcp",
                        json=mcp_request,
                        headers={
                            "Authorization": f"Bearer {self.tacnode_token}",
                            "Content-Type": "application/json"
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        print("✅ Direct MCP call successful!")
                        print(f"   Response: {json.dumps(result, indent=2)}")
                        return True
                    else:
                        print(f"❌ Direct MCP call failed: {response.status_code}")
                        print(f"   Error: {response.text}")
                        return False
            
            # Run test
            success = asyncio.run(test_direct_mcp())
            return success
            
        except Exception as e:
            print(f"❌ MCP connection test failed: {e}")
            return False
    
    def deploy_real_system(self):
        """Deploy complete REAL MCP system"""
        print("\n🚀 DEPLOYING REAL MCP AGENTCORE SYSTEM")
        print("=" * 60)
        print("🚫 NO SIMULATION - Everything is REAL!")
        
        # Step 1: Create real MCP target config
        mcp_config = self.create_real_mcp_target_config()
        if not mcp_config:
            print("❌ Failed to create MCP configuration")
            return False
        
        # Step 2: Create real agent code
        if not self.create_real_agent_code():
            print("❌ Failed to create real agent code")
            return False
        
        # Step 3: Configure real gateway target
        target_info = self.configure_real_gateway_target()
        if not target_info:
            print("❌ Failed to configure gateway target")
            return False
        
        # Step 4: Test real MCP connection
        if not self.test_real_mcp_connection():
            print("❌ MCP connection test failed")
            return False
        
        print("\n🎉 REAL MCP AGENTCORE SYSTEM DEPLOYED!")
        print("=" * 60)
        print("✅ Real MCP target configured in AgentCore Gateway")
        print("✅ Real agent code with actual TACNode calls")
        print("✅ Real MCP connection to TACNode verified")
        print("✅ NO SIMULATION - Everything is REAL!")
        
        print(f"\n📋 SYSTEM DETAILS:")
        print(f"   Gateway Target: {target_info['targetName']}")
        print(f"   TACNode URL: {target_info['serverUrl']}")
        print(f"   Agent File: real_business_intelligence_agent.py")
        print(f"   Data Source: TACNode Context Lake (PostgreSQL)")
        
        print(f"\n🧪 TO TEST:")
        print(f"   python3 real_business_intelligence_agent.py")
        
        return True

def main():
    print("🔧 CREATE REAL MCP AGENTCORE SYSTEM")
    print("🚫 NO SIMULATION - EVERYTHING MUST BE REAL!")
    print("=" * 60)
    
    try:
        system = RealMCPAgentCoreSystem()
        success = system.deploy_real_system()
        
        if success:
            print("\n🎯 MISSION ACCOMPLISHED!")
            print("   Real MCP system deployed and tested")
            print("   No simulation - all connections are real")
        else:
            print("\n❌ DEPLOYMENT FAILED")
            print("   Check configuration and try again")
            
    except Exception as e:
        print(f"❌ System creation failed: {e}")

if __name__ == "__main__":
    main()

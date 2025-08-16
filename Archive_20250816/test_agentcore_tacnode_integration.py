#!/usr/bin/env python3
"""
Test AgentCore Gateway + TACNode Integration
User → MCP → AgentCore Gateway → TACNode JSON-RPC API → PostgreSQL
"""

import asyncio
import httpx
import json
import os
import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentCoreTACNodeBusinessIntelligenceAgent:
    """Business Intelligence Agent using AgentCore Gateway + TACNode integration"""
    
    def __init__(self):
        # Load gateway and target information
        with open('tacnode-agentcore-gateway.json', 'r') as f:
            gateway_info = json.load(f)
            self.gateway_id = gateway_info['gatewayId']
        
        with open('tacnode-agentcore-target.json', 'r') as f:
            target_info = json.load(f)
            self.target_name = target_info['targetName']
            self.target_id = target_info['targetId']
        
        # Gateway access token (would be provided by user)
        self.gateway_token = os.getenv('GATEWAY_TOKEN')
        
        if not self.gateway_token:
            logger.warning("⚠️  GATEWAY_TOKEN not set - using placeholder for demo")
            self.gateway_token = "placeholder-token"
        
        self.gateway_endpoint = f"https://gateway-{self.gateway_id}.bedrock-agentcore.us-east-1.amazonaws.com"
        
        logger.info("🌐 AgentCore + TACNode Business Intelligence Agent initialized")
        logger.info(f"   Gateway ID: {self.gateway_id}")
        logger.info(f"   Target Name: {self.target_name}")
        logger.info(f"   Target ID: {self.target_id}")
        logger.info(f"   Gateway Endpoint: {self.gateway_endpoint}")
        logger.info("   🎯 Flow: User → MCP → AgentCore Gateway → TACNode → PostgreSQL")
    
    async def make_mcp_call_to_gateway(self, method: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make MCP call to AgentCore Gateway"""
        try:
            logger.info(f"🌐 Making MCP call to AgentCore Gateway: {method}")
            
            # MCP request following JSON-RPC 2.0 standard
            mcp_request = {
                "jsonrpc": "2.0",
                "id": int(time.time()),
                "method": method,
                "params": params
            }
            
            # Gateway target URL
            target_url = f"{self.gateway_endpoint}/targets/{self.target_name}/invoke"
            
            logger.info(f"   Target URL: {target_url}")
            logger.info(f"   MCP Request: {json.dumps(mcp_request, indent=2)}")
            
            # HTTP call to AgentCore Gateway
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    target_url,
                    json=mcp_request,
                    headers={
                        "Authorization": f"Bearer {self.gateway_token}",
                        "Content-Type": "application/json",
                        "User-Agent": "AgentCoreTACNodeAgent/1.0"
                    }
                )
                
                logger.info(f"   Gateway Response Status: {response.status_code}")
                
                if response.status_code != 200:
                    logger.error(f"❌ Gateway call failed: {response.status_code} - {response.text}")
                    return None
                
                # Parse gateway response
                mcp_response = response.json()
                logger.info(f"   Gateway Response: {json.dumps(mcp_response, indent=2)}")
                
                return mcp_response
                    
        except httpx.HTTPError as e:
            logger.error(f"❌ HTTP error calling AgentCore Gateway: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON decode error: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return None
    
    async def execute_sql_via_gateway(self, sql_query: str) -> Optional[Dict[str, Any]]:
        """Execute SQL query via AgentCore Gateway → TACNode"""
        
        # MCP tools/call to execute SQL following TACNode format
        mcp_params = {
            "name": "query",
            "arguments": {
                "sql": sql_query
            }
        }
        
        logger.info("📊 Executing SQL via AgentCore Gateway → TACNode...")
        logger.info(f"   SQL: {sql_query}")
        
        mcp_response = await self.make_mcp_call_to_gateway("tools/call", mcp_params)
        
        if mcp_response and 'result' in mcp_response:
            # Extract business records from gateway response
            result = mcp_response['result']
            
            if 'content' in result and len(result['content']) > 0:
                content_text = result['content'][0]['text']
                
                try:
                    # Parse business records from response
                    business_records = json.loads(content_text)
                    
                    logger.info(f"✅ Retrieved {len(business_records)} records via Gateway → TACNode")
                    
                    return {
                        "records": business_records,
                        "source": "TACNode Context Lake via AgentCore Gateway (REAL)",
                        "method": "MCP → AgentCore Gateway → TACNode JSON-RPC API",
                        "timestamp": datetime.now().isoformat(),
                        "query": sql_query
                    }
                    
                except json.JSONDecodeError:
                    # Handle non-JSON response (like error messages)
                    logger.info(f"✅ Received response via Gateway → TACNode: {content_text}")
                    
                    return {
                        "response": content_text,
                        "source": "TACNode Context Lake via AgentCore Gateway (REAL)",
                        "method": "MCP → AgentCore Gateway → TACNode JSON-RPC API",
                        "timestamp": datetime.now().isoformat(),
                        "query": sql_query
                    }
            else:
                logger.error("❌ No content in gateway response")
                return None
        else:
            logger.error("❌ No valid result from gateway")
            return None
    
    async def get_business_data(self, query_context: str) -> Optional[Dict[str, Any]]:
        """Get business data via complete gateway flow"""
        
        # Business SQL query
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
        
        logger.info("📊 Fetching business data via complete gateway flow...")
        return await self.execute_sql_via_gateway(sql_query.strip())
    
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
        """Process user question with real data via complete gateway flow"""
        
        if self.should_access_business_data(user_question):
            logger.info(f"🧠 Business question detected: {user_question}")
            
            # Get business data via complete gateway flow
            business_data = await self.get_business_data(user_question)
            
            if business_data and 'records' in business_data and business_data['records']:
                records = business_data['records']
                
                # Calculate metrics from real data
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
                
                # Generate response with real data
                response_message = f"""Based on REAL-TIME data via AgentCore Gateway:

📊 BUSINESS PERFORMANCE SUMMARY:
• Total Business Value: ${total_value:,.2f}
• Active Records: {len(records)}
• Categories Analyzed: {len(categories)}

🏆 TOP PERFORMING CATEGORY:
• {top_category[0]}: ${top_category[1]['total']:,.2f} ({top_category[1]['count']} records)

📈 CATEGORY BREAKDOWN:"""
                
                for category, data in sorted(categories.items(), key=lambda x: x[1]['total'], reverse=True):
                    response_message += f"\n• {category}: ${data['total']:,.2f} ({data['count']} records)"
                
                response_message += f"""

🔍 DATA SOURCE: TACNode Context Lake (PostgreSQL)
🌐 METHOD: MCP → AgentCore Gateway → TACNode JSON-RPC API
⏰ TIMESTAMP: {business_data['timestamp']}

This analysis uses REAL AgentCore Gateway integration!"""
                
                return {
                    "message": response_message,
                    "data_accessed": True,
                    "agentcore_gateway_used": True,
                    "records_analyzed": len(records),
                    "total_value": total_value,
                    "categories": categories,
                    "source": business_data['source'],
                    "method": business_data['method'],
                    "timestamp": business_data['timestamp']
                }
                
            elif business_data and 'response' in business_data:
                # Handle non-JSON responses (like connection errors)
                return {
                    "message": f"Received response from TACNode via AgentCore Gateway:\n{business_data['response']}",
                    "data_accessed": True,
                    "agentcore_gateway_used": True,
                    "source": business_data['source'],
                    "method": business_data['method'],
                    "timestamp": business_data['timestamp']
                }
            else:
                return {
                    "message": "❌ Unable to access business data via AgentCore Gateway. Please check configuration.",
                    "data_accessed": False,
                    "error": "Gateway call failed"
                }
        else:
            # General response for non-business questions
            return {
                "message": "I'm a business intelligence agent that accesses real data via AgentCore Gateway. Ask me about business performance, metrics, or data analysis.",
                "data_accessed": False,
                "agentcore_gateway_used": False
            }

# Test the complete integration
async def test_agentcore_tacnode_integration():
    """Test the complete AgentCore + TACNode integration"""
    print("🧪 TESTING AGENTCORE GATEWAY + TACNODE INTEGRATION")
    print("=" * 70)
    print("🎯 Flow: User → MCP → AgentCore Gateway → TACNode → PostgreSQL")
    
    try:
        agent = AgentCoreTACNodeBusinessIntelligenceAgent()
        
        # Test business question
        test_question = "What is our total business value and which category is performing best?"
        print(f"\n❓ Test Question: {test_question}")
        
        result = await agent.process_user_question(test_question)
        
        print(f"\n📋 AGENTCORE + TACNODE AGENT RESPONSE:")
        print("-" * 50)
        print(result['message'])
        
        print(f"\n📊 METADATA:")
        print(f"   Data Accessed: {result['data_accessed']}")
        print(f"   AgentCore Gateway Used: {result['agentcore_gateway_used']}")
        print(f"   Records Analyzed: {result.get('records_analyzed', 0)}")
        print(f"   Source: {result.get('source', 'N/A')}")
        print(f"   Method: {result.get('method', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    print("🌐 AgentCore Gateway + TACNode Business Intelligence Agent")
    print("🎯 Flow: User → MCP → AgentCore Gateway → TACNode → PostgreSQL")
    print("=" * 70)
    
    # Run test
    asyncio.run(test_agentcore_tacnode_integration())

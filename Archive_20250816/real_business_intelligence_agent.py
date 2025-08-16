#!/usr/bin/env python3
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
                    response_message += f"\n• {category}: ${data['total']:,.2f} ({data['count']} records)"
                
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
        print(f"\n❓ Test Question: {test_question}")
        
        result = await agent.process_user_question(test_question)
        
        print(f"\n📋 REAL AGENT RESPONSE:")
        print("-" * 40)
        print(result['message'])
        
        print(f"\n📊 METADATA:")
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

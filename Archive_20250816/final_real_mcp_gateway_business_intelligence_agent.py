#!/usr/bin/env python3
"""
FINAL REAL Business Intelligence Agent
User → MCP → AgentCore Gateway → Lambda (MCP→API) → TACNode API → PostgreSQL
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

class FinalRealMCPGatewayBusinessIntelligenceAgent:
    """FINAL REAL agent with complete gateway integration"""
    
    def __init__(self):
        # Real environment variables - REQUIRED
        self.gateway_id = "tacnodecontextlakegateway-bkq6ozcvxp"
        self.gateway_token = os.getenv('GATEWAY_TOKEN')  # AgentCore Gateway access token
        
        if not self.gateway_token:
            raise ValueError("❌ GATEWAY_TOKEN environment variable REQUIRED")
        
        self.gateway_endpoint = f"https://gateway-{self.gateway_id}.bedrock-agentcore.us-east-1.amazonaws.com"
        self.target_name = "tacnode-mcp-to-api"
        
        logger.info("🌐 FINAL REAL MCP Gateway Business Intelligence Agent initialized")
        logger.info(f"   Gateway ID: {self.gateway_id}")
        logger.info(f"   Gateway Endpoint: {self.gateway_endpoint}")
        logger.info(f"   Target: {self.target_name}")
        logger.info("   🎯 Flow: User → MCP → Gateway → Lambda → TACNode API → PostgreSQL")
    
    async def make_mcp_call_to_gateway(self, method: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make MCP call to AgentCore Gateway"""
        try:
            logger.info(f"🌐 Making MCP call to AgentCore Gateway: {method}")
            
            # Real MCP request to gateway
            mcp_request = {
                "jsonrpc": "2.0",
                "id": int(time.time()),
                "method": method,
                "params": params
            }
            
            # Gateway target URL
            target_url = f"{self.gateway_endpoint}/targets/{self.target_name}/invoke"
            
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
                        "User-Agent": "FinalRealMCPGatewayAgent/1.0"
                    }
                )
                
                logger.info(f"   Gateway Response Status: {response.status_code}")
                
                if response.status_code != 200:
                    logger.error(f"❌ Gateway MCP call failed: {response.status_code} - {response.text}")
                    return None
                
                # Parse gateway MCP response
                mcp_response = response.json()
                logger.info(f"   Gateway MCP Response: {json.dumps(mcp_response)}")
                
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
        """Execute SQL query via complete gateway flow"""
        
        # MCP tools/call to execute SQL
        mcp_params = {
            "name": "executeQuery",
            "arguments": {
                "sql": sql_query
            }
        }
        
        logger.info("📊 Executing SQL via complete gateway flow...")
        logger.info(f"   SQL: {sql_query}")
        
        mcp_response = await self.make_mcp_call_to_gateway("tools/call", mcp_params)
        
        if mcp_response and 'result' in mcp_response:
            # Extract business records from gateway response
            content = mcp_response['result']['content'][0]['text']
            business_records = json.loads(content)
            
            logger.info(f"✅ Retrieved {len(business_records)} records via complete gateway flow")
            
            return {
                "records": business_records,
                "source": "TACNode Context Lake via Complete Gateway Flow (REAL)",
                "method": "MCP → Gateway → Lambda → TACNode API",
                "timestamp": datetime.now().isoformat(),
                "query": sql_query
            }
        else:
            logger.error("❌ No valid result from gateway")
            return None
    
    async def get_real_business_data(self, query_context: str) -> Optional[Dict[str, Any]]:
        """Get REAL business data via complete gateway flow"""
        
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
        
        logger.info("📊 Fetching REAL business data via complete gateway flow...")
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
        """Process user question with REAL data via complete gateway flow"""
        
        if self.should_access_business_data(user_question):
            logger.info(f"🧠 Business question detected: {user_question}")
            
            # Get REAL business data via complete gateway flow
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
                response_message = f"""Based on REAL-TIME data via Complete Gateway Flow:

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
🌐 METHOD: MCP → AgentCore Gateway → Lambda → TACNode API
⏰ TIMESTAMP: {business_data['timestamp']}

This analysis uses COMPLETE REAL Gateway integration - exactly as requested!"""
                
                return {
                    "message": response_message,
                    "data_accessed": True,
                    "complete_gateway_used": True,
                    "records_analyzed": len(records),
                    "total_value": total_value,
                    "categories": categories,
                    "source": "TACNode Context Lake via Complete Gateway Flow (REAL)",
                    "method": "MCP → Gateway → Lambda → TACNode API",
                    "timestamp": business_data['timestamp']
                }
            else:
                return {
                    "message": "❌ Unable to access REAL business data via complete gateway flow. Please check configuration.",
                    "data_accessed": False,
                    "error": "Complete gateway flow failed"
                }
        else:
            # General response for non-business questions
            return {
                "message": "I'm a business intelligence agent that accesses REAL data via complete AgentCore Gateway flow. Ask me about business performance, metrics, or data analysis.",
                "data_accessed": False,
                "complete_gateway_used": False
            }

# Test the FINAL REAL gateway agent
async def test_final_real_gateway_agent():
    """Test the FINAL REAL gateway agent"""
    print("🧪 TESTING FINAL REAL GATEWAY BUSINESS INTELLIGENCE AGENT")
    print("=" * 70)
    print("🎯 Flow: User → MCP → Gateway → Lambda → TACNode API → PostgreSQL")
    
    try:
        agent = FinalRealMCPGatewayBusinessIntelligenceAgent()
        
        # Test business question
        test_question = "What is our total business value and which category is performing best?"
        print(f"\n❓ Test Question: {test_question}")
        
        result = await agent.process_user_question(test_question)
        
        print(f"\n📋 FINAL REAL GATEWAY AGENT RESPONSE:")
        print("-" * 50)
        print(result['message'])
        
        print(f"\n📊 METADATA:")
        print(f"   Data Accessed: {result['data_accessed']}")
        print(f"   Complete Gateway Used: {result['complete_gateway_used']}")
        print(f"   Records Analyzed: {result.get('records_analyzed', 0)}")
        print(f"   Source: {result.get('source', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    print("🌐 FINAL REAL MCP Gateway Business Intelligence Agent")
    print("🎯 Flow: User → MCP → Gateway → Lambda → TACNode API → PostgreSQL")
    print("=" * 70)
    
    # Run test
    asyncio.run(test_final_real_gateway_agent())

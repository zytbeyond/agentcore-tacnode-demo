#!/usr/bin/env python3
"""
REAL Business Intelligence Agent with AgentCore Gateway Integration
NO SHORTCUTS - Uses real gateway calls to TACNode via Lambda proxy
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

class RealGatewayBusinessIntelligenceAgent:
    """REAL agent using AgentCore Gateway - NO SIMULATION"""
    
    def __init__(self):
        # Real environment variables - REQUIRED
        self.gateway_id = "tacnodecontextlakegateway-bkq6ozcvxp"
        self.gateway_token = os.getenv('GATEWAY_TOKEN')  # AgentCore Gateway access token
        
        if not self.gateway_token:
            raise ValueError("❌ GATEWAY_TOKEN environment variable REQUIRED")
        
        self.gateway_endpoint = f"https://gateway-{self.gateway_id}.bedrock-agentcore.us-east-1.amazonaws.com"
        self.target_name = "tacnode-mcp-server"
        
        logger.info("🌉 REAL Gateway Business Intelligence Agent initialized")
        logger.info(f"   Gateway ID: {self.gateway_id}")
        logger.info(f"   Gateway Endpoint: {self.gateway_endpoint}")
        logger.info(f"   Target: {self.target_name}")
        logger.info("   🚫 NO SIMULATION - All calls go through AgentCore Gateway!")
    
    async def make_real_gateway_call(self, sql_query: str) -> Optional[Dict[str, Any]]:
        """Make REAL call through AgentCore Gateway"""
        try:
            logger.info("🌉 Making REAL call through AgentCore Gateway...")
            
            # Real MCP request
            mcp_request = {
                "jsonrpc": "2.0",
                "id": int(time.time()),
                "method": "tools/call",
                "params": {
                    "name": "query",
                    "arguments": {
                        "sql": sql_query
                    }
                }
            }
            
            # Real gateway target URL
            target_url = f"{self.gateway_endpoint}/targets/{self.target_name}/invoke"
            
            logger.info(f"   Target URL: {target_url}")
            logger.info(f"   SQL Query: {sql_query}")
            logger.info(f"   MCP Request: {json.dumps(mcp_request)}")
            
            # Real HTTP call to AgentCore Gateway
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    target_url,
                    json=mcp_request,
                    headers={
                        "Authorization": f"Bearer {self.gateway_token}",
                        "Content-Type": "application/json",
                        "User-Agent": "RealGatewayBusinessIntelligenceAgent/1.0"
                    }
                )
                
                logger.info(f"   Gateway Response Status: {response.status_code}")
                
                if response.status_code != 200:
                    logger.error(f"❌ Gateway call failed: {response.status_code} - {response.text}")
                    return None
                
                # Parse gateway response
                gateway_response = response.json()
                logger.info(f"   Gateway Response: {json.dumps(gateway_response)}")
                
                if 'result' in gateway_response and 'content' in gateway_response['result']:
                    # Extract real business data from gateway response
                    business_data_text = gateway_response['result']['content'][0]['text']
                    business_records = json.loads(business_data_text)
                    
                    logger.info(f"✅ Retrieved {len(business_records)} REAL records via AgentCore Gateway")
                    
                    return {
                        "records": business_records,
                        "source": "TACNode Context Lake via AgentCore Gateway (REAL)",
                        "method": "Real AgentCore Gateway → Lambda → TACNode",
                        "timestamp": datetime.now().isoformat(),
                        "query": sql_query
                    }
                else:
                    logger.error("❌ Invalid gateway response format")
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
        """Get REAL business data via AgentCore Gateway"""
        
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
        
        logger.info("📊 Fetching REAL business data via AgentCore Gateway...")
        return await self.make_real_gateway_call(sql_query.strip())
    
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
        """Process user question with REAL business data via gateway"""
        
        if self.should_access_business_data(user_question):
            logger.info(f"🧠 Business question detected: {user_question}")
            
            # Get REAL business data via AgentCore Gateway
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
🌉 METHOD: Real AgentCore Gateway → Lambda → TACNode
⏰ TIMESTAMP: {business_data['timestamp']}

This analysis uses REAL AgentCore Gateway integration - no shortcuts!"""
                
                return {
                    "message": response_message,
                    "data_accessed": True,
                    "gateway_used": True,
                    "records_analyzed": len(records),
                    "total_value": total_value,
                    "categories": categories,
                    "source": "TACNode Context Lake via AgentCore Gateway (REAL)",
                    "method": "Real AgentCore Gateway → Lambda → TACNode",
                    "timestamp": business_data['timestamp']
                }
            else:
                return {
                    "message": "❌ Unable to access REAL business data via AgentCore Gateway. Please check gateway configuration.",
                    "data_accessed": False,
                    "error": "Real gateway call failed"
                }
        else:
            # General response for non-business questions
            return {
                "message": "I'm a business intelligence agent that accesses REAL data via AgentCore Gateway. Ask me about business performance, metrics, or data analysis.",
                "data_accessed": False,
                "gateway_used": False
            }

# Test the REAL gateway agent
async def test_real_gateway_agent():
    """Test the REAL gateway agent"""
    print("🧪 TESTING REAL GATEWAY BUSINESS INTELLIGENCE AGENT")
    print("=" * 70)
    print("🚫 NO SIMULATION - All data via AgentCore Gateway!")
    
    try:
        agent = RealGatewayBusinessIntelligenceAgent()
        
        # Test business question
        test_question = "What is our total business value and which category is performing best?"
        print(f"\n❓ Test Question: {test_question}")
        
        result = await agent.process_user_question(test_question)
        
        print(f"\n📋 REAL GATEWAY AGENT RESPONSE:")
        print("-" * 50)
        print(result['message'])
        
        print(f"\n📊 METADATA:")
        print(f"   Data Accessed: {result['data_accessed']}")
        print(f"   Gateway Used: {result['gateway_used']}")
        print(f"   Records Analyzed: {result.get('records_analyzed', 0)}")
        print(f"   Source: {result.get('source', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    print("🌉 REAL Gateway Business Intelligence Agent")
    print("🚫 NO SIMULATION - All calls via AgentCore Gateway!")
    print("=" * 60)
    
    # Run test
    asyncio.run(test_real_gateway_agent())

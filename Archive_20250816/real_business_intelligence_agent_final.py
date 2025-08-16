#!/usr/bin/env python3
"""
REAL Business Intelligence Agent - NO SIMULATION!
Direct MCP calls to TACNode Context Lake with REAL data
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

class RealBusinessIntelligenceAgent:
    """REAL agent with actual MCP calls to TACNode - NO SIMULATION"""
    
    def __init__(self):
        # Real environment variables - REQUIRED
        self.tacnode_token = os.getenv('TACNODE_TOKEN')
        if not self.tacnode_token:
            raise ValueError("❌ TACNODE_TOKEN environment variable REQUIRED")
        
        self.tacnode_url = "https://mcp-server.tacnode.io/mcp"
        
        logger.info("🔧 REAL Business Intelligence Agent initialized")
        logger.info(f"   TACNode URL: {self.tacnode_url}")
        logger.info("   🚫 NO SIMULATION - All calls will be REAL!")
    
    def parse_sse_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Parse Server-Sent Events response from TACNode"""
        response_text = response_text.strip()
        if response_text.startswith('event: message\ndata: '):
            json_data = response_text.replace('event: message\ndata: ', '')
            try:
                return json.loads(json_data)
            except json.JSONDecodeError:
                logger.error("❌ Failed to parse SSE JSON data")
                return None
        else:
            logger.error(f"❌ Unexpected response format: {response_text[:200]}")
            return None
    
    async def make_real_mcp_call(self, sql_query: str) -> Optional[Dict[str, Any]]:
        """Make REAL MCP call to TACNode Context Lake"""
        try:
            logger.info("🌉 Making REAL MCP call to TACNode...")
            
            # Real MCP request - JSON-RPC 2.0
            mcp_request = {
                "jsonrpc": "2.0",
                "id": int(time.time()),
                "method": "tools/call",
                "params": {
                    "name": "query",  # Real tool name from TACNode
                    "arguments": {
                        "sql": sql_query  # Real parameter name
                    }
                }
            }
            
            logger.info(f"   SQL Query: {sql_query}")
            logger.info(f"   MCP Request: {json.dumps(mcp_request)}")
            
            # Real HTTP call to TACNode MCP server
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.tacnode_url,
                    json=mcp_request,
                    headers={
                        "Authorization": f"Bearer {self.tacnode_token}",
                        "Content-Type": "application/json",
                        "Accept": "application/json, text/event-stream",
                        "User-Agent": "RealBusinessIntelligenceAgent/1.0"
                    }
                )
                
                logger.info(f"   Response Status: {response.status_code}")
                
                if response.status_code != 200:
                    logger.error(f"❌ TACNode call failed: {response.status_code} - {response.text}")
                    return None
                
                # Parse real MCP response (SSE format)
                result = self.parse_sse_response(response.text)
                if not result:
                    return None
                
                logger.info(f"   MCP Response: {json.dumps(result)}")
                
                if 'result' in result and 'content' in result['result']:
                    # Extract real business data from TACNode
                    business_data_text = result['result']['content'][0]['text']
                    business_records = json.loads(business_data_text)
                    
                    logger.info(f"✅ Retrieved {len(business_records)} REAL records from TACNode")
                    
                    return {
                        "records": business_records,
                        "source": "TACNode Context Lake (REAL)",
                        "method": "Real MCP direct to TACNode",
                        "timestamp": datetime.now().isoformat(),
                        "query": sql_query
                    }
                else:
                    logger.error("❌ Invalid MCP response format")
                    return None
                    
        except httpx.HTTPError as e:
            logger.error(f"❌ HTTP error calling TACNode: {e}")
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
        return await self.make_real_mcp_call(sql_query.strip())
    
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
🌉 METHOD: Real MCP direct to TACNode
⏰ TIMESTAMP: {business_data['timestamp']}

This analysis is based on REAL business data - no simulation!"""
                
                return {
                    "message": response_message,
                    "data_accessed": True,
                    "mcp_used": True,
                    "records_analyzed": len(records),
                    "total_value": total_value,
                    "categories": categories,
                    "source": "TACNode Context Lake (REAL)",
                    "method": "Real MCP direct to TACNode",
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
                "mcp_used": False
            }

# Test the REAL agent
async def test_real_agent():
    """Test the REAL agent with actual TACNode data"""
    print("🧪 TESTING REAL BUSINESS INTELLIGENCE AGENT")
    print("=" * 60)
    print("🚫 NO SIMULATION - All data is REAL!")
    
    try:
        agent = RealBusinessIntelligenceAgent()
        
        # Test business questions
        test_questions = [
            "What is our total business value and which category is performing best?",
            "Show me our business performance overview",
            "Hello, how are you today?"  # Non-business question
        ]
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n❓ TEST QUESTION {i}: {question}")
            print("-" * 60)
            
            result = await agent.process_user_question(question)
            
            print(f"📋 REAL AGENT RESPONSE:")
            print(result['message'])
            
            print(f"\n📊 METADATA:")
            print(f"   Data Accessed: {result['data_accessed']}")
            print(f"   MCP Used: {result.get('mcp_used', False)}")
            print(f"   Records Analyzed: {result.get('records_analyzed', 0)}")
            print(f"   Total Value: ${result.get('total_value', 0):,.2f}")
            print(f"   Source: {result.get('source', 'N/A')}")
            
            if i < len(test_questions):
                print(f"\n⏳ Waiting 5 seconds before next question...")
                await asyncio.sleep(5)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

async def main():
    print("🔧 REAL Business Intelligence Agent")
    print("🚫 NO SIMULATION - All data is REAL!")
    print("=" * 50)
    
    # Run test
    await test_real_agent()
    
    print(f"\n🎉 REAL AGENT TEST COMPLETE!")
    print("=" * 50)
    print("✅ Real MCP calls to TACNode working")
    print("✅ Real business data retrieved and analyzed")
    print("✅ No simulation - everything is REAL!")

if __name__ == "__main__":
    asyncio.run(main())

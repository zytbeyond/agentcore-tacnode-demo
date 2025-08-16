#!/usr/bin/env python3
"""
REAL Business Intelligence Agent with Direct MCP Integration
Uses TACNode MCP directly - exactly like the image shows
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

class RealDirectMCPBusinessIntelligenceAgent:
    """REAL agent using direct MCP calls - like the image shows"""
    
    def __init__(self):
        # Real environment variables - REQUIRED
        self.tacnode_token = os.getenv('TACNODE_TOKEN')
        
        if not self.tacnode_token:
            raise ValueError("❌ TACNODE_TOKEN environment variable REQUIRED")
        
        self.mcp_endpoint = "https://mcp-server.tacnode.io/mcp"
        
        logger.info("🌐 REAL Direct MCP Business Intelligence Agent initialized")
        logger.info(f"   MCP Endpoint: {self.mcp_endpoint}")
        logger.info("   🚫 NO LAMBDA - Direct MCP calls like the image!")
    
    async def make_real_mcp_call(self, sql_query: str) -> Optional[Dict[str, Any]]:
        """Make REAL MCP call directly to TACNode"""
        try:
            logger.info("🌐 Making REAL MCP call to TACNode...")
            
            # Real MCP request - exactly like the documentation
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
            
            logger.info(f"   MCP Endpoint: {self.mcp_endpoint}")
            logger.info(f"   SQL Query: {sql_query}")
            logger.info(f"   MCP Request: {json.dumps(mcp_request)}")
            
            # Real HTTP call to TACNode MCP
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.mcp_endpoint,
                    json=mcp_request,
                    headers={
                        "Authorization": f"Bearer {self.tacnode_token}",
                        "Content-Type": "application/json",
                        "Accept": "application/json, text/event-stream",
                        "User-Agent": "RealDirectMCPBusinessIntelligenceAgent/1.0"
                    }
                )
                
                logger.info(f"   MCP Response Status: {response.status_code}")
                
                if response.status_code != 200:
                    logger.error(f"❌ MCP call failed: {response.status_code} - {response.text}")
                    return None
                
                # Parse MCP response (handles SSE format)
                response_text = response.text.strip()
                logger.info(f"   Raw MCP Response: {response_text[:200]}...")
                
                if response_text.startswith('event: message\ndata: '):
                    # Parse SSE format
                    json_data = response_text.replace('event: message\ndata: ', '')
                    mcp_response = json.loads(json_data)
                else:
                    # Parse direct JSON
                    mcp_response = response.json()
                
                logger.info(f"   Parsed MCP Response: {json.dumps(mcp_response)}")
                
                if 'result' in mcp_response and 'content' in mcp_response['result']:
                    # Extract business records from MCP response
                    business_data_text = mcp_response['result']['content'][0]['text']
                    business_records = json.loads(business_data_text)
                    
                    logger.info(f"✅ Retrieved {len(business_records)} REAL records via direct MCP")
                    
                    return {
                        "records": business_records,
                        "source": "TACNode Context Lake via Direct MCP (REAL)",
                        "method": "Direct MCP call to TACNode",
                        "timestamp": datetime.now().isoformat(),
                        "query": sql_query
                    }
                else:
                    logger.error("❌ Invalid MCP response format")
                    return None
                    
        except httpx.HTTPError as e:
            logger.error(f"❌ HTTP error calling TACNode MCP: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON decode error: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return None
    
    async def get_real_business_data(self, query_context: str) -> Optional[Dict[str, Any]]:
        """Get REAL business data via direct MCP"""
        
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
        
        logger.info("📊 Fetching REAL business data via direct MCP...")
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
        """Process user question with REAL business data via direct MCP"""
        
        if self.should_access_business_data(user_question):
            logger.info(f"🧠 Business question detected: {user_question}")
            
            # Get REAL business data via direct MCP
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
                response_message = f"""Based on REAL-TIME data via Direct MCP:

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
🌐 METHOD: Direct MCP call to TACNode
⏰ TIMESTAMP: {business_data['timestamp']}

This analysis uses REAL direct MCP integration - exactly like the image shows!"""
                
                return {
                    "message": response_message,
                    "data_accessed": True,
                    "direct_mcp_used": True,
                    "records_analyzed": len(records),
                    "total_value": total_value,
                    "categories": categories,
                    "source": "TACNode Context Lake via Direct MCP (REAL)",
                    "method": "Direct MCP call to TACNode",
                    "timestamp": business_data['timestamp']
                }
            else:
                return {
                    "message": "❌ Unable to access REAL business data via direct MCP. Please check MCP configuration.",
                    "data_accessed": False,
                    "error": "Real MCP call failed"
                }
        else:
            # General response for non-business questions
            return {
                "message": "I'm a business intelligence agent that accesses REAL data via direct MCP. Ask me about business performance, metrics, or data analysis.",
                "data_accessed": False,
                "direct_mcp_used": False
            }

# Test the REAL direct MCP agent
async def test_real_direct_mcp_agent():
    """Test the REAL direct MCP agent"""
    print("🧪 TESTING REAL DIRECT MCP BUSINESS INTELLIGENCE AGENT")
    print("=" * 70)
    print("🚫 NO LAMBDA - Direct MCP calls like the image!")
    
    try:
        agent = RealDirectMCPBusinessIntelligenceAgent()
        
        # Test business question
        test_question = "What is our total business value and which category is performing best?"
        print(f"\n❓ Test Question: {test_question}")
        
        result = await agent.process_user_question(test_question)
        
        print(f"\n📋 REAL DIRECT MCP AGENT RESPONSE:")
        print("-" * 50)
        print(result['message'])
        
        print(f"\n📊 METADATA:")
        print(f"   Data Accessed: {result['data_accessed']}")
        print(f"   Direct MCP Used: {result['direct_mcp_used']}")
        print(f"   Records Analyzed: {result.get('records_analyzed', 0)}")
        print(f"   Source: {result.get('source', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    print("🌐 REAL Direct MCP Business Intelligence Agent")
    print("🚫 NO LAMBDA - Direct MCP calls like the image!")
    print("=" * 60)
    
    # Run test
    asyncio.run(test_real_direct_mcp_agent())

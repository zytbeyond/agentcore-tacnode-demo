#!/usr/bin/env python3
"""
Test REAL TACNode MCP Connection - NO SIMULATION!
Direct test of MCP calls to TACNode Context Lake
"""

import asyncio
import httpx
import json
import os
import time
from datetime import datetime

class RealTACNodeMCPTester:
    """Test real MCP connection to TACNode Context Lake"""
    
    def __init__(self):
        self.tacnode_token = os.getenv('TACNODE_TOKEN')
        if not self.tacnode_token:
            raise ValueError("❌ TACNODE_TOKEN environment variable REQUIRED")
        
        self.tacnode_url = "https://mcp-server.tacnode.io/mcp"
        
        print("🧪 REAL TACNODE MCP CONNECTION TESTER")
        print("=" * 60)
        print("✅ TACNode Token: Available")
        print(f"✅ TACNode URL: {self.tacnode_url}")
        print("🚫 NO SIMULATION - Testing REAL connection!")
    
    async def test_mcp_tools_list(self):
        """Test MCP tools/list call"""
        print("\n📋 TEST 1: MCP tools/list")
        print("-" * 40)
        
        try:
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
                "params": {}
            }
            
            print(f"Request: {json.dumps(mcp_request)}")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.tacnode_url,
                    json=mcp_request,
                    headers={
                        "Authorization": f"Bearer {self.tacnode_token}",
                        "Content-Type": "application/json",
                        "Accept": "application/json, text/event-stream",
                        "User-Agent": "RealTACNodeTester/1.0"
                    }
                )
                
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")

                    # Parse SSE format
                    response_text = response.text.strip()
                    if response_text.startswith('event: message\ndata: '):
                        json_data = response_text.replace('event: message\ndata: ', '')
                        try:
                            result = json.loads(json_data)
                            print("✅ tools/list SUCCESS!")
                            print(f"Response: {json.dumps(result, indent=2)}")
                        except json.JSONDecodeError:
                            print("❌ Failed to parse SSE JSON data")
                            return False
                    else:
                        print(f"❌ Unexpected response format: {response_text[:200]}")
                        return False
                    
                    if 'result' in result and 'tools' in result['result']:
                        tools = result['result']['tools']
                        print(f"\n📊 Available Tools ({len(tools)}):")
                        for tool in tools:
                            print(f"   • {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
                    
                    return True
                else:
                    print(f"❌ tools/list FAILED: {response.status_code}")
                    print(f"Error: {response.text}")
                    return False
                    
        except Exception as e:
            print(f"❌ tools/list ERROR: {e}")
            return False
    
    async def test_mcp_execute_sql(self):
        """Test MCP execute_sql call"""
        print("\n📋 TEST 2: MCP execute_sql")
        print("-" * 40)
        
        try:
            # Test simple count query
            sql_query = "SELECT COUNT(*) as record_count FROM test WHERE is_active = true"
            
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "query",
                    "arguments": {
                        "sql": sql_query
                    }
                }
            }
            
            print(f"SQL Query: {sql_query}")
            print(f"Request: {json.dumps(mcp_request)}")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.tacnode_url,
                    json=mcp_request,
                    headers={
                        "Authorization": f"Bearer {self.tacnode_token}",
                        "Content-Type": "application/json",
                        "Accept": "application/json, text/event-stream",
                        "User-Agent": "RealTACNodeTester/1.0"
                    }
                )
                
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    # Parse SSE format
                    response_text = response.text.strip()
                    if response_text.startswith('event: message\ndata: '):
                        json_data = response_text.replace('event: message\ndata: ', '')
                        try:
                            result = json.loads(json_data)
                            print("✅ query SUCCESS!")
                            print(f"Response: {json.dumps(result, indent=2)}")
                        except json.JSONDecodeError:
                            print("❌ Failed to parse SSE JSON data")
                            return False
                    else:
                        print(f"❌ Unexpected response format: {response_text[:200]}")
                        return False
                    
                    if 'result' in result and 'content' in result['result']:
                        content = result['result']['content'][0]['text']
                        data = json.loads(content)
                        print(f"\n📊 Query Result:")
                        print(f"   Record Count: {data[0]['record_count']}")
                    
                    return True
                else:
                    print(f"❌ execute_sql FAILED: {response.status_code}")
                    print(f"Error: {response.text}")
                    return False
                    
        except Exception as e:
            print(f"❌ execute_sql ERROR: {e}")
            return False
    
    async def test_real_business_data(self):
        """Test getting real business data"""
        print("\n📋 TEST 3: Real Business Data Query")
        print("-" * 40)
        
        try:
            # Real business data query
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
            LIMIT 5
            """
            
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "query",
                    "arguments": {
                        "sql": sql_query.strip()
                    }
                }
            }
            
            print(f"Business Data Query:")
            print(sql_query.strip())
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.tacnode_url,
                    json=mcp_request,
                    headers={
                        "Authorization": f"Bearer {self.tacnode_token}",
                        "Content-Type": "application/json",
                        "Accept": "application/json, text/event-stream",
                        "User-Agent": "RealTACNodeTester/1.0"
                    }
                )
                
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    # Parse SSE format
                    response_text = response.text.strip()
                    if response_text.startswith('event: message\ndata: '):
                        json_data = response_text.replace('event: message\ndata: ', '')
                        try:
                            result = json.loads(json_data)
                            print("✅ Business Data Query SUCCESS!")

                            if 'result' in result and 'content' in result['result']:
                                content = result['result']['content'][0]['text']
                                business_records = json.loads(content)

                                print(f"\n📊 REAL Business Records ({len(business_records)}):")
                                total_value = 0

                                for record in business_records:
                                    value = float(record.get('value', 0))
                                    total_value += value
                                    print(f"   • ID {record['id']}: {record['name']} = ${value:,.2f} ({record['category']})")

                                print(f"\n💰 Total Value: ${total_value:,.2f}")
                                print(f"📅 Data Source: TACNode Context Lake (PostgreSQL)")
                                print(f"⏰ Retrieved: {datetime.now().isoformat()}")

                                return {
                                    "records": business_records,
                                    "total_value": total_value,
                                    "record_count": len(business_records),
                                    "source": "TACNode Context Lake (REAL)"
                                }
                            else:
                                print("❌ No business data in response")
                                return None
                        except json.JSONDecodeError:
                            print("❌ Failed to parse SSE JSON data")
                            return None
                    else:
                        print(f"❌ Unexpected response format: {response_text[:200]}")
                        return None
                else:
                    print(f"❌ Business Data Query FAILED: {response.status_code}")
                    print(f"Error: {response.text}")
                    return None
                    
        except Exception as e:
            print(f"❌ Business Data Query ERROR: {e}")
            return None
    
    async def run_complete_test(self):
        """Run complete MCP connection test"""
        print("🧪 COMPLETE REAL TACNODE MCP TEST")
        print("=" * 60)
        print("🚫 NO SIMULATION - Testing REAL MCP connection!")
        
        results = {
            "tools_list": False,
            "execute_sql": False,
            "business_data": None
        }
        
        # Test 1: tools/list
        results["tools_list"] = await self.test_mcp_tools_list()
        
        # Test 2: execute_sql
        results["execute_sql"] = await self.test_mcp_execute_sql()
        
        # Test 3: Real business data
        results["business_data"] = await self.test_real_business_data()
        
        # Summary
        print(f"\n🎯 TEST RESULTS SUMMARY")
        print("=" * 40)
        print(f"✅ tools/list: {'PASS' if results['tools_list'] else 'FAIL'}")
        print(f"✅ execute_sql: {'PASS' if results['execute_sql'] else 'FAIL'}")
        print(f"✅ business_data: {'PASS' if results['business_data'] else 'FAIL'}")
        
        if all([results["tools_list"], results["execute_sql"], results["business_data"]]):
            print(f"\n🎉 ALL TESTS PASSED!")
            print(f"   TACNode MCP connection is REAL and working")
            print(f"   Business data access confirmed")
            print(f"   Ready for AgentCore Gateway integration")
            
            if results["business_data"]:
                data = results["business_data"]
                print(f"\n📊 REAL DATA SUMMARY:")
                print(f"   Records: {data['record_count']}")
                print(f"   Total Value: ${data['total_value']:,.2f}")
                print(f"   Source: {data['source']}")
            
            return True
        else:
            print(f"\n❌ SOME TESTS FAILED")
            print(f"   Check TACNode token and network connectivity")
            return False

async def main():
    print("🧪 REAL TACNode MCP Connection Test")
    print("🚫 NO SIMULATION - Testing REAL connection!")
    print("=" * 60)
    
    try:
        tester = RealTACNodeMCPTester()
        success = await tester.run_complete_test()
        
        if success:
            print("\n✅ TACNode MCP connection verified!")
            print("   Ready to integrate with AgentCore Gateway")
        else:
            print("\n❌ TACNode MCP connection failed!")
            print("   Check configuration and try again")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())

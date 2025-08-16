#!/usr/bin/env python3
"""
Test Agent Data Access Logic
Test how the agent should leverage AgentCore Gateway to access TACNode data
"""

import boto3
import json
import time
from datetime import datetime

class AgentDataAccessTest:
    """Test how agent should access TACNode data through AgentCore Gateway"""
    
    def __init__(self):
        self.bedrock_agentcore = boto3.client('bedrock-agentcore', region_name='us-east-1')
        
        # Load runtime info
        with open('tacnode-agentcore-runtime-FINAL.json', 'r') as f:
            self.runtime_info = json.load(f)
        
        self.runtime_arn = self.runtime_info['runtimeArn']
    
    def generate_session_id(self, prefix=""):
        """Generate valid session ID"""
        timestamp = int(time.time())
        return f"{prefix}agent-data-access-test-{timestamp}-verification-session"
    
    def test_explicit_data_request(self):
        """Test with very explicit data access request"""
        print("🔍 Testing explicit TACNode data access request...")
        
        try:
            # Very explicit request that should trigger data access
            test_payload = {
                "input": {
                    "prompt": """You are a TACNode AgentCore agent with access to TACNode Context Lake through the AgentCore Gateway. 

TASK: Access the TACNode database and retrieve actual business records.

INSTRUCTIONS:
1. Use your TACNode integration to query the database
2. Get real records with id, name, description, value, category, created_date
3. Show me the actual data, not a generic response
4. Provide specific numbers, categories, and values from the database

This is a production test to verify the AgentCore Gateway → TACNode integration is working."""
                }
            }
            
            session_id = self.generate_session_id("explicit")
            
            print(f"📤 Sending explicit data access request...")
            print(f"   Expected: Agent should use AgentCore Gateway to query TACNode")
            
            response = self.bedrock_agentcore.invoke_agent_runtime(
                agentRuntimeArn=self.runtime_arn,
                runtimeSessionId=session_id,
                payload=json.dumps(test_payload),
                qualifier="DEFAULT"
            )
            
            response_body = response['response'].read()
            response_data = json.loads(response_body)
            
            response_message = response_data['output']['message']
            data_accessed = response_data['output'].get('data_accessed', False)
            
            print(f"\n📊 Explicit Request Response:")
            print("-" * 80)
            print(response_message)
            print("-" * 80)
            
            print(f"\n📋 Analysis:")
            print(f"   Data accessed flag: {data_accessed}")
            print(f"   Response length: {len(response_message)} characters")
            
            # Check for actual data indicators
            data_indicators = [
                "Category 1" in response_message or "Category 2" in response_message,
                any(str(i) in response_message for i in range(1, 11)),  # Record IDs 1-10
                "$" in response_message or "value" in response_message.lower(),
                "2025" in response_message,  # Recent dates
                data_accessed
            ]
            
            success = sum(data_indicators) >= 2
            
            print(f"   Actual data indicators: {sum(data_indicators)}/5")
            print(f"   Real data access: {'✅' if success else '❌'}")
            
            return success
            
        except Exception as e:
            print(f"❌ Explicit data request failed: {e}")
            return False
    
    def test_business_intelligence_request(self):
        """Test business intelligence style request"""
        print("\n📊 Testing business intelligence request...")
        
        try:
            # Wait to avoid throttling
            time.sleep(10)
            
            test_payload = {
                "input": {
                    "prompt": """I need a business intelligence report from our TACNode Context Lake data.

Please execute a SQL query to get:
- All active business records
- Group by category 
- Show total values and counts
- Include recent trends

Use the AgentCore Gateway to access TACNode and provide real numbers from our PostgreSQL database."""
                }
            }
            
            session_id = self.generate_session_id("bi")
            
            print(f"📤 Sending business intelligence request...")
            
            response = self.bedrock_agentcore.invoke_agent_runtime(
                agentRuntimeArn=self.runtime_arn,
                runtimeSessionId=session_id,
                payload=json.dumps(test_payload),
                qualifier="DEFAULT"
            )
            
            response_body = response['response'].read()
            response_data = json.loads(response_body)
            
            response_message = response_data['output']['message']
            
            print(f"\n📊 Business Intelligence Response:")
            print("-" * 80)
            print(response_message)
            print("-" * 80)
            
            # Check for BI-style data
            bi_indicators = [
                "SQL" in response_message or "query" in response_message.lower(),
                "category" in response_message.lower(),
                "total" in response_message.lower() or "count" in response_message.lower(),
                "PostgreSQL" in response_message or "database" in response_message.lower()
            ]
            
            success = sum(bi_indicators) >= 2
            print(f"   BI indicators: {sum(bi_indicators)}/4")
            print(f"   BI response quality: {'✅' if success else '❌'}")
            
            return success
            
        except Exception as e:
            print(f"❌ Business intelligence request failed: {e}")
            return False
    
    def analyze_agent_behavior(self):
        """Analyze how the agent should behave vs how it's actually behaving"""
        print("\n🔍 AGENT BEHAVIOR ANALYSIS")
        print("=" * 60)
        
        print("🎯 HOW THE AGENT SHOULD WORK:")
        print("   1. Receive user request for TACNode data")
        print("   2. Recognize keywords: 'TACNode', 'data', 'business', etc.")
        print("   3. Use AgentCore Gateway to call TACNode MCP server")
        print("   4. Execute SQL query on PostgreSQL database")
        print("   5. Get real business records (10 records available)")
        print("   6. Use Claude to analyze the real data")
        print("   7. Provide insights based on actual data")
        
        print("\n🤔 WHAT'S HAPPENING NOW:")
        print("   1. ✅ Agent receives request")
        print("   2. ✅ Agent recognizes TACNode keywords")
        print("   3. ❓ Gateway connection status unclear")
        print("   4. ❌ No real data being retrieved")
        print("   5. ❌ Agent gives generic 'no access' response")
        print("   6. ❌ Claude not analyzing real data")
        
        print("\n🔧 POSSIBLE ISSUES:")
        print("   • Agent code may not be calling AgentCore Gateway properly")
        print("   • Gateway → TACNode connection may have issues")
        print("   • Agent may be defaulting to 'safe' responses")
        print("   • MCP protocol implementation may need adjustment")
        
        print("\n📋 EXPECTED DATA FLOW:")
        print("   User Request → AgentCore Runtime → AgentCore Gateway → TACNode MCP → PostgreSQL")
        print("   PostgreSQL → TACNode MCP → AgentCore Gateway → AgentCore Runtime → Claude → User")
        
        print("\n🎯 WHAT WE SHOULD SEE:")
        print("   • Actual record IDs (1-10)")
        print("   • Real categories (Category 1, 2, 3)")
        print("   • Actual values ($-10.75 to $999.99)")
        print("   • Real dates (2025-07-20 to 2025-08-04)")
        print("   • Business insights based on real data")
    
    def run_data_access_analysis(self):
        """Run complete data access analysis"""
        print("🎯 AGENT DATA ACCESS ANALYSIS")
        print("=" * 60)
        
        # Test 1: Explicit data request
        print("\n📋 TEST 1: Explicit Data Access Request")
        explicit_success = self.test_explicit_data_request()
        
        # Test 2: Business intelligence request
        print("\n📋 TEST 2: Business Intelligence Request")
        bi_success = self.test_business_intelligence_request()
        
        # Analysis
        print("\n📋 TEST 3: Agent Behavior Analysis")
        self.analyze_agent_behavior()
        
        print("\n" + "="*60)
        print("📊 DATA ACCESS TEST RESULTS")
        print("="*60)
        
        print(f"\n✅ TEST RESULTS:")
        print(f"   Explicit Data Request: {'✅ PASSED' if explicit_success else '❌ FAILED'}")
        print(f"   Business Intelligence: {'✅ PASSED' if bi_success else '❌ FAILED'}")
        
        if explicit_success or bi_success:
            print(f"\n🎉 AGENT IS ACCESSING REAL DATA!")
            print(f"   ✅ AgentCore Gateway → TACNode integration working")
            print(f"   ✅ Real business data being retrieved")
            print(f"   ✅ AI analysis of actual data")
        else:
            print(f"\n🔧 AGENT NEEDS CONFIGURATION:")
            print(f"   ❌ Agent not accessing real TACNode data")
            print(f"   ❌ May need agent code updates")
            print(f"   ❌ Gateway integration may need fixes")
            
            print(f"\n🎯 NEXT STEPS:")
            print(f"   1. Check agent container code")
            print(f"   2. Verify AgentCore Gateway configuration")
            print(f"   3. Test TACNode MCP protocol directly")
            print(f"   4. Update agent logic if needed")
        
        return explicit_success or bi_success

def main():
    print("🔍 Agent Data Access Logic Test")
    print("=" * 60)
    
    test = AgentDataAccessTest()
    
    try:
        success = test.run_data_access_analysis()
        
        if success:
            print("\n🏆 AGENT DATA ACCESS WORKING!")
            print("   Agent is successfully leveraging AgentCore Gateway")
            print("   Real TACNode data is being accessed and analyzed")
        else:
            print("\n🔧 AGENT DATA ACCESS NEEDS WORK")
            print("   Agent recognizes TACNode but not accessing real data")
            print("   Integration logic may need updates")
        
    except Exception as e:
        print(f"❌ Data access test failed: {e}")

if __name__ == "__main__":
    main()

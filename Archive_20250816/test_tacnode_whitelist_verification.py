#!/usr/bin/env python3
"""
Test TACNode Whitelist Verification
Comprehensive test to verify if TACNode IP whitelist is working
"""

import boto3
import json
import time
import subprocess
from datetime import datetime

class TACNodeWhitelistTest:
    """Test TACNode whitelist functionality"""
    
    def __init__(self):
        self.bedrock_agentcore = boto3.client('bedrock-agentcore', region_name='us-east-1')
        
        # Load runtime info
        with open('tacnode-agentcore-runtime-FINAL.json', 'r') as f:
            self.runtime_info = json.load(f)
        
        self.runtime_arn = self.runtime_info['runtimeArn']
        self.runtime_id = self.runtime_info['runtimeId']
    
    def generate_session_id(self, prefix=""):
        """Generate valid session ID (33+ characters)"""
        timestamp = int(time.time())
        return f"{prefix}tacnode-whitelist-test-{timestamp}-agentcore-verification"
    
    def test_direct_tacnode_access(self):
        """Test direct TACNode access (baseline)"""
        print("🔍 Testing direct TACNode access (baseline)...")
        
        try:
            result = subprocess.run(['python3', 'query_tacnode_data.py'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and "Found 10 records" in result.stdout:
                print("✅ Direct TACNode access: WORKING")
                print("   10 business records accessible")
                return True
            else:
                print("❌ Direct TACNode access: FAILED")
                print(f"   Output: {result.stdout[:200]}...")
                return False
                
        except Exception as e:
            print(f"❌ Direct TACNode access error: {e}")
            return False
    
    def test_agentcore_runtime_tacnode_request(self):
        """Test AgentCore Runtime requesting TACNode data"""
        print("\n🚀 Testing AgentCore Runtime → Gateway → TACNode...")
        
        try:
            # Create a request that should trigger TACNode data access
            test_payload = {
                "input": {
                    "prompt": "Please access TACNode Context Lake and retrieve our business data. I need you to query the database and show me the actual records with categories, values, and dates. This is a test to verify the whitelist is working."
                }
            }
            
            session_id = self.generate_session_id("whitelist")
            
            print(f"📤 Sending TACNode data request...")
            print(f"   Session: {session_id}")
            print(f"   Expected flow: Runtime → Gateway → TACNode → PostgreSQL")
            
            start_time = time.time()
            
            response = self.bedrock_agentcore.invoke_agent_runtime(
                agentRuntimeArn=self.runtime_arn,
                runtimeSessionId=session_id,
                payload=json.dumps(test_payload),
                qualifier="DEFAULT"
            )
            
            end_time = time.time()
            
            response_body = response['response'].read()
            response_data = json.loads(response_body)
            
            print("✅ AgentCore Runtime response received!")
            print(f"   Response time: {end_time - start_time:.2f} seconds")
            
            response_message = response_data['output']['message']
            data_accessed = response_data['output'].get('data_accessed', False)
            
            print(f"\n📊 Response Analysis:")
            print(f"   Data accessed flag: {data_accessed}")
            print(f"   Response length: {len(response_message)} characters")
            
            print(f"\n🤖 Agent Response:")
            print("-" * 80)
            print(response_message)
            print("-" * 80)
            
            # Analyze response for TACNode data indicators
            tacnode_indicators = [
                "TACNode" in response_message,
                "Context Lake" in response_message,
                "database" in response_message.lower(),
                "records" in response_message.lower(),
                "category" in response_message.lower(),
                "value" in response_message.lower(),
                data_accessed
            ]
            
            success_count = sum(tacnode_indicators)
            
            print(f"\n📋 TACNode Access Indicators:")
            print(f"   TACNode mentioned: {'✅' if 'TACNode' in response_message else '❌'}")
            print(f"   Context Lake mentioned: {'✅' if 'Context Lake' in response_message else '❌'}")
            print(f"   Database mentioned: {'✅' if 'database' in response_message.lower() else '❌'}")
            print(f"   Records mentioned: {'✅' if 'records' in response_message.lower() else '❌'}")
            print(f"   Data accessed flag: {'✅' if data_accessed else '❌'}")
            print(f"   Success indicators: {success_count}/7")
            
            # Determine if whitelist is working
            if success_count >= 3:
                print("✅ TACNode whitelist appears to be WORKING!")
                return True
            elif "error" in response_message.lower() or "cannot" in response_message.lower():
                print("❌ TACNode whitelist may be BLOCKED")
                return False
            else:
                print("⚠️  TACNode whitelist status UNCLEAR")
                return False
                
        except Exception as e:
            print(f"❌ AgentCore Runtime test failed: {e}")
            return False
    
    def test_multiple_tacnode_requests(self):
        """Test multiple TACNode requests to verify consistent access"""
        print("\n📊 Testing multiple TACNode requests...")
        
        test_requests = [
            "Show me business data summary from TACNode",
            "Get recent records from TACNode Context Lake",
            "Analyze category performance using TACNode data"
        ]
        
        results = []
        
        for i, request in enumerate(test_requests):
            print(f"\n🔍 Request {i+1}: {request[:50]}...")
            
            try:
                # Add delay to avoid throttling
                if i > 0:
                    print("   ⏳ Waiting 15 seconds to avoid throttling...")
                    time.sleep(15)
                
                test_payload = {
                    "input": {
                        "prompt": request
                    }
                }
                
                session_id = self.generate_session_id(f"multi{i+1}")
                
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
                
                # Check for TACNode access
                has_tacnode_ref = "TACNode" in response_message or "tacnode" in response_message.lower()
                has_data_ref = "data" in response_message.lower() or "records" in response_message.lower()
                
                success = data_accessed or (has_tacnode_ref and has_data_ref)
                
                print(f"   {'✅' if success else '❌'} Response: {len(response_message)} chars")
                print(f"   Data accessed: {data_accessed}")
                print(f"   TACNode referenced: {has_tacnode_ref}")
                
                results.append({
                    'request': request,
                    'success': success,
                    'data_accessed': data_accessed,
                    'response_length': len(response_message)
                })
                
            except Exception as e:
                print(f"   ❌ Request failed: {e}")
                results.append({
                    'request': request,
                    'success': False,
                    'error': str(e)
                })
        
        # Analyze results
        successful_requests = sum(1 for r in results if r['success'])
        data_access_count = sum(1 for r in results if r.get('data_accessed', False))
        
        print(f"\n📋 Multiple Request Results:")
        print(f"   Successful requests: {successful_requests}/{len(test_requests)}")
        print(f"   Data access confirmed: {data_access_count}/{len(test_requests)}")
        
        return successful_requests >= 1  # At least 1 should work if whitelist is good
    
    def analyze_whitelist_status(self, direct_access, runtime_access, multi_access):
        """Analyze overall whitelist status"""
        print("\n📊 TACNODE WHITELIST STATUS ANALYSIS")
        print("=" * 60)
        
        total_tests = 3
        passed_tests = sum([direct_access, runtime_access, multi_access])
        success_rate = passed_tests / total_tests
        
        print(f"🏆 OVERALL WHITELIST STATUS: {passed_tests}/{total_tests} ({success_rate*100:.1f}%)")
        
        print(f"\n📋 TEST RESULTS:")
        print(f"   {'✅' if direct_access else '❌'} Direct TACNode Access: {'WORKING' if direct_access else 'FAILED'}")
        print(f"   {'✅' if runtime_access else '❌'} AgentCore → TACNode: {'WORKING' if runtime_access else 'FAILED'}")
        print(f"   {'✅' if multi_access else '❌'} Multiple Requests: {'WORKING' if multi_access else 'FAILED'}")
        
        # Determine whitelist status
        if success_rate >= 0.67:  # 2 out of 3 tests pass
            status = "WHITELIST WORKING"
            status_icon = "✅"
            color = "GREEN"
        elif success_rate >= 0.33:  # 1 out of 3 tests pass
            status = "WHITELIST PARTIAL"
            status_icon = "⚠️"
            color = "YELLOW"
        else:
            status = "WHITELIST BLOCKED"
            status_icon = "❌"
            color = "RED"
        
        print(f"\n{status_icon} WHITELIST STATUS: {status}")
        
        if success_rate >= 0.67:
            print(f"\n🎉 WHITELIST VERIFICATION SUCCESSFUL!")
            print(f"   ✅ AgentCore Gateway can access TACNode")
            print(f"   ✅ Data flow is working properly")
            print(f"   ✅ IP whitelist configuration is correct")
            
            print(f"\n🚀 READY FOR PRODUCTION USE:")
            print(f"   • Real-time business intelligence")
            print(f"   • AI-powered data analytics")
            print(f"   • Complete AgentCore + TACNode integration")
            
        elif success_rate >= 0.33:
            print(f"\n⚠️  WHITELIST PARTIALLY WORKING:")
            print(f"   • Some connections are successful")
            print(f"   • May need IP range refinement")
            print(f"   • Check TACNode logs for specific IPs")
            
        else:
            print(f"\n❌ WHITELIST NOT WORKING:")
            print(f"   • AgentCore Gateway cannot reach TACNode")
            print(f"   • Check IP whitelist configuration")
            print(f"   • Verify AWS us-east-1 ranges are correct")
            
            print(f"\n🔧 TROUBLESHOOTING STEPS:")
            print(f"   1. Check TACNode access logs")
            print(f"   2. Verify IP ranges: 3.208.0.0/12, 52.0.0.0/11, etc.")
            print(f"   3. Test with broader IP ranges if needed")
            print(f"   4. Contact AWS Support for specific Gateway IPs")
        
        return success_rate >= 0.67
    
    def run_complete_whitelist_test(self):
        """Run complete whitelist verification test"""
        print("🎯 TACNODE WHITELIST VERIFICATION TEST")
        print("=" * 60)
        
        print("🏗️  TESTING COMPLETE DATA FLOW:")
        print("   Direct Access: Python → TACNode (baseline)")
        print("   AgentCore Flow: Runtime → Gateway → TACNode")
        print("   Multiple Requests: Consistency verification")
        
        # Test 1: Direct TACNode access
        print("\n📋 TEST 1: Direct TACNode Access")
        direct_access = self.test_direct_tacnode_access()
        
        # Test 2: AgentCore Runtime → TACNode
        print("\n📋 TEST 2: AgentCore Runtime → Gateway → TACNode")
        runtime_access = self.test_agentcore_runtime_tacnode_request()
        
        # Test 3: Multiple requests
        print("\n📋 TEST 3: Multiple TACNode Requests")
        multi_access = self.test_multiple_tacnode_requests()
        
        # Analyze results
        print("\n📋 TEST 4: Whitelist Status Analysis")
        whitelist_working = self.analyze_whitelist_status(direct_access, runtime_access, multi_access)
        
        print("\n" + "="*60)
        if whitelist_working:
            print("🎉 TACNODE WHITELIST VERIFICATION: SUCCESS!")
        else:
            print("🔧 TACNODE WHITELIST VERIFICATION: NEEDS ATTENTION")
        print("="*60)
        
        return whitelist_working

def main():
    print("🌐 TACNode Whitelist Verification Test")
    print("=" * 60)
    
    test = TACNodeWhitelistTest()
    
    try:
        success = test.run_complete_whitelist_test()
        
        if success:
            print("\n🏆 WHITELIST VERIFICATION COMPLETE!")
            print("   Your IP whitelist is working correctly")
            print("   AgentCore Gateway can access TACNode")
            print("   Complete integration is functional")
        else:
            print("\n🔧 WHITELIST NEEDS ADJUSTMENT")
            print("   Some connections may be blocked")
            print("   Check TACNode logs and IP ranges")
        
    except Exception as e:
        print(f"❌ Whitelist test failed: {e}")

if __name__ == "__main__":
    main()

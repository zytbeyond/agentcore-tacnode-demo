#!/usr/bin/env python3
"""
Test AgentCore Runtime to Identify Source IP
Invoke the AgentCore Runtime to trigger gateway → TACNode connection
This will help identify the source IP that TACNode sees
"""

import boto3
import json
import time
from datetime import datetime

class AgentCoreRuntimeTester:
    """Test AgentCore Runtime to identify source IP for TACNode whitelist"""
    
    def __init__(self):
        self.bedrock_agentcore = boto3.client('bedrock-agentcore', region_name='us-east-1')
        self.bedrock_agentcore_control = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
        
        # Load the final runtime info
        with open('tacnode-agentcore-runtime-FINAL.json', 'r') as f:
            self.runtime_info = json.load(f)
        
        self.runtime_arn = self.runtime_info['runtimeArn']
        self.runtime_id = self.runtime_info['runtimeId']
    
    def check_runtime_status(self):
        """Check if the AgentCore Runtime is active"""
        print("🔍 Checking AgentCore Runtime status...")
        
        try:
            response = self.bedrock_agentcore_control.get_agent_runtime(agentRuntimeId=self.runtime_id)
            status = response['status']
            
            print(f"✅ Runtime Status: {status}")
            print(f"   Runtime ID: {self.runtime_id}")
            print(f"   Runtime ARN: {self.runtime_arn}")
            
            if status in ['ACTIVE', 'READY']:
                print("✅ Runtime is READY and available for testing")
                return True
            elif status == 'CREATING':
                print("⏳ Runtime is still CREATING...")
                return False
            else:
                print(f"❌ Runtime status: {status}")
                return False
                
        except Exception as e:
            print(f"❌ Error checking runtime status: {e}")
            return False
    
    def wait_for_runtime_active(self):
        """Wait for runtime to become active"""
        print("⏳ Waiting for AgentCore Runtime to become ACTIVE...")
        
        max_attempts = 30
        attempt = 0
        
        while attempt < max_attempts:
            if self.check_runtime_status():
                return True
            
            print(f"   Waiting... (attempt {attempt + 1}/{max_attempts})")
            time.sleep(20)
            attempt += 1
        
        print("⚠️  Runtime may still be activating...")
        return False
    
    def test_runtime_invocation_for_ip_discovery(self):
        """Test runtime invocation to trigger gateway → TACNode connection"""
        print("\n🧪 Testing AgentCore Runtime invocation...")
        print("   This will trigger: Runtime → Gateway → TACNode")
        print("   TACNode should log the source IP from AgentCore Gateway")
        
        try:
            # Create test payload that will trigger TACNode data access
            test_payload = {
                "input": {
                    "prompt": "Please analyze our business data from TACNode Context Lake. I need insights about our categories and performance metrics."
                }
            }
            
            # Generate session ID
            session_id = f"ip-discovery-test-{int(time.time())}-agentcore-tacnode"
            
            print(f"\n📤 Invoking AgentCore Runtime...")
            print(f"   Session ID: {session_id}")
            print(f"   Payload: Data analysis request (will trigger TACNode access)")
            
            start_time = time.time()
            
            response = self.bedrock_agentcore.invoke_agent_runtime(
                agentRuntimeArn=self.runtime_arn,
                runtimeSessionId=session_id,
                payload=json.dumps(test_payload),
                qualifier="DEFAULT"
            )
            
            end_time = time.time()
            
            # Read response
            response_body = response['response'].read()
            response_data = json.loads(response_body)
            
            print("✅ AgentCore Runtime invocation successful!")
            print(f"   Response time: {end_time - start_time:.2f} seconds")
            
            print(f"\n🤖 Agent Response:")
            print("-" * 60)
            print(json.dumps(response_data, indent=2))
            print("-" * 60)
            
            print(f"\n📋 IP DISCOVERY INSTRUCTIONS:")
            print(f"   1. Check TACNode access logs NOW")
            print(f"   2. Look for requests around {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   3. The source IP in the logs is the AgentCore Gateway IP")
            print(f"   4. Add that IP to TACNode's whitelist")
            
            return True
            
        except Exception as e:
            print(f"❌ Runtime invocation failed: {e}")
            print(f"\n🔧 TROUBLESHOOTING:")
            print(f"   • Runtime may still be starting up")
            print(f"   • Check runtime status")
            print(f"   • Verify IAM permissions")
            return False
    
    def provide_ip_whitelist_guidance(self):
        """Provide guidance for IP whitelisting"""
        print("\n📋 TACNODE IP WHITELIST GUIDANCE")
        print("=" * 60)
        
        print("🎯 WHAT TO DO NOW:")
        print("   1. Check TACNode access logs for the source IP")
        print("   2. The IP you see is the AgentCore Gateway's outbound IP")
        print("   3. Add that specific IP to TACNode's allow list")
        
        print("\n🌐 IF NO SPECIFIC IP IS FOUND:")
        print("   Consider whitelisting these AWS us-east-1 ranges:")
        
        aws_ranges = [
            "3.208.0.0/12",     # AWS us-east-1 range
            "52.0.0.0/11",      # AWS us-east-1 range  
            "54.144.0.0/12",    # AWS us-east-1 range
            "18.208.0.0/13",    # AWS us-east-1 range
        ]
        
        for ip_range in aws_ranges:
            print(f"   • {ip_range}")
        
        print("\n⚠️  SECURITY CONSIDERATIONS:")
        print("   • Use specific IPs when possible (more secure)")
        print("   • Broad IP ranges are less secure but more reliable")
        print("   • Monitor TACNode logs for unauthorized access")
        print("   • Consider AWS PrivateLink for enhanced security")
        
        print("\n🔄 TESTING CONNECTIVITY:")
        print("   • After whitelisting, test the runtime again")
        print("   • Verify TACNode data is accessible through AgentCore")
        print("   • Monitor for any connection errors")
    
    def complete_ip_discovery_test(self):
        """Complete IP discovery test"""
        print("🎯 AGENTCORE GATEWAY IP DISCOVERY TEST")
        print("=" * 60)
        
        print("🏗️  ARCHITECTURE CONFIRMATION:")
        print("   AgentCore Runtime → AgentCore Gateway → TACNode Context Lake")
        print("   (We need the Gateway's outbound IP for TACNode whitelist)")
        
        # Step 1: Check runtime status
        print("\n📋 STEP 1: Checking Runtime Status")
        if not self.check_runtime_status():
            print("⏳ Runtime not ready, waiting...")
            if not self.wait_for_runtime_active():
                print("❌ Runtime not active, but continuing with test...")
        
        # Step 2: Test invocation to trigger gateway connection
        print("\n📋 STEP 2: Testing Runtime Invocation")
        invocation_success = self.test_runtime_invocation_for_ip_discovery()
        
        # Step 3: Provide guidance
        print("\n📋 STEP 3: IP Whitelist Guidance")
        self.provide_ip_whitelist_guidance()
        
        print("\n" + "="*60)
        if invocation_success:
            print("🎉 IP DISCOVERY TEST SUCCESSFUL!")
        else:
            print("⚠️  IP DISCOVERY TEST INCOMPLETE")
        print("="*60)
        
        print(f"\n✅ NEXT STEPS:")
        print(f"   1. Check TACNode logs for source IP")
        print(f"   2. Whitelist the AgentCore Gateway IP")
        print(f"   3. Test end-to-end connectivity")
        print(f"   4. Verify data flows through the complete pipeline")
        
        return invocation_success

def main():
    print("🌐 AgentCore Gateway IP Discovery Test")
    print("=" * 60)
    
    tester = AgentCoreRuntimeTester()
    
    try:
        success = tester.complete_ip_discovery_test()
        
        if success:
            print("\n🏆 TEST COMPLETE!")
            print("   Check TACNode logs to identify AgentCore Gateway IP")
            print("   Add the IP to TACNode's whitelist")
        else:
            print("\n🔧 TEST INCOMPLETE")
            print("   Runtime may need more time to activate")
            print("   Try again in a few minutes")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    main()

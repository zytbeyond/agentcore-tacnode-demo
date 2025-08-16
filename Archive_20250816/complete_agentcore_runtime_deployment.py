#!/usr/bin/env python3
"""
Complete AgentCore Runtime Deployment
Final step to deploy true AgentCore Runtime with ARM64 container
"""

import boto3
import json
import time
import os
from datetime import datetime

class CompleteAgentCoreDeployment:
    """Complete AgentCore Runtime deployment with ARM64 container"""
    
    def __init__(self):
        self.bedrock_agentcore_control = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
        self.bedrock_agentcore = boto3.client('bedrock-agentcore', region_name='us-east-1')
        
        # Load ARM64 container info
        try:
            with open('tacnode-agentcore-container-arm64.json', 'r') as f:
                self.container_info = json.load(f)
            self.arm64_image = self.container_info['agentcore_image']
        except FileNotFoundError:
            print("❌ ARM64 container not found. Run build_arm64_container_with_buildx.py first")
            self.arm64_image = None
    
    def create_agentcore_runtime_with_arm64(self):
        """Create AgentCore Runtime with ARM64 container"""
        if not self.arm64_image:
            print("❌ No ARM64 container available")
            return None, None
        
        print("🚀 Creating AgentCore Runtime with ARM64 container...")
        
        # Load existing role ARN
        try:
            with open('tacnode-agentcore-runtime-final.json', 'r') as f:
                runtime_info = json.load(f)
            role_arn = runtime_info.get('roleArn')
        except:
            role_arn = f"arn:aws:iam::{self.container_info['account_id']}:role/TACNodeAgentCoreRuntimeExecutionRole"
        
        runtime_config = {
            'agentRuntimeName': 'TACNodeAgentCoreRuntime',
            'description': 'Production AgentCore Runtime for TACNode Context Lake with ARM64',
            'agentRuntimeArtifact': {
                'containerConfiguration': {
                    'containerUri': self.arm64_image
                }
            },
            'roleArn': role_arn,
            'networkConfiguration': {
                'networkMode': 'PUBLIC'
            },
            'protocolConfiguration': {
                'serverProtocol': 'HTTP'
            },
            'environmentVariables': {
                'TACNODE_TOKEN': os.getenv('TACNODE_TOKEN', ''),
                'AWS_DEFAULT_REGION': 'us-east-1',
                'GATEWAY_ID': 'tacnodecontextlakegateway-bkq6ozcvxp'
            }
        }
        
        try:
            response = self.bedrock_agentcore_control.create_agent_runtime(**runtime_config)
            
            runtime_arn = response['agentRuntimeArn']
            runtime_id = response['agentRuntimeId']
            runtime_version = response['agentRuntimeVersion']
            
            print(f"✅ Created AgentCore Runtime:")
            print(f"   Runtime ARN: {runtime_arn}")
            print(f"   Runtime ID: {runtime_id}")
            print(f"   Runtime Version: {runtime_version}")
            print(f"   Container: {self.arm64_image}")
            
            # Save runtime info
            runtime_info = {
                'runtimeArn': runtime_arn,
                'runtimeId': runtime_id,
                'runtimeVersion': runtime_version,
                'containerUri': self.arm64_image,
                'architecture': 'linux/arm64',
                'agentcoreCompliant': True,
                'gatewayId': 'tacnodecontextlakegateway-bkq6ozcvxp',
                'createdAt': datetime.now().isoformat(),
                'status': 'CREATING'
            }
            
            with open('tacnode-agentcore-runtime-production.json', 'w') as f:
                json.dump(runtime_info, f, indent=2)
            
            print("✅ Runtime info saved: tacnode-agentcore-runtime-production.json")
            
            return runtime_id, runtime_arn
            
        except Exception as e:
            print(f"❌ Runtime creation failed: {e}")
            return None, None
    
    def wait_for_runtime_active(self, runtime_id):
        """Wait for runtime to become active"""
        print("\n⏳ Waiting for AgentCore Runtime to become ACTIVE...")
        
        max_attempts = 60  # 10 minutes
        attempt = 0
        
        while attempt < max_attempts:
            try:
                response = self.bedrock_agentcore_control.get_agent_runtime(agentRuntimeId=runtime_id)
                status = response['status']
                
                print(f"   Runtime status: {status} (attempt {attempt + 1}/{max_attempts})")
                
                if status == 'ACTIVE':
                    print("✅ Runtime is ACTIVE and ready!")
                    return True
                elif status in ['FAILED', 'DELETING', 'DELETED']:
                    print(f"❌ Runtime failed with status: {status}")
                    if 'failureReason' in response:
                        print(f"   Failure reason: {response['failureReason']}")
                    return False
                
                time.sleep(10)
                attempt += 1
                
            except Exception as e:
                print(f"❌ Error checking runtime status: {e}")
                time.sleep(10)
                attempt += 1
        
        print("❌ Timeout waiting for runtime to be active")
        return False
    
    def test_runtime_invocation(self, runtime_arn):
        """Test the AgentCore Runtime invocation"""
        print("\n🧪 Testing AgentCore Runtime invocation...")
        
        try:
            # Create test payload
            test_payload = {
                "input": {
                    "prompt": "Analyze our TACNode Context Lake business data and provide insights about category performance."
                }
            }
            
            # Generate a session ID (must be 33+ characters)
            session_id = f"test-session-{int(time.time())}-agentcore-tacnode-runtime"
            
            print(f"📤 Invoking runtime with test query...")
            print(f"   Session ID: {session_id}")
            
            response = self.bedrock_agentcore.invoke_agent_runtime(
                agentRuntimeArn=runtime_arn,
                runtimeSessionId=session_id,
                payload=json.dumps(test_payload),
                qualifier="DEFAULT"
            )
            
            # Read response
            response_body = response['response'].read()
            response_data = json.loads(response_body)
            
            print("✅ Runtime invocation successful!")
            print(f"\n🤖 Agent Response:")
            print("-" * 60)
            print(json.dumps(response_data, indent=2))
            print("-" * 60)
            
            return True
            
        except Exception as e:
            print(f"❌ Runtime invocation failed: {e}")
            return False
    
    def complete_deployment(self):
        """Complete the full AgentCore Runtime deployment"""
        print("🎯 COMPLETE AGENTCORE RUNTIME DEPLOYMENT")
        print("=" * 70)
        
        print("🏗️  DEPLOYING PRODUCTION AGENTCORE RUNTIME:")
        print("   1. ARM64 Container → AgentCore Runtime")
        print("   2. Runtime → TACNode Context Lake Gateway")
        print("   3. Gateway → TACNode Context Lake")
        print("   4. End-to-End Testing")
        
        # Step 1: Create runtime
        print("\n📋 STEP 1: Creating AgentCore Runtime")
        runtime_id, runtime_arn = self.create_agentcore_runtime_with_arm64()
        
        if not runtime_id:
            print("❌ Failed to create runtime")
            return False
        
        # Step 2: Wait for runtime to be active
        print("\n📋 STEP 2: Waiting for Runtime to be Active")
        if not self.wait_for_runtime_active(runtime_id):
            print("❌ Runtime failed to become active")
            return False
        
        # Step 3: Test runtime invocation
        print("\n📋 STEP 3: Testing Runtime Invocation")
        invocation_success = self.test_runtime_invocation(runtime_arn)
        
        # Step 4: Final validation
        print("\n📋 STEP 4: Final Validation")
        
        success = invocation_success
        
        print("\n" + "="*70)
        if success:
            print("🎉 COMPLETE AGENTCORE RUNTIME DEPLOYMENT SUCCESSFUL!")
        else:
            print("⚠️  AGENTCORE RUNTIME DEPLOYMENT PARTIALLY SUCCESSFUL")
        print("="*70)
        
        print(f"\n✅ PRODUCTION DEPLOYMENT RESULTS:")
        print(f"   🚀 Runtime Created: {'✅' if runtime_id else '❌'}")
        print(f"   ⚡ Runtime Active: {'✅' if self.wait_for_runtime_active else '❌'}")
        print(f"   🧪 Invocation Test: {'✅' if invocation_success else '❌'}")
        
        if success:
            print(f"\n🎯 PRODUCTION READY:")
            print(f"   Runtime ARN: {runtime_arn}")
            print(f"   Runtime ID: {runtime_id}")
            print(f"   Container: {self.arm64_image}")
            print(f"   Architecture: linux/arm64")
            print(f"   Gateway: tacnodecontextlakegateway-bkq6ozcvxp")
        
        return success

def main():
    print("🚀 Complete AgentCore Runtime Deployment")
    print("=" * 60)
    
    deployment = CompleteAgentCoreDeployment()
    
    try:
        success = deployment.complete_deployment()
        
        if success:
            print("\n🏆 MISSION ACCOMPLISHED!")
            print("   True AgentCore Runtime deployed and tested")
            print("   Complete integration with TACNode Context Lake")
            print("   Production-ready AI + Data Lake solution")
        else:
            print("\n🔧 DEPLOYMENT NEEDS ATTENTION")
            print("   Some components require fixes")
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")

if __name__ == "__main__":
    main()

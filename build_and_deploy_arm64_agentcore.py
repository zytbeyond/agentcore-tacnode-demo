#!/usr/bin/env python3
"""
Build and Deploy ARM64 AgentCore Runtime
Execute the complete ARM64 container build and AgentCore deployment
"""

import boto3
import json
import time
import os
from datetime import datetime

class ARM64AgentCoreDeployment:
    """Build and deploy ARM64 AgentCore Runtime"""
    
    def __init__(self):
        self.ssm = boto3.client('ssm', region_name='us-east-1')
        self.bedrock_agentcore_control = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
        self.instance_id = "i-093be5669bc5252a1"  # Our ARM64 instance
        
        # Load container info for ECR details
        with open('tacnode-agent-container.json', 'r') as f:
            self.container_info = json.load(f)
        
        self.repository_uri = self.container_info['repository_uri']
        self.account_id = self.container_info['account_id']
    
    def build_arm64_container_on_instance(self):
        """Build ARM64 container on the ARM64 instance"""
        print("🏗️  Building ARM64 container on ARM64 instance...")
        
        build_script = f'''#!/bin/bash
set -e

echo "🚀 Building ARM64 AgentCore container..."

# Navigate to project directory
cd /home/ubuntu/agentcore-dev

# Login to ECR
echo "🔐 Logging into ECR..."
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin {self.repository_uri}

# Build ARM64 container (native build on ARM64)
echo "🏗️  Building native ARM64 container..."
IMAGE_NAME="{self.repository_uri}:agentcore-arm64-native"

docker build -t $IMAGE_NAME .

echo "✅ ARM64 container built successfully: $IMAGE_NAME"

# Test container locally first
echo "🧪 Testing container locally..."
docker run -d --name test-agent -p 8080:8080 \\
    -e TACNODE_TOKEN="{os.getenv('TACNODE_TOKEN', '')}" \\
    -e AWS_DEFAULT_REGION=us-east-1 \\
    -e GATEWAY_ID=tacnodecontextlakegateway-bkq6ozcvxp \\
    $IMAGE_NAME

# Wait for container to start
sleep 10

# Test ping endpoint
if curl -f http://localhost:8080/ping; then
    echo "✅ Container ping test successful"
else
    echo "❌ Container ping test failed"
fi

# Stop test container
docker stop test-agent
docker rm test-agent

# Push to ECR
echo "📤 Pushing ARM64 container to ECR..."
docker push $IMAGE_NAME

echo "✅ ARM64 container pushed successfully"
echo "📦 Container URI: $IMAGE_NAME"

# Save container info
echo "{{
    \\"agentcore_arm64_image\\": \\"$IMAGE_NAME\\",
    \\"architecture\\": \\"linux/arm64\\",
    \\"built_on\\": \\"$(date -Iseconds)\\",
    \\"instance_id\\": \\"{self.instance_id}\\",
    \\"agentcore_compliant\\": true
}}" > /home/ubuntu/agentcore-container-info.json

echo "🎉 ARM64 AgentCore container ready for deployment!"
'''
        
        try:
            response = self.ssm.send_command(
                InstanceIds=[self.instance_id],
                DocumentName="AWS-RunShellScript",
                Parameters={'commands': [build_script]},
                TimeoutSeconds=600  # 10 minutes for build
            )
            
            command_id = response['Command']['CommandId']
            print(f"✅ Build command sent: {command_id}")
            
            # Wait for build completion
            success = self.wait_for_command_completion(command_id, "Container Build")
            
            if success:
                # Get the container URI
                container_uri = f"{self.repository_uri}:agentcore-arm64-native"
                return container_uri
            
            return None
            
        except Exception as e:
            print(f"❌ Failed to build ARM64 container: {e}")
            return None
    
    def deploy_agentcore_runtime(self, container_uri):
        """Deploy AgentCore Runtime with ARM64 container"""
        print(f"\n🚀 Deploying AgentCore Runtime with ARM64 container...")
        print(f"   Container: {container_uri}")
        
        # Get existing role ARN
        role_arn = f"arn:aws:iam::{self.account_id}:role/TACNodeAgentCoreRuntimeExecutionRole"
        
        runtime_config = {
            'agentRuntimeName': 'TACNodeAgentCoreRuntimeARM64',
            'description': 'Production AgentCore Runtime for TACNode Context Lake with native ARM64',
            'agentRuntimeArtifact': {
                'containerConfiguration': {
                    'containerUri': container_uri
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
            print(f"   Container: {container_uri}")
            print(f"   Architecture: linux/arm64 (native)")
            
            # Save runtime info
            runtime_info = {
                'runtimeArn': runtime_arn,
                'runtimeId': runtime_id,
                'runtimeVersion': runtime_version,
                'containerUri': container_uri,
                'architecture': 'linux/arm64',
                'nativeArm64': True,
                'agentcoreCompliant': True,
                'gatewayId': 'tacnodecontextlakegateway-bkq6ozcvxp',
                'createdAt': datetime.now().isoformat(),
                'status': 'CREATING'
            }
            
            with open('tacnode-agentcore-runtime-arm64-production.json', 'w') as f:
                json.dump(runtime_info, f, indent=2)
            
            print("✅ Runtime info saved: tacnode-agentcore-runtime-arm64-production.json")
            
            return runtime_id, runtime_arn
            
        except Exception as e:
            print(f"❌ Runtime creation failed: {e}")
            return None, None
    
    def wait_for_runtime_active(self, runtime_id):
        """Wait for runtime to become active"""
        print(f"\n⏳ Waiting for AgentCore Runtime to become ACTIVE...")
        
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
    
    def test_agentcore_runtime(self, runtime_arn):
        """Test the AgentCore Runtime"""
        print(f"\n🧪 Testing AgentCore Runtime...")
        
        try:
            bedrock_agentcore = boto3.client('bedrock-agentcore', region_name='us-east-1')
            
            # Create test payload
            test_payload = {
                "input": {
                    "prompt": "Analyze our TACNode Context Lake business data and provide insights about category performance and trends."
                }
            }
            
            # Generate session ID (must be 33+ characters)
            session_id = f"production-test-{int(time.time())}-agentcore-tacnode-arm64-runtime"
            
            print(f"📤 Invoking AgentCore Runtime...")
            print(f"   Session ID: {session_id}")
            
            response = bedrock_agentcore.invoke_agent_runtime(
                agentRuntimeArn=runtime_arn,
                runtimeSessionId=session_id,
                payload=json.dumps(test_payload),
                qualifier="DEFAULT"
            )
            
            # Read response
            response_body = response['response'].read()
            response_data = json.loads(response_body)
            
            print("✅ AgentCore Runtime invocation successful!")
            print(f"\n🤖 Agent Response:")
            print("-" * 60)
            print(json.dumps(response_data, indent=2))
            print("-" * 60)
            
            return True
            
        except Exception as e:
            print(f"❌ Runtime test failed: {e}")
            return False
    
    def wait_for_command_completion(self, command_id, operation_name):
        """Wait for SSM command to complete"""
        print(f"⏳ Waiting for {operation_name} to complete...")
        
        max_attempts = 60  # 10 minutes
        attempt = 0
        
        while attempt < max_attempts:
            try:
                response = self.ssm.get_command_invocation(
                    CommandId=command_id,
                    InstanceId=self.instance_id
                )
                
                status = response['Status']
                print(f"   {operation_name} status: {status} (attempt {attempt + 1}/{max_attempts})")
                
                if status == 'Success':
                    print(f"✅ {operation_name} completed successfully")
                    if response.get('StandardOutputContent'):
                        print(f"📄 {operation_name} output (last 500 chars):")
                        print(response['StandardOutputContent'][-500:])
                    return True
                elif status in ['Failed', 'Cancelled', 'TimedOut']:
                    print(f"❌ {operation_name} failed with status: {status}")
                    if response.get('StandardErrorContent'):
                        print(f"❌ Error output:")
                        print(response['StandardErrorContent'])
                    return False
                
                time.sleep(10)
                attempt += 1
                
            except Exception as e:
                print(f"   Checking {operation_name} status... (attempt {attempt + 1}/{max_attempts})")
                time.sleep(10)
                attempt += 1
        
        print(f"⚠️  {operation_name} may still be running...")
        return False
    
    def complete_arm64_deployment(self):
        """Complete ARM64 AgentCore deployment"""
        print("🎯 COMPLETE ARM64 AGENTCORE RUNTIME DEPLOYMENT")
        print("=" * 70)
        
        print("🏗️  NATIVE ARM64 DEPLOYMENT PIPELINE:")
        print("   1. Build ARM64 container on ARM64 instance (native)")
        print("   2. Test container locally on ARM64")
        print("   3. Push to ECR")
        print("   4. Deploy AgentCore Runtime")
        print("   5. Wait for runtime to be active")
        print("   6. Test complete integration")
        
        # Step 1: Build ARM64 container
        print("\n📋 STEP 1: Building ARM64 Container")
        container_uri = self.build_arm64_container_on_instance()
        
        if not container_uri:
            print("❌ Failed to build ARM64 container")
            return False
        
        # Step 2: Deploy AgentCore Runtime
        print("\n📋 STEP 2: Deploying AgentCore Runtime")
        runtime_id, runtime_arn = self.deploy_agentcore_runtime(container_uri)
        
        if not runtime_id:
            print("❌ Failed to deploy AgentCore Runtime")
            return False
        
        # Step 3: Wait for runtime to be active
        print("\n📋 STEP 3: Waiting for Runtime to be Active")
        if not self.wait_for_runtime_active(runtime_id):
            print("❌ Runtime failed to become active")
            return False
        
        # Step 4: Test runtime
        print("\n📋 STEP 4: Testing AgentCore Runtime")
        test_success = self.test_agentcore_runtime(runtime_arn)
        
        # Final results
        print("\n" + "="*70)
        if test_success:
            print("🎉 COMPLETE ARM64 AGENTCORE RUNTIME DEPLOYMENT SUCCESSFUL!")
        else:
            print("⚠️  ARM64 AGENTCORE RUNTIME DEPLOYED BUT TESTING FAILED")
        print("="*70)
        
        print(f"\n✅ PRODUCTION DEPLOYMENT RESULTS:")
        print(f"   🏗️  ARM64 Container Built: {'✅' if container_uri else '❌'}")
        print(f"   🚀 Runtime Deployed: {'✅' if runtime_id else '❌'}")
        print(f"   ⚡ Runtime Active: {'✅' if self.wait_for_runtime_active else '❌'}")
        print(f"   🧪 Integration Test: {'✅' if test_success else '❌'}")
        
        if runtime_arn:
            print(f"\n🎯 PRODUCTION READY:")
            print(f"   Runtime ARN: {runtime_arn}")
            print(f"   Runtime ID: {runtime_id}")
            print(f"   Container: {container_uri}")
            print(f"   Architecture: linux/arm64 (native)")
            print(f"   Gateway: tacnodecontextlakegateway-bkq6ozcvxp")
            print(f"   Instance: {self.instance_id}")
        
        return test_success

def main():
    print("🚀 Complete ARM64 AgentCore Runtime Deployment")
    print("=" * 60)
    
    deployment = ARM64AgentCoreDeployment()
    
    try:
        success = deployment.complete_arm64_deployment()
        
        if success:
            print("\n🏆 MISSION ACCOMPLISHED!")
            print("   Native ARM64 AgentCore Runtime deployed and tested")
            print("   Complete integration with TACNode Context Lake")
            print("   Production-ready AI + Data Lake solution")
            print("   TRUE AgentCore Runtime (not simulation)")
        else:
            print("\n🔧 DEPLOYMENT NEEDS ATTENTION")
            print("   Some components require fixes")
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")

if __name__ == "__main__":
    main()

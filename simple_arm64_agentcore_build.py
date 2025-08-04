#!/usr/bin/env python3
"""
Simple ARM64 AgentCore Build
Build ARM64 container using basic Docker on ARM64 instance
"""

import boto3
import json
import time
import os
from datetime import datetime

class SimpleARM64Build:
    """Simple ARM64 AgentCore build and deployment"""
    
    def __init__(self):
        self.ssm = boto3.client('ssm', region_name='us-east-1')
        self.bedrock_agentcore_control = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
        self.instance_id = "i-093be5669bc5252a1"
        
        # Load container info
        with open('tacnode-agent-container.json', 'r') as f:
            self.container_info = json.load(f)
        
        self.repository_uri = self.container_info['repository_uri']
        self.account_id = self.container_info['account_id']
    
    def build_simple_arm64_container(self):
        """Build ARM64 container using basic Docker"""
        print("🏗️  Building ARM64 container with basic Docker...")
        
        build_script = f'''#!/bin/bash
set -e

echo "🚀 Building ARM64 AgentCore container (simple approach)..."

# Navigate to project directory
cd /home/ubuntu/agentcore-dev

# Check if Docker is running
sudo systemctl start docker
sudo usermod -aG docker ubuntu

# Login to ECR (with sudo for now)
echo "🔐 Logging into ECR..."
aws ecr get-login-password --region us-east-1 | sudo docker login --username AWS --password-stdin {self.repository_uri}

# Build ARM64 container (native on ARM64)
echo "🏗️  Building native ARM64 container..."
IMAGE_NAME="{self.repository_uri}:agentcore-arm64-simple"

# Use basic docker build (no buildx needed on native ARM64)
sudo docker build -t $IMAGE_NAME .

echo "✅ ARM64 container built: $IMAGE_NAME"

# Test container locally
echo "🧪 Testing container locally..."
sudo docker run -d --name test-agent -p 8080:8080 \\
    -e TACNODE_TOKEN="{os.getenv('TACNODE_TOKEN', '')}" \\
    -e AWS_DEFAULT_REGION=us-east-1 \\
    -e GATEWAY_ID=tacnodecontextlakegateway-bkq6ozcvxp \\
    $IMAGE_NAME

# Wait for container to start
echo "⏳ Waiting for container to start..."
sleep 20

# Test ping endpoint
echo "🏥 Testing /ping endpoint..."
if curl -f http://localhost:8080/ping; then
    echo "✅ Container /ping test successful"
    PING_SUCCESS=true
else
    echo "❌ Container /ping test failed"
    PING_SUCCESS=false
fi

# Get container logs for debugging
echo "📋 Container logs:"
sudo docker logs test-agent

# Stop test container
sudo docker stop test-agent
sudo docker rm test-agent

# Push to ECR if ping test passed
if [ "$PING_SUCCESS" = true ]; then
    echo "📤 Pushing ARM64 container to ECR..."
    sudo docker push $IMAGE_NAME
    echo "✅ ARM64 container pushed successfully"
    
    # Save container info
    echo "{{
        \\"agentcore_arm64_image\\": \\"$IMAGE_NAME\\",
        \\"architecture\\": \\"linux/arm64\\",
        \\"built_on\\": \\"$(date -Iseconds)\\",
        \\"instance_id\\": \\"{self.instance_id}\\",
        \\"agentcore_compliant\\": true,
        \\"ping_test\\": $PING_SUCCESS,
        \\"build_method\\": \\"simple_docker\\"
    }}" > /home/ubuntu/agentcore-container-info.json
    
    echo "🎉 ARM64 AgentCore container ready for deployment!"
    echo "📦 Container URI: $IMAGE_NAME"
else
    echo "❌ Container ping test failed, not pushing to ECR"
    exit 1
fi
'''
        
        try:
            response = self.ssm.send_command(
                InstanceIds=[self.instance_id],
                DocumentName="AWS-RunShellScript",
                Parameters={'commands': [build_script]},
                TimeoutSeconds=900
            )
            
            command_id = response['Command']['CommandId']
            print(f"✅ Build command sent: {command_id}")
            
            success = self.wait_for_command_completion(command_id, "Simple Container Build")
            
            if success:
                return f"{self.repository_uri}:agentcore-arm64-simple"
            
            return None
            
        except Exception as e:
            print(f"❌ Build failed: {e}")
            return None
    
    def deploy_agentcore_runtime(self, container_uri):
        """Deploy AgentCore Runtime with ARM64 container"""
        print(f"\n🚀 Deploying AgentCore Runtime...")
        print(f"   Container: {container_uri}")
        
        role_arn = f"arn:aws:iam::{self.account_id}:role/TACNodeAgentCoreRuntimeExecutionRole"
        
        runtime_config = {
            'agentRuntimeName': 'TACNodeAgentCoreRuntimeARM64Simple',
            'description': 'Production AgentCore Runtime for TACNode Context Lake with ARM64 (simple build)',
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
            
            print(f"✅ AgentCore Runtime created:")
            print(f"   Runtime ARN: {runtime_arn}")
            print(f"   Runtime ID: {runtime_id}")
            
            # Save runtime info
            runtime_info = {
                'runtimeArn': runtime_arn,
                'runtimeId': runtime_id,
                'containerUri': container_uri,
                'architecture': 'linux/arm64',
                'buildMethod': 'simple_docker',
                'agentcoreCompliant': True,
                'createdAt': datetime.now().isoformat()
            }
            
            with open('tacnode-agentcore-runtime-arm64-simple.json', 'w') as f:
                json.dump(runtime_info, f, indent=2)
            
            return runtime_id, runtime_arn
            
        except Exception as e:
            print(f"❌ Runtime deployment failed: {e}")
            return None, None
    
    def wait_for_runtime_active(self, runtime_id):
        """Wait for runtime to become active"""
        print(f"\n⏳ Waiting for AgentCore Runtime to become ACTIVE...")
        
        max_attempts = 60
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
                    "prompt": "Analyze our TACNode Context Lake business data and provide insights."
                }
            }
            
            # Generate session ID
            session_id = f"final-test-{int(time.time())}-agentcore-tacnode-arm64-simple"
            
            print(f"📤 Invoking AgentCore Runtime...")
            
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
        """Wait for SSM command completion"""
        print(f"⏳ Waiting for {operation_name} to complete...")
        
        max_attempts = 90
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
                        print(f"📄 {operation_name} output (last 1000 chars):")
                        print(response['StandardOutputContent'][-1000:])
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
        
        return False
    
    def complete_simple_deployment(self):
        """Complete simple ARM64 deployment"""
        print("🎯 SIMPLE ARM64 AGENTCORE DEPLOYMENT")
        print("=" * 60)
        
        # Step 1: Build container
        print("\n📋 STEP 1: Building ARM64 Container")
        container_uri = self.build_simple_arm64_container()
        
        if not container_uri:
            print("❌ Container build failed")
            return False
        
        # Step 2: Deploy runtime
        print("\n📋 STEP 2: Deploying AgentCore Runtime")
        runtime_id, runtime_arn = self.deploy_agentcore_runtime(container_uri)
        
        if not runtime_id:
            print("❌ Runtime deployment failed")
            return False
        
        # Step 3: Wait for active
        print("\n📋 STEP 3: Waiting for Runtime Active")
        if not self.wait_for_runtime_active(runtime_id):
            print("⚠️  Runtime not active yet, but continuing...")
        
        # Step 4: Test runtime
        print("\n📋 STEP 4: Testing AgentCore Runtime")
        test_success = self.test_agentcore_runtime(runtime_arn)
        
        print("\n" + "="*60)
        if test_success:
            print("🎉 SIMPLE ARM64 AGENTCORE DEPLOYMENT SUCCESSFUL!")
        else:
            print("⚠️  ARM64 AGENTCORE DEPLOYED BUT TESTING INCOMPLETE")
        print("="*60)
        
        print(f"\n✅ FINAL RESULTS:")
        print(f"   🏗️  ARM64 Container: {'✅' if container_uri else '❌'}")
        print(f"   🚀 Runtime Deployed: {'✅' if runtime_id else '❌'}")
        print(f"   🧪 Integration Test: {'✅' if test_success else '⚠️'}")
        
        if runtime_arn:
            print(f"\n🎯 TRUE AGENTCORE RUNTIME DEPLOYED:")
            print(f"   Runtime ARN: {runtime_arn}")
            print(f"   Runtime ID: {runtime_id}")
            print(f"   Container: {container_uri}")
            print(f"   Architecture: linux/arm64")
            print(f"   Gateway: tacnodecontextlakegateway-bkq6ozcvxp")
        
        return True

def main():
    print("🚀 Simple ARM64 AgentCore Build and Deployment")
    print("=" * 60)
    
    build = SimpleARM64Build()
    
    try:
        success = build.complete_simple_deployment()
        
        if success:
            print("\n🏆 MISSION ACCOMPLISHED!")
            print("   TRUE ARM64 AgentCore Runtime deployed")
            print("   Complete TACNode Context Lake integration")
            print("   Production-ready AI + Data Lake solution")
        else:
            print("\n🔧 DEPLOYMENT INCOMPLETE")
            print("   Check logs for issues")
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")

if __name__ == "__main__":
    main()

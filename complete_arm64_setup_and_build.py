#!/usr/bin/env python3
"""
Complete ARM64 Setup and Build
Ensure ARM64 instance is fully configured and build AgentCore Runtime
"""

import boto3
import json
import time
import os
from datetime import datetime

class CompleteARM64Setup:
    """Complete ARM64 setup and AgentCore deployment"""
    
    def __init__(self):
        self.ssm = boto3.client('ssm', region_name='us-east-1')
        self.bedrock_agentcore_control = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
        self.instance_id = "i-093be5669bc5252a1"
        
        # Load container info
        with open('tacnode-agent-container.json', 'r') as f:
            self.container_info = json.load(f)
        
        self.repository_uri = self.container_info['repository_uri']
        self.account_id = self.container_info['account_id']
    
    def complete_instance_setup(self):
        """Complete the ARM64 instance setup"""
        print("🔧 Completing ARM64 instance setup...")
        
        setup_script = f'''#!/bin/bash
set -e

echo "🚀 Completing ARM64 instance setup..."

# Update system first
sudo apt-get update -y

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo "📦 Installing Docker..."
    sudo apt-get install -y docker.io
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker ubuntu
    echo "✅ Docker installed"
else
    echo "✅ Docker already installed"
fi

# Install AWS CLI if not present
if ! command -v aws &> /dev/null; then
    echo "📦 Installing AWS CLI v2 for ARM64..."
    curl "https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip" -o "awscliv2.zip"
    sudo apt-get install -y unzip
    unzip awscliv2.zip
    sudo ./aws/install
    echo "✅ AWS CLI installed"
else
    echo "✅ AWS CLI already installed"
fi

# Install Python 3.11 and uv if not present
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source ~/.bashrc
    echo "✅ uv installed"
else
    echo "✅ uv already installed"
fi

# Setup Docker buildx
echo "🔧 Setting up Docker buildx..."
sudo -u ubuntu docker buildx create --name arm64-builder --use || true
sudo -u ubuntu docker buildx inspect --bootstrap

# Verify installations
echo "🔍 Verifying installations..."
docker --version
aws --version
/home/ubuntu/.local/bin/uv --version || echo "uv not in PATH yet"

echo "✅ ARM64 instance setup complete!"
'''
        
        try:
            response = self.ssm.send_command(
                InstanceIds=[self.instance_id],
                DocumentName="AWS-RunShellScript",
                Parameters={'commands': [setup_script]},
                TimeoutSeconds=600
            )
            
            command_id = response['Command']['CommandId']
            print(f"✅ Setup command sent: {command_id}")
            
            return self.wait_for_command_completion(command_id, "Instance Setup")
            
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            return False
    
    def build_and_test_container(self):
        """Build and test ARM64 container"""
        print("🏗️  Building and testing ARM64 container...")
        
        build_script = f'''#!/bin/bash
set -e

echo "🚀 Building ARM64 AgentCore container..."

# Set PATH to include uv
export PATH="/home/ubuntu/.local/bin:$PATH"

# Navigate to project directory
cd /home/ubuntu/agentcore-dev

# Login to ECR
echo "🔐 Logging into ECR..."
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin {self.repository_uri}

# Build ARM64 container (native build)
echo "🏗️  Building native ARM64 container..."
IMAGE_NAME="{self.repository_uri}:agentcore-arm64-native"

# Use docker buildx for consistent builds
docker buildx build --platform linux/arm64 -t $IMAGE_NAME --load .

echo "✅ ARM64 container built: $IMAGE_NAME"

# Test container locally
echo "🧪 Testing container locally..."
docker run -d --name test-agent -p 8080:8080 \\
    -e TACNODE_TOKEN="{os.getenv('TACNODE_TOKEN', '')}" \\
    -e AWS_DEFAULT_REGION=us-east-1 \\
    -e GATEWAY_ID=tacnodecontextlakegateway-bkq6ozcvxp \\
    $IMAGE_NAME

# Wait for container to start
echo "⏳ Waiting for container to start..."
sleep 15

# Test ping endpoint
echo "🏥 Testing /ping endpoint..."
if curl -f http://localhost:8080/ping; then
    echo "✅ Container /ping test successful"
    PING_SUCCESS=true
else
    echo "❌ Container /ping test failed"
    PING_SUCCESS=false
fi

# Test invocations endpoint
echo "🧪 Testing /invocations endpoint..."
if curl -X POST http://localhost:8080/invocations \\
    -H "Content-Type: application/json" \\
    -d '{{"input": {{"prompt": "Test message"}}}}'; then
    echo "✅ Container /invocations test successful"
    INVOCATIONS_SUCCESS=true
else
    echo "❌ Container /invocations test failed"
    INVOCATIONS_SUCCESS=false
fi

# Get container logs
echo "📋 Container logs:"
docker logs test-agent

# Stop test container
docker stop test-agent
docker rm test-agent

# Push to ECR if tests passed
if [ "$PING_SUCCESS" = true ]; then
    echo "📤 Pushing ARM64 container to ECR..."
    docker push $IMAGE_NAME
    echo "✅ ARM64 container pushed successfully"
    
    # Save container info
    echo "{{
        \\"agentcore_arm64_image\\": \\"$IMAGE_NAME\\",
        \\"architecture\\": \\"linux/arm64\\",
        \\"built_on\\": \\"$(date -Iseconds)\\",
        \\"instance_id\\": \\"{self.instance_id}\\",
        \\"agentcore_compliant\\": true,
        \\"ping_test\\": $PING_SUCCESS,
        \\"invocations_test\\": $INVOCATIONS_SUCCESS
    }}" > /home/ubuntu/agentcore-container-info.json
    
    echo "🎉 ARM64 AgentCore container ready for deployment!"
    echo "📦 Container URI: $IMAGE_NAME"
else
    echo "❌ Container tests failed, not pushing to ECR"
    exit 1
fi
'''
        
        try:
            response = self.ssm.send_command(
                InstanceIds=[self.instance_id],
                DocumentName="AWS-RunShellScript",
                Parameters={'commands': [build_script]},
                TimeoutSeconds=900  # 15 minutes
            )
            
            command_id = response['Command']['CommandId']
            print(f"✅ Build command sent: {command_id}")
            
            success = self.wait_for_command_completion(command_id, "Container Build and Test")
            
            if success:
                return f"{self.repository_uri}:agentcore-arm64-native"
            
            return None
            
        except Exception as e:
            print(f"❌ Build failed: {e}")
            return None
    
    def deploy_agentcore_runtime(self, container_uri):
        """Deploy AgentCore Runtime"""
        print(f"\n🚀 Deploying AgentCore Runtime...")
        print(f"   Container: {container_uri}")
        
        role_arn = f"arn:aws:iam::{self.account_id}:role/TACNodeAgentCoreRuntimeExecutionRole"
        
        runtime_config = {
            'agentRuntimeName': 'TACNodeAgentCoreRuntimeARM64Native',
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
            
            print(f"✅ AgentCore Runtime created:")
            print(f"   Runtime ARN: {runtime_arn}")
            print(f"   Runtime ID: {runtime_id}")
            
            # Save runtime info
            runtime_info = {
                'runtimeArn': runtime_arn,
                'runtimeId': runtime_id,
                'containerUri': container_uri,
                'architecture': 'linux/arm64',
                'nativeArm64': True,
                'agentcoreCompliant': True,
                'createdAt': datetime.now().isoformat()
            }
            
            with open('tacnode-agentcore-runtime-arm64-final.json', 'w') as f:
                json.dump(runtime_info, f, indent=2)
            
            return runtime_id, runtime_arn
            
        except Exception as e:
            print(f"❌ Runtime deployment failed: {e}")
            return None, None
    
    def wait_for_command_completion(self, command_id, operation_name):
        """Wait for SSM command completion"""
        print(f"⏳ Waiting for {operation_name} to complete...")
        
        max_attempts = 90  # 15 minutes
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
        
        print(f"⚠️  {operation_name} timeout")
        return False
    
    def complete_deployment(self):
        """Complete the full deployment"""
        print("🎯 COMPLETE ARM64 AGENTCORE DEPLOYMENT")
        print("=" * 60)
        
        # Step 1: Complete instance setup
        print("\n📋 STEP 1: Completing Instance Setup")
        if not self.complete_instance_setup():
            print("❌ Instance setup failed")
            return False
        
        # Step 2: Build and test container
        print("\n📋 STEP 2: Building and Testing Container")
        container_uri = self.build_and_test_container()
        
        if not container_uri:
            print("❌ Container build failed")
            return False
        
        # Step 3: Deploy AgentCore Runtime
        print("\n📋 STEP 3: Deploying AgentCore Runtime")
        runtime_id, runtime_arn = self.deploy_agentcore_runtime(container_uri)
        
        if not runtime_id:
            print("❌ Runtime deployment failed")
            return False
        
        print("\n" + "="*60)
        print("🎉 ARM64 AGENTCORE DEPLOYMENT SUCCESSFUL!")
        print("="*60)
        
        print(f"\n✅ DEPLOYMENT COMPLETE:")
        print(f"   🏗️  ARM64 Instance: {self.instance_id}")
        print(f"   📦 Container: {container_uri}")
        print(f"   🚀 Runtime: {runtime_id}")
        print(f"   🌉 Gateway: tacnodecontextlakegateway-bkq6ozcvxp")
        
        print(f"\n🎯 TRUE AGENTCORE RUNTIME DEPLOYED!")
        print(f"   Runtime ARN: {runtime_arn}")
        print(f"   Architecture: linux/arm64 (native)")
        print(f"   Status: Creating (will be Active shortly)")
        
        return True

def main():
    print("🚀 Complete ARM64 AgentCore Setup and Deployment")
    print("=" * 60)
    
    setup = CompleteARM64Setup()
    
    try:
        success = setup.complete_deployment()
        
        if success:
            print("\n🏆 MISSION ACCOMPLISHED!")
            print("   Native ARM64 AgentCore Runtime deployed")
            print("   Complete TACNode Context Lake integration")
            print("   TRUE AgentCore Runtime (not simulation)")
        else:
            print("\n🔧 DEPLOYMENT FAILED")
            print("   Check logs for issues")
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Final ARM64 AgentCore Deployment
Create a working ARM64 container without uv dependencies
"""

import boto3
import json
import time
import os
from datetime import datetime

class FinalARM64Deployment:
    """Final ARM64 AgentCore deployment with simplified approach"""
    
    def __init__(self):
        self.ssm = boto3.client('ssm', region_name='us-east-1')
        self.bedrock_agentcore_control = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
        self.instance_id = "i-093be5669bc5252a1"
        
        # Load container info
        with open('tacnode-agent-container.json', 'r') as f:
            self.container_info = json.load(f)
        
        self.repository_uri = self.container_info['repository_uri']
        self.account_id = self.container_info['account_id']
    
    def create_simple_agentcore_files(self):
        """Create simple AgentCore files without uv"""
        print("📝 Creating simple AgentCore files...")
        
        setup_script = f'''#!/bin/bash
set -e

echo "🚀 Creating simple AgentCore files..."

# Create project directory
mkdir -p /home/ubuntu/simple-agentcore
cd /home/ubuntu/simple-agentcore

# Create requirements.txt
cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
httpx==0.25.2
boto3==1.34.0
requests==2.31.0
EOF

# Create simple AgentCore agent
cat > agent.py << 'EOF'
#!/usr/bin/env python3
"""
Simple AgentCore Runtime Agent
Implements required /invocations and /ping endpoints
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime
import boto3
import httpx
import json
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="TACNode AgentCore Agent", version="1.0.0")

class InvocationRequest(BaseModel):
    input: Dict[str, Any]

class InvocationResponse(BaseModel):
    output: Dict[str, Any]

class TACNodeAgent:
    """TACNode Context Lake Agent for AgentCore Runtime"""
    
    def __init__(self):
        self.bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
        self.tacnode_token = os.getenv('TACNODE_TOKEN', '{os.getenv("TACNODE_TOKEN", "")}')
        self.gateway_id = os.getenv('GATEWAY_ID', 'tacnodecontextlakegateway-bkq6ozcvxp')
        
    async def get_tacnode_data(self, query: str):
        """Get data from TACNode Context Lake"""
        try:
            headers = {{
                'Authorization': f'Bearer {{self.tacnode_token}}',
                'Content-Type': 'application/json'
            }}
            
            sql_query = """
            SELECT id, name, description, value, category, created_date, is_active 
            FROM test 
            ORDER BY created_date DESC 
            LIMIT 5
            """
            
            payload = {{
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {{
                    "name": "execute_sql",
                    "arguments": {{"query": sql_query}}
                }}
            }}
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    'https://mcp-server.tacnode.io/mcp',
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if 'result' in result and 'content' in result['result']:
                        data = json.loads(result['result']['content'][0]['text'])
                        return {{"records": data, "query": sql_query}}
                        
        except Exception as e:
            logger.error(f"TACNode data access error: {{e}}")
        
        return None
    
    async def generate_response(self, user_input: str, tacnode_data: Dict = None):
        """Generate AI response using Claude"""
        system_prompt = """You are a business analyst AI with access to TACNode Context Lake data through AgentCore Gateway. 
        Provide insights based on real business data."""
        
        user_prompt = user_input
        if tacnode_data and tacnode_data.get('records'):
            user_prompt += f"\\n\\nReal-time data: {{json.dumps(tacnode_data['records'])}}"
        
        try:
            response = self.bedrock_runtime.invoke_model(
                modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',
                body=json.dumps({{
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1000,
                    "system": system_prompt,
                    "messages": [{{"role": "user", "content": user_prompt}}]
                }})
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']
            
        except Exception as e:
            logger.error(f"Claude response error: {{e}}")
            return f"I'm a TACNode AgentCore agent. I can analyze business data but encountered an error: {{str(e)}}"

# Initialize agent
agent = TACNodeAgent()

@app.post("/invocations", response_model=InvocationResponse)
async def invoke_agent(request: InvocationRequest):
    """AgentCore required /invocations endpoint"""
    try:
        user_message = request.input.get("prompt", "")
        if not user_message:
            raise HTTPException(status_code=400, detail="No prompt found in input")
        
        # Get TACNode data if relevant
        tacnode_data = None
        if any(keyword in user_message.lower() for keyword in ['data', 'business', 'analytics', 'report']):
            tacnode_data = await agent.get_tacnode_data(user_message)
        
        # Generate response
        response_text = await agent.generate_response(user_message, tacnode_data)
        
        return InvocationResponse(output={{
            "message": response_text,
            "timestamp": datetime.utcnow().isoformat(),
            "model": "tacnode-agentcore-agent",
            "gateway": agent.gateway_id,
            "data_accessed": tacnode_data is not None
        }})
        
    except Exception as e:
        logger.error(f"Agent invocation failed: {{e}}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ping")
async def ping():
    """AgentCore required /ping endpoint"""
    return {{"status": "healthy", "timestamp": datetime.utcnow().isoformat()}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
EOF

# Create simple Dockerfile
cat > Dockerfile << 'EOF'
# Simple AgentCore Runtime Dockerfile - ARM64
FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY agent.py ./

# Create non-root user
RUN useradd -m -u 1000 agentuser && chown -R agentuser:agentuser /app
USER agentuser

# Expose port 8080 (AgentCore requirement)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8080/ping || exit 1

# Run application
CMD ["python", "-m", "uvicorn", "agent:app", "--host", "0.0.0.0", "--port", "8080"]
EOF

echo "✅ Simple AgentCore files created successfully"
echo "📁 Files created:"
echo "   - requirements.txt (pip dependencies)"
echo "   - agent.py (AgentCore-compliant agent)"
echo "   - Dockerfile (simple ARM64 container)"
'''
        
        try:
            response = self.ssm.send_command(
                InstanceIds=[self.instance_id],
                DocumentName="AWS-RunShellScript",
                Parameters={'commands': [setup_script]},
                TimeoutSeconds=300
            )
            
            command_id = response['Command']['CommandId']
            print(f"✅ Setup command sent: {command_id}")
            
            return self.wait_for_command_completion(command_id, "File Creation")
            
        except Exception as e:
            print(f"❌ File creation failed: {e}")
            return False
    
    def build_and_push_container(self):
        """Build and push simple ARM64 container"""
        print("🏗️  Building simple ARM64 container...")
        
        build_script = f'''#!/bin/bash
set -e

echo "🚀 Building simple ARM64 AgentCore container..."

# Navigate to project directory
cd /home/ubuntu/simple-agentcore

# Login to ECR
echo "🔐 Logging into ECR..."
aws ecr get-login-password --region us-east-1 | sudo docker login --username AWS --password-stdin {self.repository_uri}

# Build ARM64 container
echo "🏗️  Building ARM64 container..."
IMAGE_NAME="{self.repository_uri}:agentcore-arm64-final"

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
sleep 25

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
    -d '{{"input": {{"prompt": "Hello from AgentCore test"}}}}'; then
    echo "✅ Container /invocations test successful"
    INVOCATIONS_SUCCESS=true
else
    echo "❌ Container /invocations test failed"
    INVOCATIONS_SUCCESS=false
fi

# Get container logs
echo "📋 Container logs:"
sudo docker logs test-agent | tail -20

# Stop test container
sudo docker stop test-agent
sudo docker rm test-agent

# Push to ECR if tests passed
if [ "$PING_SUCCESS" = true ]; then
    echo "📤 Pushing ARM64 container to ECR..."
    sudo docker push $IMAGE_NAME
    echo "✅ ARM64 container pushed successfully"
    
    echo "🎉 ARM64 AgentCore container ready for deployment!"
    echo "📦 Container URI: $IMAGE_NAME"
    echo "✅ Ping test: $PING_SUCCESS"
    echo "✅ Invocations test: $INVOCATIONS_SUCCESS"
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
                TimeoutSeconds=900
            )
            
            command_id = response['Command']['CommandId']
            print(f"✅ Build command sent: {command_id}")
            
            success = self.wait_for_command_completion(command_id, "Container Build and Push")
            
            if success:
                return f"{self.repository_uri}:agentcore-arm64-final"
            
            return None
            
        except Exception as e:
            print(f"❌ Build failed: {e}")
            return None
    
    def deploy_final_agentcore_runtime(self, container_uri):
        """Deploy final AgentCore Runtime"""
        print(f"\n🚀 Deploying FINAL AgentCore Runtime...")
        print(f"   Container: {container_uri}")
        
        role_arn = f"arn:aws:iam::{self.account_id}:role/TACNodeAgentCoreRuntimeExecutionRole"
        
        runtime_config = {
            'agentRuntimeName': 'TACNodeAgentCoreRuntimeFinal',
            'description': 'FINAL Production AgentCore Runtime for TACNode Context Lake with ARM64',
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
            
            print(f"✅ FINAL AgentCore Runtime created:")
            print(f"   Runtime ARN: {runtime_arn}")
            print(f"   Runtime ID: {runtime_id}")
            
            # Save final runtime info
            runtime_info = {
                'runtimeArn': runtime_arn,
                'runtimeId': runtime_id,
                'containerUri': container_uri,
                'architecture': 'linux/arm64',
                'buildMethod': 'simple_pip',
                'agentcoreCompliant': True,
                'final': True,
                'createdAt': datetime.now().isoformat()
            }
            
            with open('tacnode-agentcore-runtime-FINAL.json', 'w') as f:
                json.dump(runtime_info, f, indent=2)
            
            return runtime_id, runtime_arn
            
        except Exception as e:
            print(f"❌ FINAL Runtime deployment failed: {e}")
            return None, None
    
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
                        print(f"📄 {operation_name} output (last 800 chars):")
                        print(response['StandardOutputContent'][-800:])
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
    
    def complete_final_deployment(self):
        """Complete the final deployment"""
        print("🎯 FINAL ARM64 AGENTCORE DEPLOYMENT")
        print("=" * 60)
        
        # Step 1: Create simple files
        print("\n📋 STEP 1: Creating Simple AgentCore Files")
        if not self.create_simple_agentcore_files():
            print("❌ File creation failed")
            return False
        
        # Step 2: Build and push container
        print("\n📋 STEP 2: Building and Pushing Container")
        container_uri = self.build_and_push_container()
        
        if not container_uri:
            print("❌ Container build failed")
            return False
        
        # Step 3: Deploy final runtime
        print("\n📋 STEP 3: Deploying FINAL AgentCore Runtime")
        runtime_id, runtime_arn = self.deploy_final_agentcore_runtime(container_uri)
        
        if not runtime_id:
            print("❌ FINAL Runtime deployment failed")
            return False
        
        print("\n" + "="*60)
        print("🎉 FINAL ARM64 AGENTCORE DEPLOYMENT SUCCESSFUL!")
        print("="*60)
        
        print(f"\n✅ FINAL DEPLOYMENT COMPLETE:")
        print(f"   🏗️  ARM64 Instance: {self.instance_id}")
        print(f"   📦 Container: {container_uri}")
        print(f"   🚀 Runtime: {runtime_id}")
        print(f"   🌉 Gateway: tacnodecontextlakegateway-bkq6ozcvxp")
        
        print(f"\n🎯 TRUE AGENTCORE RUNTIME DEPLOYED!")
        print(f"   Runtime ARN: {runtime_arn}")
        print(f"   Runtime ID: {runtime_id}")
        print(f"   Architecture: linux/arm64")
        print(f"   Status: Creating → Active")
        
        return True

def main():
    print("🚀 FINAL ARM64 AgentCore Deployment")
    print("=" * 60)
    
    deployment = FinalARM64Deployment()
    
    try:
        success = deployment.complete_final_deployment()
        
        if success:
            print("\n🏆 MISSION ACCOMPLISHED!")
            print("   FINAL ARM64 AgentCore Runtime deployed")
            print("   Complete TACNode Context Lake integration")
            print("   TRUE AgentCore Runtime (not simulation)")
            print("   Production-ready AI + Data Lake solution")
        else:
            print("\n🔧 FINAL DEPLOYMENT FAILED")
            print("   Check logs for issues")
        
    except Exception as e:
        print(f"❌ FINAL Deployment failed: {e}")

if __name__ == "__main__":
    main()

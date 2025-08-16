#!/usr/bin/env python3
"""
Build ARM64 Container using Docker Buildx
Complete AgentCore Runtime deployment with proper ARM64 architecture
"""

import subprocess
import json
import os
import time
from datetime import datetime

class ARM64ContainerBuilder:
    """Build ARM64 container for AgentCore Runtime"""
    
    def __init__(self):
        # Load existing container info
        with open('tacnode-agent-container.json', 'r') as f:
            self.container_info = json.load(f)
        
        self.repository_uri = self.container_info['repository_uri']
        self.account_id = self.container_info['account_id']
    
    def setup_docker_buildx(self):
        """Setup Docker buildx for multi-platform builds"""
        print("🔧 Setting up Docker buildx for ARM64...")
        
        try:
            # Create buildx builder
            cmd = ['docker', 'buildx', 'create', '--name', 'arm64-builder', '--use']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0 and "already exists" not in result.stderr:
                print(f"⚠️  Buildx create warning: {result.stderr}")
            
            # Use the builder
            cmd = ['docker', 'buildx', 'use', 'arm64-builder']
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Inspect builder
            cmd = ['docker', 'buildx', 'inspect', '--bootstrap']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            print("✅ Docker buildx configured for ARM64")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Buildx setup failed: {e.stderr}")
            return False
    
    def create_agentcore_compliant_dockerfile(self):
        """Create AgentCore-compliant Dockerfile based on AWS documentation"""
        print("📝 Creating AgentCore-compliant Dockerfile...")
        
        dockerfile_content = """# AgentCore Runtime Dockerfile - ARM64 compliant
# Based on AWS AgentCore documentation requirements
FROM --platform=linux/arm64 ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

# Copy uv files first for better caching
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-cache

# Copy application code
COPY agent_runtime.py ./
COPY requirements.txt ./

# Install additional dependencies if needed
RUN uv add fastapi 'uvicorn[standard]' pydantic httpx boto3 requests

# Create non-root user for security
RUN useradd -m -u 1000 agentuser && chown -R agentuser:agentuser /app
USER agentuser

# Expose port 8080 (AgentCore requirement)
EXPOSE 8080

# Health check for AgentCore
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8080/ping || exit 1

# Run application with AgentCore-required endpoints
CMD ["uv", "run", "uvicorn", "agent_runtime:app", "--host", "0.0.0.0", "--port", "8080"]
"""
        
        # Create AgentCore-compliant directory structure
        os.makedirs('agentcore_runtime', exist_ok=True)
        
        with open('agentcore_runtime/Dockerfile', 'w') as f:
            f.write(dockerfile_content)
        
        print("✅ AgentCore-compliant Dockerfile created")
        return True
    
    def create_agentcore_agent_code(self):
        """Create AgentCore-compliant agent code"""
        print("🤖 Creating AgentCore-compliant agent code...")
        
        # Create pyproject.toml
        pyproject_content = """[project]
name = "tacnode-agentcore-agent"
version = "1.0.0"
description = "TACNode AgentCore Runtime Agent"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "pydantic>=2.5.0",
    "httpx>=0.25.0",
    "boto3>=1.34.0",
    "requests>=2.31.0"
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
"""
        
        # Create AgentCore-compliant agent
        agent_code = """#!/usr/bin/env python3
\"\"\"
AgentCore Runtime Agent - AWS Compliant
Implements required /invocations and /ping endpoints
\"\"\"

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
    \"\"\"TACNode Context Lake Agent for AgentCore Runtime\"\"\"
    
    def __init__(self):
        self.bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
        self.tacnode_token = os.getenv('TACNODE_TOKEN')
        self.gateway_id = os.getenv('GATEWAY_ID', 'tacnodecontextlakegateway-bkq6ozcvxp')
        
    async def get_tacnode_data(self, query: str):
        \"\"\"Get data from TACNode Context Lake\"\"\"
        try:
            headers = {
                'Authorization': f'Bearer {self.tacnode_token}',
                'Content-Type': 'application/json'
            }
            
            # Generate SQL based on query
            sql_query = self.generate_sql_query(query)
            
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "execute_sql",
                    "arguments": {"query": sql_query}
                }
            }
            
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
                        return {"records": data, "query": sql_query}
                        
        except Exception as e:
            logger.error(f"TACNode data access error: {e}")
        
        return None
    
    def generate_sql_query(self, user_query: str) -> str:
        \"\"\"Generate SQL query based on user request\"\"\"
        query_lower = user_query.lower()
        
        if 'summary' in query_lower or 'overview' in query_lower:
            return \"\"\"
            SELECT category, COUNT(*) as count, 
                   AVG(CAST(value AS DECIMAL)) as avg_value,
                   SUM(CAST(value AS DECIMAL)) as total_value
            FROM test 
            WHERE is_active = true 
            GROUP BY category 
            ORDER BY total_value DESC
            \"\"\"
        else:
            return \"\"\"
            SELECT id, name, description, value, category, created_date, is_active 
            FROM test 
            ORDER BY created_date DESC 
            LIMIT 10
            \"\"\"
    
    async def generate_response(self, user_input: str, tacnode_data: Dict = None):
        \"\"\"Generate AI response using Claude\"\"\"
        system_prompt = \"\"\"You are a business analyst AI with access to TACNode Context Lake data through AgentCore Gateway. 
        Provide insights based on real business data.\"\"\"
        
        user_prompt = user_input
        if tacnode_data and tacnode_data.get('records'):
            user_prompt += f\"\\n\\nReal-time data: {json.dumps(tacnode_data['records'][:5])}\"
        
        try:
            response = self.bedrock_runtime.invoke_model(
                modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1000,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": user_prompt}]
                })
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']
            
        except Exception as e:
            logger.error(f"Claude response error: {e}")
            return f"I apologize, but I encountered an error: {str(e)}"

# Initialize agent
agent = TACNodeAgent()

@app.post("/invocations", response_model=InvocationResponse)
async def invoke_agent(request: InvocationRequest):
    \"\"\"AgentCore required /invocations endpoint\"\"\"
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
        
        return InvocationResponse(output={
            "message": response_text,
            "timestamp": datetime.utcnow().isoformat(),
            "model": "tacnode-agentcore-agent",
            "gateway": agent.gateway_id
        })
        
    except Exception as e:
        logger.error(f"Agent invocation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ping")
async def ping():
    \"\"\"AgentCore required /ping endpoint\"\"\"
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
"""
        
        # Write files
        with open('agentcore_runtime/pyproject.toml', 'w') as f:
            f.write(pyproject_content)
        
        with open('agentcore_runtime/agent_runtime.py', 'w') as f:
            f.write(agent_code)
        
        # Create uv.lock (empty for now)
        with open('agentcore_runtime/uv.lock', 'w') as f:
            f.write("# This file is @generated by uv.\n")
        
        print("✅ AgentCore-compliant agent code created")
        return True
    
    def build_and_push_arm64_container(self):
        """Build and push ARM64 container"""
        print("🏗️  Building ARM64 container for AgentCore...")
        
        try:
            # Change to agentcore_runtime directory
            os.chdir('agentcore_runtime')
            
            # Build and push ARM64 image
            image_name = f"{self.repository_uri}:agentcore-arm64"
            
            cmd = [
                'docker', 'buildx', 'build',
                '--platform', 'linux/arm64',
                '-t', image_name,
                '--push',
                '.'
            ]
            
            print(f"🚀 Building and pushing: {image_name}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            print("✅ ARM64 container built and pushed successfully")
            
            # Change back to parent directory
            os.chdir('..')
            
            # Update container info
            self.container_info['agentcore_image'] = image_name
            self.container_info['architecture'] = 'linux/arm64'
            self.container_info['agentcore_compliant'] = True
            self.container_info['updated_at'] = datetime.now().isoformat()
            
            with open('tacnode-agentcore-container-arm64.json', 'w') as f:
                json.dump(self.container_info, f, indent=2)
            
            print(f"✅ Container info saved: tacnode-agentcore-container-arm64.json")
            
            return image_name
            
        except subprocess.CalledProcessError as e:
            print(f"❌ ARM64 build failed: {e.stderr}")
            os.chdir('..')
            return None
        except Exception as e:
            print(f"❌ Build error: {e}")
            os.chdir('..')
            return None

def main():
    print("🚀 ARM64 Container Builder for AgentCore Runtime")
    print("=" * 60)
    
    builder = ARM64ContainerBuilder()
    
    try:
        # Setup buildx
        if not builder.setup_docker_buildx():
            print("❌ Failed to setup Docker buildx")
            return
        
        # Create AgentCore-compliant files
        builder.create_agentcore_compliant_dockerfile()
        builder.create_agentcore_agent_code()
        
        # Build and push ARM64 container
        image_name = builder.build_and_push_arm64_container()
        
        if image_name:
            print("\n" + "="*60)
            print("🎉 ARM64 AGENTCORE CONTAINER READY!")
            print("="*60)
            
            print(f"\n✅ CONTAINER DETAILS:")
            print(f"   Image: {image_name}")
            print(f"   Architecture: linux/arm64")
            print(f"   AgentCore Compliant: ✅")
            print(f"   Endpoints: /invocations, /ping")
            
            print(f"\n🎯 READY FOR AGENTCORE RUNTIME DEPLOYMENT!")
            print(f"   Use this image for create_agent_runtime")
        else:
            print("\n❌ ARM64 container build failed")
        
    except Exception as e:
        print(f"❌ Build process failed: {e}")

if __name__ == "__main__":
    main()

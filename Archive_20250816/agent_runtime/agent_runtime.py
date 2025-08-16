#!/usr/bin/env python3
"""
TACNode AgentCore Runtime
Custom agent that integrates Claude with AgentCore Gateway for TACNode Context Lake access
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

import boto3
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
import uvicorn
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentRequest(BaseModel):
    """Request model for agent invocations"""
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    """Response model for agent responses"""
    response: str
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class TACNodeAgentRuntime:
    """Custom AgentCore Runtime for TACNode Context Lake integration"""
    
    def __init__(self):
        self.app = FastAPI(title="TACNode AgentCore Runtime", version="1.0.0")
        self.bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
        self.gateway_id = "tacnodecontextlakegateway-bkq6ozcvxp"
        self.tacnode_token = os.getenv('TACNODE_TOKEN')
        
        # Setup routes
        self.setup_routes()
        
        logger.info("TACNode AgentCore Runtime initialized")
    
    def setup_routes(self):
        """Setup FastAPI routes for the agent runtime"""
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}
        
        @self.app.post("/invoke", response_model=AgentResponse)
        async def invoke_agent(request: AgentRequest):
            """Main agent invocation endpoint"""
            try:
                logger.info(f"Agent invocation: {request.message[:100]}...")
                
                # Process the request through our agent
                response = await self.process_agent_request(request)
                
                return AgentResponse(
                    response=response,
                    session_id=request.session_id,
                    metadata={
                        "timestamp": datetime.now().isoformat(),
                        "model": "claude-3-5-sonnet",
                        "gateway": self.gateway_id
                    }
                )
                
            except Exception as e:
                logger.error(f"Agent invocation failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/stream")
        async def stream_agent(request: AgentRequest):
            """Streaming agent invocation endpoint"""
            try:
                return StreamingResponse(
                    self.stream_agent_response(request),
                    media_type="text/plain"
                )
            except Exception as e:
                logger.error(f"Streaming failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    async def process_agent_request(self, request: AgentRequest) -> str:
        """Process agent request with TACNode data integration"""
        
        # Step 1: Analyze the request to determine if TACNode data is needed
        needs_data = await self.analyze_request_for_data_needs(request.message)
        
        # Step 2: Get TACNode data if needed
        tacnode_data = None
        if needs_data:
            tacnode_data = await self.get_tacnode_data(request.message)
        
        # Step 3: Generate Claude response with context
        response = await self.generate_claude_response(request.message, tacnode_data, request.context)
        
        return response
    
    async def analyze_request_for_data_needs(self, message: str) -> bool:
        """Analyze if the request needs TACNode data"""
        data_keywords = [
            'data', 'records', 'business', 'category', 'value', 'analytics',
            'report', 'summary', 'trends', 'insights', 'metrics', 'performance',
            'revenue', 'sales', 'financial', 'statistics', 'analysis'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in data_keywords)
    
    async def get_tacnode_data(self, query: str) -> Optional[Dict[str, Any]]:
        """Get relevant data from TACNode Context Lake"""
        try:
            logger.info("Fetching data from TACNode Context Lake...")
            
            # Determine what type of data query to make based on the user query
            sql_query = self.generate_sql_query(query)
            
            headers = {
                'Authorization': f'Bearer {self.tacnode_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "execute_sql",
                    "arguments": {
                        "query": sql_query
                    }
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
                        logger.info(f"Retrieved {len(data)} records from TACNode")
                        return {"records": data, "query": sql_query}
                    
        except Exception as e:
            logger.error(f"Error fetching TACNode data: {e}")
        
        return None
    
    def generate_sql_query(self, user_query: str) -> str:
        """Generate appropriate SQL query based on user request"""
        query_lower = user_query.lower()
        
        if 'summary' in query_lower or 'overview' in query_lower:
            return """
            SELECT category, COUNT(*) as count, 
                   AVG(CAST(value AS DECIMAL)) as avg_value,
                   SUM(CAST(value AS DECIMAL)) as total_value
            FROM test 
            WHERE is_active = true 
            GROUP BY category 
            ORDER BY total_value DESC
            """
        elif 'recent' in query_lower or 'latest' in query_lower:
            return """
            SELECT name, description, value, category, created_date 
            FROM test 
            WHERE is_active = true 
            ORDER BY created_date DESC 
            LIMIT 5
            """
        elif 'high' in query_lower and 'value' in query_lower:
            return """
            SELECT name, value, category, is_active 
            FROM test 
            WHERE CAST(value AS DECIMAL) > 100 
            ORDER BY CAST(value AS DECIMAL) DESC
            """
        elif 'trend' in query_lower or 'time' in query_lower:
            return """
            SELECT DATE(created_date) as date, 
                   COUNT(*) as records,
                   AVG(CAST(value AS DECIMAL)) as avg_value
            FROM test 
            GROUP BY DATE(created_date) 
            ORDER BY date DESC
            """
        else:
            # Default: get all active records
            return """
            SELECT id, name, description, value, category, created_date, is_active 
            FROM test 
            ORDER BY created_date DESC 
            LIMIT 10
            """
    
    async def generate_claude_response(self, message: str, tacnode_data: Optional[Dict], context: Optional[Dict]) -> str:
        """Generate Claude response with TACNode data context"""
        
        # Build system prompt
        system_prompt = """You are a business data analyst AI agent with access to real-time business data from TACNode Context Lake through AWS Bedrock AgentCore Gateway.

Your capabilities include:
- Analyzing live business data from TACNode Context Lake
- Providing data-driven insights and recommendations
- Answering questions about business metrics, trends, and performance
- Generating executive-level business intelligence reports

You have access to business records with the following structure:
- id: Unique identifier
- name: Record name
- description: Record description
- value: Monetary value (can be positive or negative)
- category: Business category (Category 1, 2, 3)
- created_date: When the record was created
- is_active: Whether the record is currently active

Always provide specific, actionable insights based on the real data available."""

        # Build user prompt with data context
        user_prompt = message
        
        if tacnode_data and tacnode_data.get('records'):
            data_context = f"""

REAL-TIME DATA FROM TACNODE CONTEXT LAKE:
Query executed: {tacnode_data.get('query', 'N/A')}
Records retrieved: {len(tacnode_data['records'])}

Data:
{json.dumps(tacnode_data['records'], indent=2)}

Please analyze this real data to answer the user's question."""
            
            user_prompt += data_context
        
        try:
            # Call Claude through Bedrock
            response = self.bedrock_runtime.invoke_model(
                modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 2000,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": user_prompt}]
                })
            )
            
            response_body = json.loads(response['body'].read())
            claude_response = response_body['content'][0]['text']
            
            logger.info("Generated Claude response successfully")
            return claude_response
            
        except Exception as e:
            logger.error(f"Error generating Claude response: {e}")
            return f"I apologize, but I encountered an error while processing your request: {str(e)}"
    
    async def stream_agent_response(self, request: AgentRequest):
        """Stream agent response for real-time interaction"""
        try:
            # For streaming, we'll simulate streaming by yielding chunks
            response = await self.process_agent_request(request)
            
            # Split response into chunks for streaming
            words = response.split()
            for i in range(0, len(words), 5):  # 5 words per chunk
                chunk = " ".join(words[i:i+5]) + " "
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                await asyncio.sleep(0.1)  # Small delay for streaming effect
            
            yield f"data: {json.dumps({'done': True})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

def create_app():
    """Create and configure the FastAPI application"""
    runtime = TACNodeAgentRuntime()
    return runtime.app

if __name__ == "__main__":
    app = create_app()
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

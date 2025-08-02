#!/usr/bin/env python3
"""
AgentCore Demo Agent
Demonstrates integration of AWS Bedrock AgentCore, Strands SDK, and Tacnode Context Lake
"""

import os
import asyncio
import logging
from typing import Dict, Any, List
from dataclasses import dataclass

from strands import Agent
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AgentConfig:
    """Configuration for the demo agent"""
    model_id: str = "bedrock:anthropic.claude-3-7-sonnet-20241022-v1:0"
    tacnode_endpoint: str = os.getenv("TACNODE_ENDPOINT", "")
    tacnode_api_key: str = os.getenv("TACNODE_API_KEY", "")
    tacnode_mcp_token: str = os.getenv("TACNODE_MCP_TOKEN", "")
    max_iterations: int = 10
    timeout: int = 300

class TacnodeAgent:
    """
    Demo agent that integrates with Tacnode Context Lake via MCP protocol
    """
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.agent = None
        self.mcp_client = None
        
    async def initialize(self):
        """Initialize the agent with Tacnode MCP tools"""
        try:
            # Initialize Tacnode MCP client
            self.mcp_client = MCPClient(lambda: stdio_client(
                StdioServerParameters(
                    command="npx",
                    args=[
                        "mcp-remote",
                        f"{self.config.tacnode_endpoint}/mcp",
                        "--header",
                        f"Authorization: Bearer {self.config.tacnode_mcp_token}"
                    ]
                )
            ))
            
            # Get available tools from Tacnode
            async with self.mcp_client:
                tools = await self.mcp_client.list_tools()
                logger.info(f"Loaded {len(tools)} tools from Tacnode MCP server")
                
                # Create agent with system prompt and tools
                self.agent = Agent(
                    model=self.config.model_id,
                    system_prompt=self._get_system_prompt(),
                    tools=tools,
                    max_iterations=self.config.max_iterations
                )
                
            logger.info("Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            raise
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the agent"""
        return """
        You are an intelligent data agent powered by Tacnode Context Lake.
        
        Your capabilities include:
        - Querying real-time data with millisecond latency
        - Handling structured, JSON, GIS, and vector data types
        - Providing contextual insights and analysis
        - Supporting natural language queries
        
        Guidelines:
        1. Always understand the user's intent before querying data
        2. Use appropriate Tacnode tools for data retrieval
        3. Provide clear, actionable insights
        4. Handle errors gracefully and suggest alternatives
        5. Maintain context across the conversation
        
        Available data types in Tacnode Context Lake:
        - Structured data (SQL tables)
        - JSON documents
        - Geospatial data (GIS)
        - Vector embeddings for semantic search
        - Time series data
        
        When querying data:
        - Use SQL for structured queries
        - Use vector search for semantic similarity
        - Combine multiple data types when needed
        - Optimize for performance and accuracy
        """
    
    async def query(self, user_input: str, session_id: str = None) -> Dict[str, Any]:
        """
        Process a user query and return the response
        
        Args:
            user_input: Natural language query from the user
            session_id: Optional session identifier for context
            
        Returns:
            Dictionary containing response and metadata
        """
        if not self.agent:
            raise RuntimeError("Agent not initialized. Call initialize() first.")
        
        try:
            logger.info(f"Processing query: {user_input}")
            
            # Process the query with the agent
            async with self.mcp_client:
                response = await self.agent.arun(user_input)
                
            # Extract metadata
            metadata = {
                "session_id": session_id,
                "model_used": self.config.model_id,
                "tools_available": len(await self.mcp_client.list_tools()) if self.mcp_client else 0,
                "response_length": len(response) if response else 0
            }
            
            logger.info("Query processed successfully")
            
            return {
                "response": response,
                "metadata": metadata,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "response": f"I apologize, but I encountered an error: {str(e)}",
                "metadata": {"error": str(e)},
                "status": "error"
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check of the agent and its dependencies
        
        Returns:
            Dictionary containing health status
        """
        health_status = {
            "agent_initialized": self.agent is not None,
            "mcp_client_available": self.mcp_client is not None,
            "tacnode_connection": False,
            "tools_count": 0
        }
        
        try:
            if self.mcp_client:
                async with self.mcp_client:
                    tools = await self.mcp_client.list_tools()
                    health_status["tools_count"] = len(tools)
                    health_status["tacnode_connection"] = True
                    
        except Exception as e:
            logger.warning(f"Health check failed for Tacnode connection: {e}")
            health_status["error"] = str(e)
        
        return health_status

# Example usage and demo scenarios
async def run_demo_scenarios():
    """Run demonstration scenarios"""
    
    # Initialize configuration
    config = AgentConfig()
    
    # Validate configuration
    if not config.tacnode_endpoint or not config.tacnode_api_key:
        logger.error("Tacnode configuration missing. Please set TACNODE_ENDPOINT and TACNODE_API_KEY environment variables.")
        return
    
    # Create and initialize agent
    agent = TacnodeAgent(config)
    await agent.initialize()
    
    # Health check
    health = await agent.health_check()
    logger.info(f"Health check: {health}")
    
    # Demo scenarios
    demo_queries = [
        "What data sources are available in the Context Lake?",
        "Show me the schema of the main customer table",
        "Find customers who made purchases in the last 24 hours",
        "What are the top 5 products by sales volume this month?",
        "Analyze customer behavior patterns using vector similarity"
    ]
    
    for i, query in enumerate(demo_queries, 1):
        print(f"\n--- Demo Scenario {i} ---")
        print(f"Query: {query}")
        
        result = await agent.query(query, session_id=f"demo-session-{i}")
        
        print(f"Status: {result['status']}")
        print(f"Response: {result['response']}")
        print(f"Metadata: {result['metadata']}")
        
        # Add delay between queries
        await asyncio.sleep(2)

async def interactive_mode():
    """Run the agent in interactive mode"""
    
    config = AgentConfig()
    agent = TacnodeAgent(config)
    
    try:
        await agent.initialize()
        print("AgentCore Demo Agent initialized successfully!")
        print("Type 'quit' to exit, 'health' for health check")
        print("-" * 50)
        
        session_id = "interactive-session"
        
        while True:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            elif user_input.lower() == 'health':
                health = await agent.health_check()
                print(f"Health Status: {health}")
                continue
            elif not user_input:
                continue
            
            result = await agent.query(user_input, session_id)
            print(f"\nAgent: {result['response']}")
            
            if result['status'] == 'error':
                print(f"Error details: {result['metadata'].get('error', 'Unknown error')}")
                
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        logger.error(f"Error in interactive mode: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        # Run demo scenarios
        asyncio.run(run_demo_scenarios())
    else:
        # Run interactive mode
        asyncio.run(interactive_mode())

#!/usr/bin/env python3
"""
Multi-MCP Agent Example
Demonstrates integration of multiple MCP servers with AgentCore
"""

import asyncio
import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, List

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from strands import Agent
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultiMCPAgent:
    """
    Advanced agent that integrates multiple MCP servers for enhanced capabilities
    """
    
    def __init__(self):
        self.mcp_clients = {}
        self.agent = None
        
    async def initialize_mcp_servers(self):
        """Initialize all available MCP servers"""
        
        # Sequential Thinking Server
        try:
            self.mcp_clients['thinking'] = MCPClient(lambda: stdio_client(
                StdioServerParameters(
                    command="npx",
                    args=["@modelcontextprotocol/server-sequential-thinking"]
                )
            ))
            logger.info("✅ Sequential Thinking server configured")
        except Exception as e:
            logger.warning(f"⚠️  Sequential Thinking server not available: {e}")
        
        # AWS Documentation Server
        try:
            self.mcp_clients['aws_docs'] = MCPClient(lambda: stdio_client(
                StdioServerParameters(
                    command="uvx",
                    args=["awslabs.aws-documentation-mcp-server@latest"],
                    env={
                        "FASTMCP_LOG_LEVEL": "ERROR",
                        "AWS_DOCUMENTATION_PARTITION": "aws"
                    }
                )
            ))
            logger.info("✅ AWS Documentation server configured")
        except Exception as e:
            logger.warning(f"⚠️  AWS Documentation server not available: {e}")
        
        # Playwright Server
        try:
            playwright_path = "/home/ubuntu/AugmentFile/mcp-playwright/dist/index.js"
            if os.path.exists(playwright_path):
                self.mcp_clients['playwright'] = MCPClient(lambda: stdio_client(
                    StdioServerParameters(
                        command="node",
                        args=[playwright_path],
                        cwd="/home/ubuntu/AugmentFile/mcp-playwright"
                    )
                ))
                logger.info("✅ Playwright server configured")
            else:
                logger.warning("⚠️  Playwright server not found at expected path")
        except Exception as e:
            logger.warning(f"⚠️  Playwright server not available: {e}")
        
        # Fetch Server
        try:
            self.mcp_clients['fetch'] = MCPClient(lambda: stdio_client(
                StdioServerParameters(
                    command="uvx",
                    args=["mcp-server-fetch"]
                )
            ))
            logger.info("✅ Fetch server configured")
        except Exception as e:
            logger.warning(f"⚠️  Fetch server not available: {e}")
        
        # GitHub Server
        try:
            github_path = "/home/ubuntu/AugmentFile/github-mcp-server/github-mcp-server"
            github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
            if os.path.exists(github_path) and github_token:
                self.mcp_clients['github'] = MCPClient(lambda: stdio_client(
                    StdioServerParameters(
                        command=github_path,
                        args=["stdio"],
                        env={"GITHUB_PERSONAL_ACCESS_TOKEN": github_token}
                    )
                ))
                logger.info("✅ GitHub server configured")
            else:
                logger.warning("⚠️  GitHub server not available (missing binary or token)")
        except Exception as e:
            logger.warning(f"⚠️  GitHub server not available: {e}")

        # Tacnode Context Lake (if configured)
        tacnode_endpoint = os.getenv("TACNODE_ENDPOINT")
        tacnode_token = os.getenv("TACNODE_MCP_TOKEN")
        if tacnode_endpoint and tacnode_token:
            try:
                self.mcp_clients['tacnode'] = MCPClient(lambda: stdio_client(
                    StdioServerParameters(
                        command="npx",
                        args=[
                            "mcp-remote",
                            f"{tacnode_endpoint}/mcp",
                            "--header",
                            f"Authorization: Bearer {tacnode_token}"
                        ]
                    )
                ))
                logger.info("✅ Tacnode Context Lake server configured")
            except Exception as e:
                logger.warning(f"⚠️  Tacnode server not available: {e}")
    
    async def collect_all_tools(self):
        """Collect tools from all available MCP servers"""
        all_tools = []
        
        for server_name, client in self.mcp_clients.items():
            try:
                async with client:
                    tools = await client.list_tools()
                    logger.info(f"Loaded {len(tools)} tools from {server_name}")
                    all_tools.extend(tools)
            except Exception as e:
                logger.warning(f"Failed to load tools from {server_name}: {e}")
        
        return all_tools
    
    async def initialize_agent(self):
        """Initialize the agent with all available tools"""
        await self.initialize_mcp_servers()
        
        # Collect all tools from all servers
        all_tools = await self.collect_all_tools()
        
        # Create agent with comprehensive system prompt
        system_prompt = self._get_comprehensive_system_prompt()
        
        self.agent = Agent(
            model="bedrock:anthropic.claude-3-7-sonnet-20241022-v1:0",
            system_prompt=system_prompt,
            tools=all_tools,
            max_iterations=15
        )
        
        logger.info(f"Agent initialized with {len(all_tools)} tools from {len(self.mcp_clients)} MCP servers")
    
    def _get_comprehensive_system_prompt(self):
        """Get comprehensive system prompt for multi-MCP agent"""
        return """
        You are an advanced AI agent with access to multiple specialized capabilities through MCP servers:
        
        🧠 **Sequential Thinking**: Use for complex reasoning, analysis, and structured problem-solving
        📚 **AWS Documentation**: Access comprehensive AWS documentation, search, and recommendations
        🎭 **Playwright**: Automate web browsers, take screenshots, interact with web pages
        🌐 **Web Fetch**: Retrieve web content and search the internet
        🐙 **GitHub**: Manage repositories, issues, PRs, code analysis, and workflows
        🏗️ **Tacnode Context Lake**: Query real-time data with millisecond latency (if configured)
        
        **Capabilities by Domain:**
        
        **Data Analysis & Research:**
        - Use Sequential Thinking for complex analytical reasoning
        - Use AWS Documentation for cloud architecture questions
        - Use Web Fetch for general research and information gathering
        - Use Tacnode for real-time data queries (if available)
        
        **Web Automation & Testing:**
        - Use Playwright for browser automation
        - Use Playwright for taking screenshots and web testing
        - Use Web Fetch for simple content retrieval
        
        **Cloud & Infrastructure:**
        - Use AWS Documentation for AWS-specific questions
        - Use Sequential Thinking for architecture planning
        - Use Tacnode for infrastructure monitoring data (if available)

        **Development & Code Management:**
        - Use GitHub for repository operations, code analysis, and issue management
        - Use Sequential Thinking for code review and architecture decisions
        - Use Playwright for testing web applications
        
        **Guidelines:**
        1. **Choose the right tool** for each task based on the capabilities above
        2. **Combine tools** when needed for comprehensive solutions
        3. **Use Sequential Thinking** for complex multi-step problems
        4. **Provide clear explanations** of your reasoning and tool choices
        5. **Handle errors gracefully** and suggest alternatives
        
        Always explain which tools you're using and why they're appropriate for the task.
        """
    
    async def query(self, user_input: str, session_id: str = None) -> Dict[str, Any]:
        """Process a query using the multi-MCP agent"""
        if not self.agent:
            raise RuntimeError("Agent not initialized. Call initialize_agent() first.")
        
        try:
            logger.info(f"Processing multi-MCP query: {user_input}")
            
            # Process with all available MCP clients
            for client in self.mcp_clients.values():
                async with client:
                    pass  # Keep connections alive during processing
            
            response = await self.agent.arun(user_input)
            
            return {
                "response": response,
                "metadata": {
                    "session_id": session_id,
                    "servers_used": list(self.mcp_clients.keys()),
                    "tools_available": len(await self.collect_all_tools()) if self.mcp_clients else 0
                },
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "response": f"I encountered an error: {str(e)}",
                "metadata": {"error": str(e)},
                "status": "error"
            }

async def demo_multi_mcp_scenarios():
    """Demonstrate multi-MCP agent capabilities"""
    
    print("🚀 Multi-MCP Agent Demo")
    print("=" * 50)
    
    # Initialize agent
    agent = MultiMCPAgent()
    await agent.initialize_agent()
    
    # Demo scenarios that showcase different MCP servers
    scenarios = [
        {
            "name": "Complex AWS Architecture Analysis",
            "query": "I need to design a scalable web application on AWS. Can you help me think through the architecture step by step, and provide relevant AWS documentation?",
            "expected_tools": ["Sequential Thinking", "AWS Documentation"]
        },
        {
            "name": "Web Research with Screenshots",
            "query": "Research the latest trends in AI agents and take a screenshot of a relevant website",
            "expected_tools": ["Web Fetch", "Playwright"]
        },
        {
            "name": "Data Analysis with Real-time Context",
            "query": "Analyze the current system performance and provide insights",
            "expected_tools": ["Sequential Thinking", "Tacnode Context Lake"]
        },
        {
            "name": "GitHub Repository Analysis",
            "query": "Analyze the structure and recent activity of a GitHub repository, and suggest improvements",
            "expected_tools": ["GitHub", "Sequential Thinking"]
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n--- Scenario {i}: {scenario['name']} ---")
        print(f"Query: {scenario['query']}")
        print(f"Expected tools: {', '.join(scenario['expected_tools'])}")
        
        result = await agent.query(scenario['query'], f"demo-{i}")
        
        print(f"Status: {result['status']}")
        print(f"Response: {result['response'][:200]}...")  # First 200 chars
        print(f"Servers available: {result['metadata'].get('servers_used', [])}")
        
        await asyncio.sleep(2)  # Brief pause between scenarios

async def interactive_multi_mcp_mode():
    """Interactive mode with multi-MCP agent"""
    
    agent = MultiMCPAgent()
    await agent.initialize_agent()
    
    print("🤖 Multi-MCP Agent Interactive Mode")
    print("Available capabilities:")
    print("- 🧠 Sequential Thinking for complex reasoning")
    print("- 📚 AWS Documentation access")
    print("- 🎭 Playwright for web automation")
    print("- 🌐 Web content fetching")
    print("- 🐙 GitHub repository management")
    print("- 🏗️ Tacnode Context Lake (if configured)")
    print("\nType 'quit' to exit, 'help' for guidance")
    print("-" * 60)
    
    session_id = "interactive-multi-mcp"
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        elif user_input.lower() == 'help':
            print("\nExample queries:")
            print("- 'Help me design an AWS serverless architecture'")
            print("- 'Take a screenshot of example.com'")
            print("- 'Research the latest AI developments'")
            print("- 'Analyze this complex problem step by step'")
            print("- 'Show me recent issues in my GitHub repository'")
            print("- 'Help me review this pull request'")
            continue
        elif not user_input:
            continue
        
        result = await agent.query(user_input, session_id)
        print(f"\n🤖 Agent: {result['response']}")
        
        if result['status'] == 'error':
            print(f"⚠️  Error: {result['metadata'].get('error')}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        asyncio.run(demo_multi_mcp_scenarios())
    else:
        asyncio.run(interactive_multi_mcp_mode())

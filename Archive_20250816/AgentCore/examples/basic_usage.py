#!/usr/bin/env python3
"""
Basic Usage Example for AgentCore Demo
Demonstrates simple integration with Tacnode Context Lake
"""

import asyncio
import os
import sys
import logging
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent.demo_agent import TacnodeAgent, AgentConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def basic_query_example():
    """Basic example of querying data through the agent"""
    
    print("=== Basic Query Example ===")
    
    # Create agent configuration
    config = AgentConfig()
    
    # Initialize agent
    agent = TacnodeAgent(config)
    await agent.initialize()
    
    # Simple query
    query = "What tables are available in the database?"
    print(f"Query: {query}")
    
    result = await agent.query(query)
    print(f"Response: {result['response']}")
    print(f"Status: {result['status']}")
    
    return result

async def data_analysis_example():
    """Example of data analysis queries"""
    
    print("\n=== Data Analysis Example ===")
    
    config = AgentConfig()
    agent = TacnodeAgent(config)
    await agent.initialize()
    
    # Analysis queries
    queries = [
        "Show me the schema of the customers table",
        "Count the total number of records in each table",
        "Find the most recent data updates across all tables"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        result = await agent.query(query)
        print(f"Response: {result['response']}")
        
        if result['status'] == 'error':
            print(f"Error: {result['metadata'].get('error')}")

async def real_time_monitoring_example():
    """Example of real-time monitoring capabilities"""
    
    print("\n=== Real-Time Monitoring Example ===")
    
    config = AgentConfig()
    agent = TacnodeAgent(config)
    await agent.initialize()
    
    # Monitoring queries
    queries = [
        "Show me current system statistics",
        "What's the data freshness for the main tables?",
        "Are there any performance issues I should be aware of?"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        result = await agent.query(query)
        print(f"Response: {result['response']}")

async def business_intelligence_example():
    """Example of business intelligence queries"""
    
    print("\n=== Business Intelligence Example ===")
    
    config = AgentConfig()
    agent = TacnodeAgent(config)
    await agent.initialize()
    
    # BI queries
    queries = [
        "What are the top 10 customers by transaction volume?",
        "Show me sales trends for the last 30 days",
        "Identify any unusual patterns in customer behavior",
        "Generate a summary report of key business metrics"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        result = await agent.query(query)
        print(f"Response: {result['response']}")
        
        # Add small delay between queries
        await asyncio.sleep(1)

async def error_handling_example():
    """Example of error handling and recovery"""
    
    print("\n=== Error Handling Example ===")
    
    config = AgentConfig()
    agent = TacnodeAgent(config)
    await agent.initialize()
    
    # Queries that might cause errors
    queries = [
        "SELECT * FROM non_existent_table",  # Invalid SQL
        "Show me data from yesterday's moon landing",  # Nonsensical request
        "",  # Empty query
        "What is the meaning of life?"  # Non-data related query
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        result = await agent.query(query)
        print(f"Response: {result['response']}")
        print(f"Status: {result['status']}")
        
        if result['status'] == 'error':
            print(f"Error handled gracefully: {result['metadata'].get('error')}")

async def performance_test_example():
    """Example of performance testing with concurrent queries"""
    
    print("\n=== Performance Test Example ===")
    
    config = AgentConfig()
    agent = TacnodeAgent(config)
    await agent.initialize()
    
    # Create multiple concurrent queries
    queries = [
        "Count records in the main tables",
        "Show current system time",
        "List available data sources",
        "Get database size information",
        "Show active connections"
    ]
    
    print(f"Running {len(queries)} concurrent queries...")
    
    # Execute queries concurrently
    tasks = [agent.query(query, f"perf-test-{i}") for i, query in enumerate(queries)]
    results = await asyncio.gather(*tasks)
    
    # Display results
    for i, result in enumerate(results):
        print(f"\nQuery {i+1}: {queries[i]}")
        print(f"Status: {result['status']}")
        print(f"Response length: {len(result['response'])} characters")
        
        if 'execution_time_ms' in result.get('metadata', {}):
            print(f"Execution time: {result['metadata']['execution_time_ms']}ms")

async def health_check_example():
    """Example of health checking"""
    
    print("\n=== Health Check Example ===")
    
    config = AgentConfig()
    agent = TacnodeAgent(config)
    
    # Check health before initialization
    print("Health check before initialization:")
    health = await agent.health_check()
    print(f"Health status: {health}")
    
    # Initialize and check again
    await agent.initialize()
    print("\nHealth check after initialization:")
    health = await agent.health_check()
    print(f"Health status: {health}")

async def main():
    """Run all examples"""
    
    print("AgentCore Demo - Basic Usage Examples")
    print("=" * 50)
    
    # Check environment variables
    required_vars = ["TACNODE_ENDPOINT", "TACNODE_API_KEY", "TACNODE_MCP_TOKEN"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Error: Missing required environment variables: {missing_vars}")
        print("Please set these variables before running the examples.")
        return
    
    try:
        # Run examples
        await health_check_example()
        await basic_query_example()
        await data_analysis_example()
        await real_time_monitoring_example()
        await business_intelligence_example()
        await error_handling_example()
        await performance_test_example()
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        
    except Exception as e:
        logger.error(f"Error running examples: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())

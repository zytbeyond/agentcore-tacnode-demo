"""
Tacnode Context Lake Tools for AgentCore Demo
Custom tools for interacting with Tacnode Context Lake
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional
import aiohttp
import psycopg2
from psycopg2.extras import RealDictCursor
from strands.tools import tool

logger = logging.getLogger(__name__)

class TacnodeClient:
    """Client for interacting with Tacnode Context Lake"""
    
    def __init__(self, endpoint: str, api_key: str):
        self.endpoint = endpoint.rstrip('/')
        self.api_key = api_key
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def execute_query(self, query: str, parameters: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute a SQL query against Tacnode Context Lake"""
        try:
            payload = {
                "query": query,
                "parameters": parameters or {}
            }
            
            async with self.session.post(f"{self.endpoint}/api/v1/query", json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "success": True,
                        "data": result.get("data", []),
                        "columns": result.get("columns", []),
                        "row_count": result.get("row_count", 0),
                        "execution_time_ms": result.get("execution_time_ms", 0)
                    }
                else:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}: {error_text}"
                    }
                    
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def vector_search(self, query_vector: List[float], table: str, 
                          vector_column: str = "embedding", top_k: int = 10,
                          filters: Optional[Dict] = None) -> Dict[str, Any]:
        """Perform vector similarity search"""
        try:
            payload = {
                "query_vector": query_vector,
                "table": table,
                "vector_column": vector_column,
                "top_k": top_k,
                "filters": filters or {}
            }
            
            async with self.session.post(f"{self.endpoint}/api/v1/vector-search", json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "success": True,
                        "results": result.get("results", []),
                        "execution_time_ms": result.get("execution_time_ms", 0)
                    }
                else:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}: {error_text}"
                    }
                    
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# Initialize Tacnode client
tacnode_client = TacnodeClient(
    endpoint=os.getenv("TACNODE_ENDPOINT", ""),
    api_key=os.getenv("TACNODE_API_KEY", "")
)

@tool
async def tacnode_query(query: str, parameters: Optional[Dict] = None) -> str:
    """
    Execute a SQL query against Tacnode Context Lake.
    
    Args:
        query: SQL query string
        parameters: Optional query parameters for parameterized queries
        
    Returns:
        JSON string containing query results
    """
    if not tacnode_client.endpoint or not tacnode_client.api_key:
        return json.dumps({
            "error": "Tacnode configuration missing. Please set TACNODE_ENDPOINT and TACNODE_API_KEY."
        })
    
    async with tacnode_client as client:
        result = await client.execute_query(query, parameters)
        
    if result["success"]:
        return json.dumps({
            "data": result["data"],
            "columns": result["columns"],
            "row_count": result["row_count"],
            "execution_time_ms": result["execution_time_ms"]
        }, indent=2)
    else:
        return json.dumps({
            "error": result["error"]
        })

@tool
async def tacnode_vector_search(query_text: str, table: str, 
                              vector_column: str = "embedding", 
                              top_k: int = 10) -> str:
    """
    Perform semantic search using vector embeddings in Tacnode Context Lake.
    
    Args:
        query_text: Text to search for semantically similar content
        table: Table name containing vector embeddings
        vector_column: Column name containing the vector embeddings
        top_k: Number of top results to return
        
    Returns:
        JSON string containing search results
    """
    # Note: In a real implementation, you would convert query_text to embeddings
    # using a model like Amazon Bedrock Titan Embeddings
    
    # For demo purposes, we'll use a placeholder vector
    # In production, you would do something like:
    # query_vector = await get_embeddings(query_text)
    
    placeholder_vector = [0.1] * 1536  # Typical embedding dimension
    
    async with tacnode_client as client:
        result = await client.vector_search(
            query_vector=placeholder_vector,
            table=table,
            vector_column=vector_column,
            top_k=top_k
        )
    
    if result["success"]:
        return json.dumps({
            "query_text": query_text,
            "results": result["results"],
            "execution_time_ms": result["execution_time_ms"]
        }, indent=2)
    else:
        return json.dumps({
            "error": result["error"]
        })

@tool
async def tacnode_schema_info(table_name: Optional[str] = None) -> str:
    """
    Get schema information for tables in Tacnode Context Lake.
    
    Args:
        table_name: Optional specific table name. If not provided, lists all tables.
        
    Returns:
        JSON string containing schema information
    """
    if table_name:
        query = """
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = %s
        ORDER BY ordinal_position
        """
        parameters = {"table_name": table_name}
    else:
        query = """
        SELECT table_name, table_type
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
        """
        parameters = None
    
    async with tacnode_client as client:
        result = await client.execute_query(query, parameters)
    
    if result["success"]:
        return json.dumps({
            "table_name": table_name,
            "schema_info": result["data"],
            "execution_time_ms": result["execution_time_ms"]
        }, indent=2)
    else:
        return json.dumps({
            "error": result["error"]
        })

@tool
async def tacnode_real_time_stats() -> str:
    """
    Get real-time statistics about the Tacnode Context Lake instance.
    
    Returns:
        JSON string containing system statistics
    """
    query = """
    SELECT 
        current_timestamp as current_time,
        (SELECT count(*) FROM pg_stat_activity WHERE state = 'active') as active_connections,
        (SELECT count(*) FROM pg_stat_activity) as total_connections,
        pg_database_size(current_database()) as database_size_bytes
    """
    
    async with tacnode_client as client:
        result = await client.execute_query(query)
    
    if result["success"]:
        stats = result["data"][0] if result["data"] else {}
        return json.dumps({
            "system_stats": stats,
            "execution_time_ms": result["execution_time_ms"]
        }, indent=2)
    else:
        return json.dumps({
            "error": result["error"]
        })

@tool
async def tacnode_data_freshness(table_name: str, timestamp_column: str = "created_at") -> str:
    """
    Check data freshness for a specific table in Tacnode Context Lake.
    
    Args:
        table_name: Name of the table to check
        timestamp_column: Column name containing timestamps
        
    Returns:
        JSON string containing freshness information
    """
    query = f"""
    SELECT 
        MAX({timestamp_column}) as latest_record,
        MIN({timestamp_column}) as earliest_record,
        COUNT(*) as total_records,
        COUNT(*) FILTER (WHERE {timestamp_column} > NOW() - INTERVAL '1 hour') as records_last_hour,
        COUNT(*) FILTER (WHERE {timestamp_column} > NOW() - INTERVAL '1 day') as records_last_day
    FROM {table_name}
    """
    
    async with tacnode_client as client:
        result = await client.execute_query(query)
    
    if result["success"]:
        freshness_info = result["data"][0] if result["data"] else {}
        return json.dumps({
            "table_name": table_name,
            "freshness_info": freshness_info,
            "execution_time_ms": result["execution_time_ms"]
        }, indent=2)
    else:
        return json.dumps({
            "error": result["error"]
        })

@tool
async def tacnode_aggregation_query(table_name: str, group_by: str, 
                                  aggregate_column: str, 
                                  aggregate_function: str = "COUNT") -> str:
    """
    Perform aggregation queries on Tacnode Context Lake data.
    
    Args:
        table_name: Name of the table to query
        group_by: Column to group by
        aggregate_column: Column to aggregate (use '*' for COUNT)
        aggregate_function: Aggregation function (COUNT, SUM, AVG, MAX, MIN)
        
    Returns:
        JSON string containing aggregation results
    """
    # Validate aggregate function
    valid_functions = ["COUNT", "SUM", "AVG", "MAX", "MIN"]
    if aggregate_function.upper() not in valid_functions:
        return json.dumps({
            "error": f"Invalid aggregate function. Must be one of: {valid_functions}"
        })
    
    if aggregate_function.upper() == "COUNT" and aggregate_column != "*":
        aggregate_expr = f"COUNT({aggregate_column})"
    else:
        aggregate_expr = f"{aggregate_function.upper()}({aggregate_column})"
    
    query = f"""
    SELECT 
        {group_by},
        {aggregate_expr} as {aggregate_function.lower()}_value
    FROM {table_name}
    GROUP BY {group_by}
    ORDER BY {aggregate_expr} DESC
    LIMIT 100
    """
    
    async with tacnode_client as client:
        result = await client.execute_query(query)
    
    if result["success"]:
        return json.dumps({
            "table_name": table_name,
            "group_by": group_by,
            "aggregate_function": aggregate_function,
            "results": result["data"],
            "execution_time_ms": result["execution_time_ms"]
        }, indent=2)
    else:
        return json.dumps({
            "error": result["error"]
        })

# Export all tools for easy import
__all__ = [
    "tacnode_query",
    "tacnode_vector_search", 
    "tacnode_schema_info",
    "tacnode_real_time_stats",
    "tacnode_data_freshness",
    "tacnode_aggregation_query"
]

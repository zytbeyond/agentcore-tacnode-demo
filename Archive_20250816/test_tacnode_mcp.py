#!/usr/bin/env python3
"""
Test script to query TACNode Context Lake via MCP server
"""
import json
import requests
import os
import sys

def test_tacnode_mcp():
    """Test TACNode MCP server connectivity and data access"""
    
    # Get token from environment
    token = os.getenv('TACNODE_TOKEN')
    if not token:
        print("❌ TACNODE_TOKEN environment variable not set")
        return False
    
    # MCP server endpoint
    url = "https://mcp-server.tacnode.io/mcp"
    
    # Headers
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream',
        'Authorization': f'Bearer {token}'
    }
    
    print("🔍 Testing TACNode Context Lake MCP Server...")
    print(f"📡 Endpoint: {url}")
    
    # Test 1: Initialize connection
    print("\n1️⃣ Testing MCP initialization...")
    init_payload = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "clientInfo": {"name": "tacnode-test", "version": "1.0.0"},
            "capabilities": {"roots": {"listChanged": True}, "sampling": {}}
        },
        "id": 1
    }
    
    try:
        response = requests.post(url, headers=headers, json=init_payload, timeout=10)
        print(f"✅ Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ MCP initialization successful")
        else:
            print(f"❌ Initialization failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False
    
    # Test 2: List available tools
    print("\n2️⃣ Listing available tools...")
    tools_payload = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "params": {},
        "id": 2
    }
    
    try:
        response = requests.post(url, headers=headers, json=tools_payload, timeout=10)
        if response.status_code == 200:
            print("✅ Tools list retrieved")
            # Parse SSE response
            lines = response.text.strip().split('\n')
            for line in lines:
                if line.startswith('data: '):
                    data = json.loads(line[6:])  # Remove 'data: ' prefix
                    if 'result' in data and 'tools' in data['result']:
                        tools = data['result']['tools']
                        print(f"📋 Available tools: {len(tools)}")
                        for tool in tools:
                            print(f"   - {tool['name']}: {tool['description']}")
        else:
            print(f"❌ Tools list failed: {response.text}")
    except Exception as e:
        print(f"❌ Tools list error: {e}")
    
    # Test 3: Query database info
    print("\n3️⃣ Testing database connection...")
    query_payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "query",
            "arguments": {
                "sql": "SELECT current_database(), current_user, version();"
            }
        },
        "id": 3
    }
    
    try:
        response = requests.post(url, headers=headers, json=query_payload, timeout=15)
        if response.status_code == 200:
            print("✅ Database query successful")
            # Parse SSE response
            lines = response.text.strip().split('\n')
            for line in lines:
                if line.startswith('data: '):
                    data = json.loads(line[6:])
                    if 'result' in data:
                        result = data['result']
                        print(f"📊 Query result: {result}")
        else:
            print(f"❌ Database query failed: {response.text}")
    except Exception as e:
        print(f"❌ Database query error: {e}")
    
    # Test 4: Check for test table data
    print("\n4️⃣ Checking for available data...")
    tables_payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "query",
            "arguments": {
                "sql": "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
            }
        },
        "id": 4
    }
    
    try:
        response = requests.post(url, headers=headers, json=tables_payload, timeout=15)
        if response.status_code == 200:
            print("✅ Tables query successful")
            # Parse SSE response
            lines = response.text.strip().split('\n')
            for line in lines:
                if line.startswith('data: '):
                    data = json.loads(line[6:])
                    if 'result' in data:
                        result = data['result']
                        print(f"📋 Available tables: {result}")
        else:
            print(f"❌ Tables query failed: {response.text}")
    except Exception as e:
        print(f"❌ Tables query error: {e}")
    
    return True

if __name__ == "__main__":
    success = test_tacnode_mcp()
    sys.exit(0 if success else 1)

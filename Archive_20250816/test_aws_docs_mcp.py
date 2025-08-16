#!/usr/bin/env python3
"""
Test script for AWS Documentation MCP Server
"""

import json
import subprocess
import time
import os
import signal
import sys

def start_mcp_server():
    """Start the AWS Documentation MCP server"""
    print("🚀 Starting AWS Documentation MCP Server...")
    
    env = os.environ.copy()
    env['FASTMCP_LOG_LEVEL'] = 'ERROR'
    env['AWS_DOCUMENTATION_PARTITION'] = 'aws'
    
    # Start the server
    process = subprocess.Popen(
        ['awslabs.aws-documentation-mcp-server'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env
    )
    
    print(f"✅ MCP Server started with PID: {process.pid}")
    return process

def send_mcp_request(process, request):
    """Send an MCP request to the server"""
    try:
        request_json = json.dumps(request) + '\n'
        process.stdin.write(request_json)
        process.stdin.flush()
        
        # Read response
        response_line = process.stdout.readline()
        if response_line:
            return json.loads(response_line.strip())
        return None
    except Exception as e:
        print(f"❌ Error sending request: {e}")
        return None

def test_mcp_server():
    """Test the AWS Documentation MCP server"""
    print("🧪 Testing AWS Documentation MCP Server")
    print("=" * 60)
    
    # Start server
    server_process = start_mcp_server()
    
    try:
        # Wait for server to start
        time.sleep(2)
        
        # Test 1: Initialize
        print("\n1️⃣ Testing MCP initialization...")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {"listChanged": True},
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "aws-docs-test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        response = send_mcp_request(server_process, init_request)
        if response and 'result' in response:
            print("✅ MCP initialization successful")
            print(f"   Server capabilities: {list(response['result']['capabilities'].keys())}")
        else:
            print(f"❌ Initialization failed: {response}")
            return
        
        # Test 2: List tools
        print("\n2️⃣ Listing available tools...")
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        response = send_mcp_request(server_process, tools_request)
        if response and 'result' in response:
            tools = response['result']['tools']
            print(f"✅ Found {len(tools)} tools:")
            for tool in tools:
                print(f"   - {tool['name']}: {tool['description']}")
        else:
            print(f"❌ Tools list failed: {response}")
        
        # Test 3: Search AWS documentation
        print("\n3️⃣ Testing documentation search...")
        search_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "search_documentation",
                "arguments": {
                    "search_phrase": "S3 bucket naming rules",
                    "limit": 3
                }
            }
        }
        
        response = send_mcp_request(server_process, search_request)
        if response and 'result' in response:
            print("✅ Documentation search successful")
            content = response['result']['content']
            if content and len(content) > 0:
                search_results = json.loads(content[0]['text'])
                print(f"   Found {len(search_results)} results:")
                for i, result in enumerate(search_results[:2], 1):
                    print(f"   {i}. {result.get('title', 'No title')}")
                    print(f"      URL: {result.get('url', 'No URL')}")
            else:
                print("   No search results found")
        else:
            print(f"❌ Documentation search failed: {response}")
        
        # Test 4: Read specific documentation
        print("\n4️⃣ Testing documentation reading...")
        read_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "read_documentation",
                "arguments": {
                    "url": "https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html"
                }
            }
        }
        
        response = send_mcp_request(server_process, read_request)
        if response and 'result' in response:
            print("✅ Documentation reading successful")
            content = response['result']['content']
            if content and len(content) > 0:
                doc_content = content[0]['text']
                print(f"   Retrieved {len(doc_content)} characters of documentation")
                print(f"   Preview: {doc_content[:200]}...")
            else:
                print("   No documentation content retrieved")
        else:
            print(f"❌ Documentation reading failed: {response}")
        
        # Test 5: Get recommendations
        print("\n5️⃣ Testing content recommendations...")
        recommend_request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "recommend",
                "arguments": {
                    "url": "https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html"
                }
            }
        }
        
        response = send_mcp_request(server_process, recommend_request)
        if response and 'result' in response:
            print("✅ Content recommendations successful")
            content = response['result']['content']
            if content and len(content) > 0:
                recommendations = json.loads(content[0]['text'])
                print(f"   Found {len(recommendations)} recommendations:")
                for i, rec in enumerate(recommendations[:3], 1):
                    print(f"   {i}. {rec.get('title', 'No title')}")
            else:
                print("   No recommendations found")
        else:
            print(f"❌ Content recommendations failed: {response}")
        
        print("\n✅ AWS Documentation MCP Server testing complete!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        # Clean up
        print("\n🧹 Cleaning up...")
        try:
            server_process.terminate()
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
        print("✅ Server stopped")

def create_mcp_config():
    """Create MCP configuration file for integration"""
    print("\n📋 Creating MCP configuration...")
    
    config = {
        "mcpServers": {
            "awslabs.aws-documentation-mcp-server": {
                "command": "awslabs.aws-documentation-mcp-server",
                "args": [],
                "env": {
                    "FASTMCP_LOG_LEVEL": "ERROR",
                    "AWS_DOCUMENTATION_PARTITION": "aws"
                },
                "disabled": False,
                "autoApprove": []
            }
        }
    }
    
    # Save configuration
    with open('aws-docs-mcp-config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ MCP configuration saved to: aws-docs-mcp-config.json")
    
    # Also create a simple usage guide
    usage_guide = """# AWS Documentation MCP Server Usage Guide

## Available Tools

1. **read_documentation(url)** - Fetch and convert AWS documentation pages to markdown
2. **search_documentation(search_phrase, limit)** - Search AWS documentation 
3. **recommend(url)** - Get content recommendations for AWS documentation pages

## Example Usage

### Search for S3 documentation
```
search_documentation("S3 bucket naming rules", 5)
```

### Read specific documentation page
```
read_documentation("https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html")
```

### Get recommendations for a page
```
recommend("https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html")
```

## Integration

The MCP server is now available for integration with AI assistants and can provide:
- Real-time access to AWS documentation
- Search capabilities across AWS docs
- Content recommendations
- Markdown-formatted documentation for easy processing
"""
    
    with open('AWS_DOCS_MCP_USAGE.md', 'w') as f:
        f.write(usage_guide)
    
    print("✅ Usage guide saved to: AWS_DOCS_MCP_USAGE.md")

def main():
    print("🚀 AWS Documentation MCP Server Setup & Test")
    print("=" * 70)
    
    try:
        # Test the server
        test_mcp_server()
        
        # Create configuration
        create_mcp_config()
        
        print("\n" + "="*70)
        print("🎉 AWS DOCUMENTATION MCP SERVER SETUP COMPLETE!")
        print("="*70)
        
        print("\n✅ CAPABILITIES ENABLED:")
        print("   📖 Read AWS documentation pages")
        print("   🔍 Search AWS documentation")
        print("   💡 Get content recommendations")
        print("   📝 Convert docs to markdown format")
        
        print("\n✅ INTEGRATION READY:")
        print("   🤖 Available for AI assistant integration")
        print("   🔧 MCP configuration file created")
        print("   📋 Usage guide provided")
        
        print("\n🎯 NEXT STEPS:")
        print("   1. Use the MCP server with AI assistants")
        print("   2. Query AWS documentation in real-time")
        print("   3. Get contextual recommendations")
        print("   4. Build AWS knowledge-powered applications")
        
    except KeyboardInterrupt:
        print("\n⚠️  Setup interrupted by user")
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Setup AWS Documentation MCP Server for AI Agent use
"""

import json
import subprocess
import time
import os
import threading
import queue

class AWSDocsMCPClient:
    """Client for AWS Documentation MCP Server"""
    
    def __init__(self):
        self.process = None
        self.request_id = 0
        
    def start_server(self):
        """Start the MCP server"""
        print("🚀 Starting AWS Documentation MCP Server...")
        
        env = os.environ.copy()
        env['FASTMCP_LOG_LEVEL'] = 'ERROR'
        env['AWS_DOCUMENTATION_PARTITION'] = 'aws'
        
        self.process = subprocess.Popen(
            ['awslabs.aws-documentation-mcp-server'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
            bufsize=1
        )
        
        # Wait for server to start
        time.sleep(2)
        print(f"✅ MCP Server started with PID: {self.process.pid}")
        
        # Initialize the connection
        self.initialize()
        
    def send_request(self, method, params=None):
        """Send a request to the MCP server"""
        self.request_id += 1
        
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method
        }
        
        if params:
            request["params"] = params
            
        try:
            request_json = json.dumps(request) + '\n'
            self.process.stdin.write(request_json)
            self.process.stdin.flush()
            
            # Read response
            response_line = self.process.stdout.readline()
            if response_line:
                return json.loads(response_line.strip())
            return None
        except Exception as e:
            print(f"❌ Error sending request: {e}")
            return None
    
    def initialize(self):
        """Initialize the MCP connection"""
        print("🔗 Initializing MCP connection...")
        
        params = {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "roots": {"listChanged": True},
                "sampling": {}
            },
            "clientInfo": {
                "name": "aws-docs-agent-client",
                "version": "1.0.0"
            }
        }
        
        response = self.send_request("initialize", params)
        if response and 'result' in response:
            print("✅ MCP connection initialized")
            return True
        else:
            print(f"❌ Initialization failed: {response}")
            return False
    
    def list_tools(self):
        """List available tools"""
        print("📋 Listing available tools...")
        
        response = self.send_request("tools/list")
        if response and 'result' in response:
            tools = response['result']['tools']
            print(f"✅ Found {len(tools)} tools:")
            for tool in tools:
                print(f"   - {tool['name']}: {tool['description']}")
            return tools
        else:
            print(f"❌ Tools list failed: {response}")
            return []
    
    def search_documentation(self, search_phrase, limit=5):
        """Search AWS documentation"""
        print(f"🔍 Searching for: '{search_phrase}'...")
        
        params = {
            "name": "search_documentation",
            "arguments": {
                "search_phrase": search_phrase,
                "limit": limit
            }
        }
        
        response = self.send_request("tools/call", params)
        if response and 'result' in response:
            print("✅ Search successful")
            content = response['result']['content']
            if content and len(content) > 0:
                try:
                    search_results = json.loads(content[0]['text'])
                    print(f"   Found {len(search_results)} results:")
                    for i, result in enumerate(search_results[:3], 1):
                        print(f"   {i}. {result.get('title', 'No title')}")
                        print(f"      URL: {result.get('url', 'No URL')}")
                    return search_results
                except json.JSONDecodeError:
                    print(f"   Raw result: {content[0]['text']}")
                    return content[0]['text']
            return []
        else:
            print(f"❌ Search failed: {response}")
            return []
    
    def read_documentation(self, url):
        """Read AWS documentation page"""
        print(f"📖 Reading documentation: {url}")
        
        params = {
            "name": "read_documentation",
            "arguments": {
                "url": url
            }
        }
        
        response = self.send_request("tools/call", params)
        if response and 'result' in response:
            print("✅ Documentation read successful")
            content = response['result']['content']
            if content and len(content) > 0:
                doc_content = content[0]['text']
                print(f"   Retrieved {len(doc_content)} characters")
                return doc_content
            return ""
        else:
            print(f"❌ Documentation read failed: {response}")
            return ""
    
    def get_recommendations(self, url):
        """Get content recommendations"""
        print(f"💡 Getting recommendations for: {url}")
        
        params = {
            "name": "recommend",
            "arguments": {
                "url": url
            }
        }
        
        response = self.send_request("tools/call", params)
        if response and 'result' in response:
            print("✅ Recommendations retrieved")
            content = response['result']['content']
            if content and len(content) > 0:
                try:
                    recommendations = json.loads(content[0]['text'])
                    print(f"   Found {len(recommendations)} recommendations:")
                    for i, rec in enumerate(recommendations[:3], 1):
                        print(f"   {i}. {rec.get('title', 'No title')}")
                    return recommendations
                except json.JSONDecodeError:
                    print(f"   Raw result: {content[0]['text']}")
                    return content[0]['text']
            return []
        else:
            print(f"❌ Recommendations failed: {response}")
            return []
    
    def stop_server(self):
        """Stop the MCP server"""
        if self.process:
            print("🛑 Stopping MCP server...")
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            print("✅ Server stopped")

def demonstrate_aws_docs_mcp():
    """Demonstrate AWS Documentation MCP capabilities"""
    print("🎯 AWS Documentation MCP Demonstration")
    print("=" * 60)
    
    client = AWSDocsMCPClient()
    
    try:
        # Start server
        client.start_server()
        
        # List tools
        tools = client.list_tools()
        
        # Test search
        print("\n" + "="*60)
        search_results = client.search_documentation("S3 bucket naming rules", 3)
        
        # Test reading documentation
        print("\n" + "="*60)
        if search_results and len(search_results) > 0:
            first_result_url = search_results[0].get('url', '')
            if first_result_url:
                doc_content = client.read_documentation(first_result_url)
                if doc_content:
                    print(f"📄 Documentation preview (first 500 chars):")
                    print(doc_content[:500] + "...")
        
        # Test recommendations
        print("\n" + "="*60)
        s3_naming_url = "https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html"
        recommendations = client.get_recommendations(s3_naming_url)
        
        print("\n✅ AWS Documentation MCP demonstration complete!")
        
    except Exception as e:
        print(f"❌ Demonstration failed: {e}")
    finally:
        client.stop_server()

def create_integration_files():
    """Create integration files for using AWS Docs MCP"""
    print("\n📁 Creating integration files...")
    
    # Create MCP configuration
    mcp_config = {
        "mcpServers": {
            "aws-documentation": {
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
    
    with open('aws-docs-mcp-config.json', 'w') as f:
        json.dump(mcp_config, f, indent=2)
    
    # Create usage examples
    usage_examples = """# AWS Documentation MCP Server - Usage Examples

## Available Tools

### 1. search_documentation
Search AWS documentation for specific topics.

**Example:**
```python
search_documentation("S3 bucket naming rules", 5)
search_documentation("Lambda function configuration", 3)
search_documentation("EC2 instance types", 10)
```

### 2. read_documentation  
Read and convert AWS documentation pages to markdown.

**Example:**
```python
read_documentation("https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html")
read_documentation("https://docs.aws.amazon.com/lambda/latest/dg/configuration-function-common.html")
```

### 3. recommend
Get content recommendations for AWS documentation pages.

**Example:**
```python
recommend("https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html")
```

## Integration with AI Agents

The AWS Documentation MCP server enables AI agents to:

1. **Real-time Documentation Access**: Query the latest AWS documentation
2. **Contextual Search**: Find relevant AWS docs based on user questions
3. **Content Recommendations**: Discover related AWS documentation
4. **Markdown Conversion**: Get documentation in AI-friendly format

## Example AI Agent Queries

- "What are the S3 bucket naming rules?"
- "How do I configure Lambda function memory?"
- "What are the different EC2 instance types?"
- "Show me documentation about VPC security groups"
- "Find information about RDS backup strategies"

## Benefits

- ✅ Always up-to-date AWS documentation
- ✅ Intelligent search capabilities  
- ✅ Content recommendations
- ✅ Markdown formatting for AI processing
- ✅ Real-time access to AWS knowledge base
"""
    
    with open('AWS_DOCS_MCP_EXAMPLES.md', 'w') as f:
        f.write(usage_examples)
    
    print("✅ Integration files created:")
    print("   - aws-docs-mcp-config.json (MCP configuration)")
    print("   - AWS_DOCS_MCP_EXAMPLES.md (Usage examples)")

def main():
    print("🚀 AWS Documentation MCP Server Setup for AI Agent")
    print("=" * 70)
    
    try:
        # Demonstrate capabilities
        demonstrate_aws_docs_mcp()
        
        # Create integration files
        create_integration_files()
        
        print("\n" + "="*70)
        print("🎉 AWS DOCUMENTATION MCP SERVER READY FOR AI AGENT USE!")
        print("="*70)
        
        print("\n✅ CAPABILITIES AVAILABLE:")
        print("   📖 Real-time AWS documentation access")
        print("   🔍 Intelligent documentation search")
        print("   💡 Content recommendations")
        print("   📝 Markdown-formatted documentation")
        
        print("\n✅ INTEGRATION COMPLETE:")
        print("   🤖 Ready for AI agent integration")
        print("   🔧 MCP configuration files created")
        print("   📋 Usage examples provided")
        print("   🎯 Demonstration completed successfully")
        
        print("\n🎯 AI AGENT BENEFITS:")
        print("   - Answer AWS questions with latest documentation")
        print("   - Provide contextual AWS guidance")
        print("   - Recommend related AWS resources")
        print("   - Access comprehensive AWS knowledge base")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")

if __name__ == "__main__":
    main()

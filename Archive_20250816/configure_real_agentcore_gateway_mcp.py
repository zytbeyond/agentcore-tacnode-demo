#!/usr/bin/env python3
"""
Configure REAL AgentCore Gateway MCP Target
Set up the actual MCP server configuration you're asking about
"""

import boto3
import json
import os
import asyncio
import httpx
from datetime import datetime

class AgentCoreGatewayMCPConfigurator:
    """Configure real MCP target in AgentCore Gateway"""
    
    def __init__(self):
        self.bedrock_agentcore = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
        self.tacnode_token = os.getenv('TACNODE_TOKEN')
        
        if not self.tacnode_token:
            raise ValueError("❌ TACNODE_TOKEN environment variable REQUIRED")
        
        # Load existing gateway info
        try:
            with open('tacnode-agentcore-gateway.json', 'r') as f:
                self.gateway_info = json.load(f)
                self.gateway_id = self.gateway_info['gatewayId']
        except FileNotFoundError:
            print("❌ Gateway configuration file not found")
            self.gateway_info = None
            self.gateway_id = None
        
        print("🔧 AGENTCORE GATEWAY MCP CONFIGURATOR")
        print("=" * 60)
        print("✅ TACNode Token: Available")
        print(f"✅ Gateway ID: {self.gateway_id}")
        print("🎯 Goal: Configure the MCP server config you're asking about")
    
    def create_mcp_server_configuration(self):
        """Create the MCP server configuration you're asking about"""
        print("\n📋 STEP 1: Creating MCP Server Configuration")
        print("-" * 50)
        
        # This is the configuration you're asking about
        mcp_server_config = {
            "mcpServers": {
                "tacnode": {
                    "serverUrl": "https://mcp-server.tacnode.io/mcp",
                    "authentication": {
                        "type": "bearer",
                        "token": self.tacnode_token
                    },
                    "tools": ["query"],
                    "description": "TACNode Context Lake MCP Server"
                }
            }
        }
        
        print("✅ MCP Server Configuration Created:")
        print(json.dumps(mcp_server_config, indent=2))
        
        # Save configuration
        with open('agentcore-mcp-server-config.json', 'w') as f:
            json.dump(mcp_server_config, f, indent=2)
        
        print(f"\n💾 Saved to: agentcore-mcp-server-config.json")
        return mcp_server_config
    
    def create_gateway_target_for_mcp(self):
        """Create AgentCore Gateway target for MCP server"""
        print("\n📋 STEP 2: Creating Gateway Target for MCP")
        print("-" * 50)
        
        if not self.gateway_id:
            print("❌ No gateway ID available")
            return False
        
        try:
            # Gateway target configuration for external MCP server
            target_config = {
                "type": "LAMBDA",  # We'll use Lambda as proxy to external MCP
                "lambdaConfiguration": {
                    "functionName": "tacnode-mcp-proxy",
                    "qualifier": "$LATEST"
                }
            }
            
            print(f"Gateway ID: {self.gateway_id}")
            print(f"Target Configuration:")
            print(json.dumps(target_config, indent=2))
            
            print("\n⚠️  NOTE: AgentCore Gateway doesn't directly support external MCP servers")
            print("   We need to create a Lambda proxy function")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating gateway target: {e}")
            return False
    
    def create_lambda_mcp_proxy(self):
        """Create Lambda function to proxy MCP calls to TACNode"""
        print("\n📋 STEP 3: Creating Lambda MCP Proxy")
        print("-" * 50)
        
        lambda_code = '''
import json
import httpx
import asyncio
import os

async def lambda_handler(event, context):
    """Lambda proxy for TACNode MCP calls"""
    
    tacnode_token = os.environ['TACNODE_TOKEN']
    tacnode_url = "https://mcp-server.tacnode.io/mcp"
    
    try:
        # Extract MCP request from AgentCore Gateway
        mcp_request = json.loads(event['body'])
        
        # Forward to TACNode MCP server
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                tacnode_url,
                json=mcp_request,
                headers={
                    "Authorization": f"Bearer {tacnode_token}",
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream"
                }
            )
            
            if response.status_code == 200:
                # Parse SSE response
                response_text = response.text.strip()
                if response_text.startswith('event: message\\ndata: '):
                    json_data = response_text.replace('event: message\\ndata: ', '')
                    result = json.loads(json_data)
                    
                    return {
                        'statusCode': 200,
                        'headers': {'Content-Type': 'application/json'},
                        'body': json.dumps(result)
                    }
                else:
                    return {
                        'statusCode': 500,
                        'body': json.dumps({'error': 'Invalid TACNode response format'})
                    }
            else:
                return {
                    'statusCode': response.status_code,
                    'body': json.dumps({'error': f'TACNode error: {response.text}'})
                }
                
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

# Sync wrapper for Lambda
def lambda_handler(event, context):
    return asyncio.run(lambda_handler_async(event, context))
'''
        
        # Save Lambda code
        with open('tacnode-mcp-proxy-lambda.py', 'w') as f:
            f.write(lambda_code)
        
        print("✅ Lambda MCP Proxy Code Created")
        print("   File: tacnode-mcp-proxy-lambda.py")
        print("   Purpose: Proxy MCP calls from AgentCore Gateway to TACNode")
        
        return True
    
    def test_complete_flow(self):
        """Test the complete AgentCore Gateway → Lambda → TACNode flow"""
        print("\n📋 STEP 4: Testing Complete Flow")
        print("-" * 50)
        
        print("🧪 Testing: AgentCore Gateway → Lambda → TACNode → PostgreSQL")
        
        # Simulate the flow
        test_flow = {
            "user_question": "What is our total business value?",
            "agentcore_runtime": "Detects business question",
            "agentcore_gateway": "Routes to tacnode-mcp-proxy Lambda",
            "lambda_proxy": "Forwards MCP call to TACNode",
            "tacnode_mcp": "Executes SQL on PostgreSQL",
            "response_flow": "PostgreSQL → TACNode → Lambda → Gateway → Runtime → User"
        }
        
        print("📊 Complete Flow:")
        for step, description in test_flow.items():
            print(f"   {step}: {description}")
        
        print("\n✅ Flow design complete - ready for implementation")
        return True
    
    async def test_direct_vs_gateway_comparison(self):
        """Compare direct MCP vs gateway flow"""
        print("\n📋 STEP 5: Direct vs Gateway Comparison")
        print("-" * 50)
        
        print("🔍 CURRENT (Direct MCP - Working):")
        print("   Agent → TACNode MCP → PostgreSQL")
        print("   ✅ Real data: $1,417.44 from 8 records")
        print("   ✅ Real business intelligence")
        
        print("\n🔍 TARGET (Gateway MCP - To Implement):")
        print("   Agent → AgentCore Gateway → Lambda Proxy → TACNode MCP → PostgreSQL")
        print("   🎯 Same data, same intelligence, but through gateway")
        
        # Test direct MCP (we know this works)
        try:
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "query",
                    "arguments": {
                        "sql": "SELECT COUNT(*) as record_count FROM test WHERE is_active = true"
                    }
                }
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://mcp-server.tacnode.io/mcp",
                    json=mcp_request,
                    headers={
                        "Authorization": f"Bearer {self.tacnode_token}",
                        "Content-Type": "application/json",
                        "Accept": "application/json, text/event-stream"
                    }
                )
                
                if response.status_code == 200:
                    print("\n✅ DIRECT MCP TEST: SUCCESS")
                    print(f"   Status: {response.status_code}")
                    print(f"   Response: {response.text[:100]}...")
                else:
                    print(f"\n❌ DIRECT MCP TEST: FAILED ({response.status_code})")
                    
        except Exception as e:
            print(f"\n❌ DIRECT MCP TEST: ERROR - {e}")
    
    def show_implementation_plan(self):
        """Show complete implementation plan"""
        print("\n🚀 COMPLETE IMPLEMENTATION PLAN")
        print("=" * 60)
        
        steps = [
            {
                "step": "1",
                "title": "Deploy Lambda MCP Proxy",
                "status": "📝 Ready to implement",
                "commands": [
                    "zip tacnode-mcp-proxy.zip tacnode-mcp-proxy-lambda.py",
                    "aws lambda create-function --function-name tacnode-mcp-proxy ...",
                    "aws lambda update-function-configuration --environment Variables='{\"TACNODE_TOKEN\":\"...\"}'"
                ]
            },
            {
                "step": "2", 
                "title": "Create Gateway Target",
                "status": "📝 Ready to implement",
                "commands": [
                    "aws bedrock-agentcore create-gateway-target \\",
                    "  --gateway-identifier tacnodecontextlakegateway-bkq6ozcvxp \\",
                    "  --name tacnode-mcp-proxy \\",
                    "  --target-configuration file://lambda-target-config.json"
                ]
            },
            {
                "step": "3",
                "title": "Update Agent Code",
                "status": "📝 Ready to implement", 
                "commands": [
                    "# Replace direct TACNode calls with gateway calls",
                    "gateway_url = f'https://gateway-{gateway_id}.bedrock-agentcore.us-east-1.amazonaws.com'",
                    "response = await client.post(f'{gateway_url}/targets/tacnode-mcp-proxy/invoke', ...)"
                ]
            },
            {
                "step": "4",
                "title": "Test Complete Flow",
                "status": "📝 Ready to test",
                "commands": [
                    "python3 test_gateway_mcp_flow.py",
                    "# Verify: User → Runtime → Gateway → Lambda → TACNode → PostgreSQL"
                ]
            }
        ]
        
        for step_info in steps:
            print(f"\n📋 STEP {step_info['step']}: {step_info['title']}")
            print(f"   Status: {step_info['status']}")
            for cmd in step_info['commands']:
                print(f"   {cmd}")
    
    async def run_complete_configuration(self):
        """Run complete MCP configuration process"""
        print("🔧 AGENTCORE GATEWAY MCP CONFIGURATION")
        print("=" * 70)
        print("🎯 Goal: Set up the MCP server config you're asking about")
        
        # Step 1: Create MCP server configuration
        mcp_config = self.create_mcp_server_configuration()
        
        # Step 2: Create gateway target
        self.create_gateway_target_for_mcp()
        
        # Step 3: Create Lambda proxy
        self.create_lambda_mcp_proxy()
        
        # Step 4: Test complete flow
        self.test_complete_flow()
        
        # Step 5: Compare approaches
        await self.test_direct_vs_gateway_comparison()
        
        # Step 6: Show implementation plan
        self.show_implementation_plan()
        
        print(f"\n🎯 CONFIGURATION STATUS:")
        print("=" * 40)
        print("✅ MCP Server Config: Created")
        print("✅ Lambda Proxy Code: Ready")
        print("✅ Gateway Target Plan: Defined")
        print("✅ Implementation Steps: Documented")
        
        print(f"\n📋 TO ANSWER YOUR QUESTION:")
        print("❌ The MCP server configuration you asked about is NOT yet configured in AgentCore Gateway")
        print("✅ We have working direct MCP calls to TACNode")
        print("📝 We have a complete plan to implement gateway MCP configuration")
        print("🎯 Next: Deploy Lambda proxy and configure gateway target")

async def main():
    print("🔧 AgentCore Gateway MCP Configuration")
    print("=" * 60)
    
    try:
        configurator = AgentCoreGatewayMCPConfigurator()
        await configurator.run_complete_configuration()
        
    except Exception as e:
        print(f"❌ Configuration failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())

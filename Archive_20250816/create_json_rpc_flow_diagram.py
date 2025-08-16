#!/usr/bin/env python3
"""
Create JSON-RPC Flow Diagram
Visualize the exact JSON-RPC API calls and data transfers
"""

import json
from datetime import datetime

class JSONRPCFlowAnalyzer:
    """Analyze and document JSON-RPC flow in detail"""
    
    def __init__(self):
        self.flow_steps = []
    
    def show_complete_json_rpc_flow(self):
        """Show complete JSON-RPC flow with actual payloads"""
        print("🔍 COMPLETE JSON-RPC API FLOW ANALYSIS")
        print("=" * 80)
        
        # Step 1: User to AgentCore Runtime
        print("\n📋 STEP 1: USER → AGENTCORE RUNTIME")
        print("-" * 50)
        print("Protocol: HTTP POST")
        print("Endpoint: /invocations")
        
        user_payload = {
            "input": {
                "prompt": "What is our total business value and which category is performing best?"
            }
        }
        print("User Payload:")
        print(json.dumps(user_payload, indent=2))
        
        # Step 2: AgentCore Runtime processes and decides
        print("\n📋 STEP 2: AGENTCORE RUNTIME PROCESSING")
        print("-" * 50)
        print("Location: Docker container in AgentCore Runtime")
        print("Agent: business-intelligence-agent")
        print("Decision Logic:")
        print("  business_keywords = ['business', 'value', 'category', 'performance']")
        print("  needs_data = True (keywords found)")
        print("  → Agent will call AgentCore Gateway")
        
        # Step 3: Runtime to Gateway JSON-RPC
        print("\n📋 STEP 3: AGENTCORE RUNTIME → AGENTCORE GATEWAY")
        print("-" * 50)
        print("WHO GENERATES: Docker container (Python agent code)")
        print("Protocol: JSON-RPC 2.0 over HTTP")
        print("Endpoint: AgentCore Gateway MCP endpoint")
        
        runtime_to_gateway = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "get_business_data",
                "arguments": {
                    "query_type": "business_summary",
                    "context": "total business value and category performance"
                }
            }
        }
        print("JSON-RPC Request:")
        print(json.dumps(runtime_to_gateway, indent=2))
        
        # Step 4: Gateway to TACNode JSON-RPC
        print("\n📋 STEP 4: AGENTCORE GATEWAY → TACNODE MCP")
        print("-" * 50)
        print("WHO GENERATES: AgentCore Gateway (AWS managed service)")
        print("Protocol: JSON-RPC 2.0 over HTTPS")
        print("Endpoint: https://mcp-server.tacnode.io/mcp")
        print("Authentication: Bearer token")
        print("Source IP: AWS us-east-1 range (whitelisted)")
        
        gateway_to_tacnode = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "execute_sql",
                "arguments": {
                    "query": "SELECT id, name, description, value, category, created_date, is_active FROM test WHERE is_active = true ORDER BY created_date DESC"
                }
            }
        }
        print("JSON-RPC Request:")
        print(json.dumps(gateway_to_tacnode, indent=2))
        
        # Step 5: TACNode to PostgreSQL
        print("\n📋 STEP 5: TACNODE MCP → POSTGRESQL")
        print("-" * 50)
        print("WHO EXECUTES: TACNode MCP Server")
        print("Protocol: PostgreSQL wire protocol")
        print("Database: PostgreSQL")
        
        sql_query = """SELECT 
    id, 
    name, 
    description, 
    value, 
    category, 
    created_date, 
    is_active 
FROM test 
WHERE is_active = true 
ORDER BY created_date DESC;"""
        
        print("SQL Query:")
        print(sql_query)
        
        # Step 6: PostgreSQL Results
        print("\n📋 STEP 6: POSTGRESQL RESULTS")
        print("-" * 50)
        
        sample_results = [
            {"id": 1, "name": "Sample A", "description": "First test record", "value": "123.45", "category": "Category 1", "created_date": "2025-07-20", "is_active": True},
            {"id": 2, "name": "Sample B", "description": "Second test record", "value": "456.78", "category": "Category 2", "created_date": "2025-07-21", "is_active": True},
            {"id": 10, "name": "Sample J", "description": "Latest record", "value": "111.11", "category": "Category 1", "created_date": "2025-08-04", "is_active": True}
        ]
        
        print("Sample Database Results (10 records total):")
        for record in sample_results:
            print(f"  ID {record['id']}: {record['name']} = ${record['value']} ({record['category']})")
        print("  ... (7 more records)")
        
        # Step 7: TACNode JSON-RPC Response
        print("\n📋 STEP 7: TACNODE → AGENTCORE GATEWAY")
        print("-" * 50)
        print("Protocol: JSON-RPC 2.0 Response")
        
        tacnode_response = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(sample_results)
                    }
                ]
            }
        }
        print("JSON-RPC Response:")
        print(json.dumps(tacnode_response, indent=2))
        
        # Step 8: Gateway to Runtime
        print("\n📋 STEP 8: AGENTCORE GATEWAY → AGENTCORE RUNTIME")
        print("-" * 50)
        print("Protocol: JSON-RPC 2.0 Response")
        print("Same payload as received from TACNode")
        
        # Step 9: Runtime Processing
        print("\n📋 STEP 9: AGENTCORE RUNTIME PROCESSING")
        print("-" * 50)
        print("Location: Docker container")
        print("Processing:")
        
        processing_code = """
# Agent receives JSON-RPC response
response_data = json.loads(response_text)
business_records = json.loads(response_data['result']['content'][0]['text'])

# Calculate business metrics
total_value = sum(float(record['value']) for record in business_records)
# Result: $1,417.44

categories = {}
for record in business_records:
    category = record['category']
    if category not in categories:
        categories[category] = {'count': 0, 'total': 0}
    categories[category]['count'] += 1
    categories[category]['total'] += float(record['value'])

# Find top performing category
top_category = max(categories.items(), key=lambda x: x[1]['total'])
# Result: Category 3 with $989.24
"""
        print(processing_code)
        
        # Step 10: Claude AI Analysis
        print("\n📋 STEP 10: CLAUDE AI ANALYSIS")
        print("-" * 50)
        print("Service: AWS Bedrock (Claude 3.5 Sonnet)")
        print("Input: User question + Business data")
        
        claude_prompt = f"""User Question: {user_payload['input']['prompt']}

Real-time Business Data:
{json.dumps(sample_results, indent=2)}

Provide comprehensive business intelligence analysis."""
        
        print("Claude Prompt (truncated):")
        print(claude_prompt[:200] + "...")
        
        # Step 11: Final Response
        print("\n📋 STEP 11: FINAL RESPONSE TO USER")
        print("-" * 50)
        
        final_response = {
            "output": {
                "message": "Based on real-time business data, your total business value is $1,417.44 across 10 active records. Category 3 is your top performer with $989.24 total value...",
                "timestamp": datetime.now().isoformat(),
                "model": "business-intelligence-agent",
                "data_accessed": True,
                "gateway_used": True,
                "records_analyzed": 10
            }
        }
        
        print("Final Response:")
        print(json.dumps(final_response, indent=2))
    
    def show_json_rpc_summary_table(self):
        """Show summary table of all JSON-RPC transfers"""
        print("\n📊 JSON-RPC TRANSFER SUMMARY TABLE")
        print("=" * 100)
        
        transfers = [
            {
                "Step": "1",
                "From": "User",
                "To": "AgentCore Runtime",
                "Protocol": "HTTP",
                "Generator": "User Interface",
                "Content": "Business question",
                "Data Type": "JSON"
            },
            {
                "Step": "2",
                "From": "Runtime Container",
                "To": "AgentCore Gateway",
                "Protocol": "JSON-RPC 2.0",
                "Generator": "Docker Container (Python Agent)",
                "Content": "tools/call → get_business_data",
                "Data Type": "MCP Request"
            },
            {
                "Step": "3",
                "From": "AgentCore Gateway",
                "To": "TACNode MCP",
                "Protocol": "JSON-RPC 2.0",
                "Generator": "AgentCore Gateway (AWS)",
                "Content": "tools/call → execute_sql",
                "Data Type": "SQL Request"
            },
            {
                "Step": "4",
                "From": "TACNode MCP",
                "To": "PostgreSQL",
                "Protocol": "SQL",
                "Generator": "TACNode MCP Server",
                "Content": "SELECT query",
                "Data Type": "SQL Command"
            },
            {
                "Step": "5",
                "From": "PostgreSQL",
                "To": "TACNode MCP",
                "Protocol": "SQL",
                "Generator": "PostgreSQL Database",
                "Content": "10 business records",
                "Data Type": "Result Set"
            },
            {
                "Step": "6",
                "From": "TACNode MCP",
                "To": "AgentCore Gateway",
                "Protocol": "JSON-RPC 2.0",
                "Generator": "TACNode MCP Server",
                "Content": "JSON array of records",
                "Data Type": "MCP Response"
            },
            {
                "Step": "7",
                "From": "AgentCore Gateway",
                "To": "Runtime Container",
                "Protocol": "JSON-RPC 2.0",
                "Generator": "AgentCore Gateway (AWS)",
                "Content": "Same JSON data",
                "Data Type": "MCP Response"
            },
            {
                "Step": "8",
                "From": "Runtime Container",
                "To": "Claude AI",
                "Protocol": "HTTP",
                "Generator": "Docker Container (Python Agent)",
                "Content": "Business data + question",
                "Data Type": "AI Prompt"
            },
            {
                "Step": "9",
                "From": "Claude AI",
                "To": "Runtime Container",
                "Protocol": "HTTP",
                "Generator": "AWS Bedrock (Claude)",
                "Content": "Business intelligence",
                "Data Type": "AI Response"
            },
            {
                "Step": "10",
                "From": "Runtime Container",
                "To": "User",
                "Protocol": "HTTP",
                "Generator": "Docker Container (Python Agent)",
                "Content": "Final business report",
                "Data Type": "JSON"
            }
        ]
        
        # Print table header
        print(f"{'Step':<4} {'From':<18} {'To':<18} {'Protocol':<12} {'Generator':<25} {'Content':<25}")
        print("-" * 100)
        
        # Print table rows
        for transfer in transfers:
            print(f"{transfer['Step']:<4} {transfer['From']:<18} {transfer['To']:<18} {transfer['Protocol']:<12} {transfer['Generator']:<25} {transfer['Content']:<25}")
        
        print("=" * 100)
    
    def show_key_insights(self):
        """Show key insights about JSON-RPC usage"""
        print("\n🎯 KEY JSON-RPC INSIGHTS")
        print("=" * 60)
        
        print("\n✅ WHO GENERATES JSON-RPC:")
        print("  • Docker Container (Python Agent): Generates business data requests")
        print("  • AgentCore Gateway (AWS): Transforms requests for TACNode")
        print("  • TACNode MCP Server: Generates SQL execution responses")
        
        print("\n✅ JSON-RPC PROTOCOL USAGE:")
        print("  • Standard: JSON-RPC 2.0 (RFC 4627)")
        print("  • Transport: HTTP/HTTPS")
        print("  • Method: 'tools/call' (MCP standard)")
        print("  • Authentication: Bearer tokens")
        
        print("\n✅ DATA TRANSFORMATIONS:")
        print("  • User Question → Business Keywords → JSON-RPC MCP Call")
        print("  • MCP Call → SQL Query → Database Results")
        print("  • Database Results → JSON Array → Business Intelligence")
        
        print("\n✅ SECURITY LAYERS:")
        print("  • AgentCore Gateway: AWS managed authentication")
        print("  • TACNode Access: Bearer token + IP whitelist")
        print("  • HTTPS: Encrypted transport throughout")
        
        print("\n✅ ERROR HANDLING:")
        print("  • JSON-RPC standard error responses")
        print("  • SQL error handling by TACNode MCP")
        print("  • Network retry logic in agent")
        print("  • Graceful fallbacks for failed requests")
    
    def run_complete_analysis(self):
        """Run complete JSON-RPC flow analysis"""
        print("🔍 COMPLETE JSON-RPC API ANALYSIS")
        print("AgentCore Runtime → Gateway → TACNode Context Lake")
        print("=" * 80)
        
        # Show detailed flow
        self.show_complete_json_rpc_flow()
        
        # Show summary table
        self.show_json_rpc_summary_table()
        
        # Show key insights
        self.show_key_insights()
        
        print("\n🎉 JSON-RPC ANALYSIS COMPLETE!")
        print("=" * 80)
        print("This analysis shows how JSON-RPC serves as the backbone")
        print("for seamless communication between AgentCore and TACNode,")
        print("enabling real-time business intelligence with proper")
        print("security, error handling, and data transformation.")

def main():
    print("🔍 JSON-RPC API Flow Analysis")
    print("=" * 50)
    
    analyzer = JSONRPCFlowAnalyzer()
    analyzer.run_complete_analysis()

if __name__ == "__main__":
    main()

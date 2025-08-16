# 🚀 TACNode + AWS Bedrock AgentCore Integration Guide

## Overview
This guide shows how to integrate TACNode Context Lake with AWS Bedrock AgentCore Gateway, enabling AI agents to query real-time data.

## Architecture
```
Bedrock AgentCore Runtime → AgentCore Gateway → TACNode MCP Server → TACNode Context Lake
```

## ✅ Prerequisites Verified
- **AWS Account**: 560155322832
- **Region**: us-east-1 
- **Service**: Bedrock AgentCore available ✅
- **Service Role**: AmazonBedrockAgentCoreGatewayDefaultServiceRole1754124199105 ✅
- **TACNode Token**: TACNODE_TOKEN environment variable set ✅
- **TACNode MCP Server**: https://mcp-server.tacnode.io/mcp accessible ✅

## 🎯 Current Status
- **TACNode Connection**: ✅ Working (tested successfully)
- **AgentCore Gateway**: ❌ Needs to be created
- **Integration**: ⏳ Ready to configure once gateway exists

## 📊 Available Data in TACNode Context Lake
- **Database**: PostgreSQL 14.2 (TACNode Context Lake v1.2.3)
- **Table**: `test` with 10 business records
- **Data Types**: IDs, names, descriptions, timestamps, values, categories
- **Query Tool**: `query` - Execute read-only SQL queries
- **Response Format**: JSON with real-time results

## 🔧 Setup Options

### Option 1: Manual Setup (Recommended)
1. **Go to AWS Console**: https://console.aws.amazon.com/bedrock/
2. **Navigate**: Bedrock → AgentCore → Gateways
3. **Create Gateway**:
   - **Name**: `TACNodeContextLakeGateway`
   - **Description**: `Gateway for TACNode Context Lake real-time data access`
   - **Protocol Type**: `MCP`
   - **MCP Version**: `2025-03-26`
   - **Service Role**: `AmazonBedrockAgentCoreGatewayDefaultServiceRole1754124199105`
   - **Instructions**: `Gateway for connecting Bedrock AgentCore to TACNode Context Lake for real-time data analytics and AI-driven insights`

4. **Add Target**:
   - **Target Name**: `TACNodeContextLake`
   - **Target Type**: `MCP Server`
   - **Server URL**: `https://mcp-server.tacnode.io/mcp`
   - **Authentication**: `Bearer Token`
   - **Token**: `[Your TACNODE_TOKEN value]`
   - **Capabilities**: `query` (SQL query execution)

### Option 2: Programmatic Setup
```bash
# Try automated setup (may require additional permissions)
python3 setup_tacnode_agentcore_gateway.py
```

## 🧪 Testing the Integration

### 1. Verify TACNode Connection
```bash
python3 test_tacnode_mcp.py
```

### 2. Query Sample Data
```bash
python3 query_tacnode_data.py
```

### 3. Test Through AgentCore (Once Gateway is Created)
The AgentCore runtime can now execute queries like:
- "Show me all active records from the test table"
- "What are the top categories by total value?"
- "Find records created in the last 5 days"

## 💡 What This Enables

### For AI Agents
- **Real-time Data Access**: Query live business data instantly
- **Analytics Capabilities**: Perform aggregations, filtering, sorting
- **Business Intelligence**: Generate insights from structured data
- **Decision Making**: Data-driven recommendations and actions

### Example Agent Capabilities
```sql
-- High-value analysis
SELECT category, COUNT(*) as count, SUM(value) as total_value 
FROM test 
WHERE is_active = true AND value > 100 
GROUP BY category 
ORDER BY total_value DESC;

-- Recent activity trends
SELECT DATE(created_date) as date, AVG(value) as avg_value 
FROM test 
WHERE created_date > CURRENT_DATE - INTERVAL '7 days' 
GROUP BY DATE(created_date) 
ORDER BY date DESC;
```

## 🔐 Security Features
- **Bearer Token Authentication**: Secure access to TACNode MCP server
- **IAM Role-based Access**: AWS service role controls gateway permissions
- **Read-only Queries**: Safe data access without modification capabilities
- **HTTPS Transport**: Encrypted communication throughout the chain

## 📈 Performance Benefits
- **Sub-second Queries**: Real-time response from TACNode Context Lake
- **Scalable Architecture**: Handle multiple concurrent agent requests
- **Efficient Protocol**: MCP optimized for AI agent communication
- **JSON Results**: Structured data perfect for AI processing

## 🚀 Next Steps After Gateway Creation

1. **Create AgentCore Agents**: Build AI agents that use the gateway
2. **Configure Agent Tools**: Enable agents to use the `query` tool
3. **Test Business Scenarios**: Run real-world data analysis tasks
4. **Monitor Performance**: Track query performance and usage
5. **Scale Integration**: Add more data sources and capabilities

## 🛠️ Troubleshooting

### Common Issues
- **Gateway Creation Fails**: Check IAM permissions for bedrock-agentcore:CreateGateway
- **Target Addition Fails**: Verify TACNODE_TOKEN is valid and server is accessible
- **Query Failures**: Check SQL syntax and table permissions

### Support Resources
- **TACNode Support**: support@tacnode.io
- **AWS Documentation**: Bedrock AgentCore Gateway documentation
- **Test Scripts**: Use provided Python scripts for validation

## 📋 Summary
This integration connects AWS Bedrock AgentCore with TACNode Context Lake, enabling AI agents to:
- Query real-time business data
- Perform complex analytics
- Generate data-driven insights
- Make intelligent decisions based on live information

The setup provides a secure, scalable, and high-performance foundation for AI-powered business applications.

# 🚀 AgentCore + DynamoDB Integration

Complete setup for AWS Bedrock AgentCore with DynamoDB context store integration.

## 🎯 **What's Included**

### **Production-Ready Components**
- ✅ **DynamoDB Table**: `AgentCoreContextStore` (us-east-1)
- ✅ **Python Client Library**: Full-featured context management
- ✅ **Setup Scripts**: Automated table creation and configuration
- ✅ **Analysis Tools**: Status checking and testing utilities
- ✅ **Documentation**: Comprehensive guides and examples

### **Key Features**
- 💬 **Conversation Context**: Store and retrieve user-agent interactions
- 📚 **Knowledge Base**: Manage domain-specific information
- 👤 **User Preferences**: Handle personalization and settings
- 🔍 **Semantic Search**: Query by context type, session, or time
- 📊 **Optimized Schema**: Efficient data structure for agent workloads

## 📁 **File Structure**

### **Core Client Library**
- `agentcore_dynamodb_client.py` - Main client for context operations
- `setup_agentcore_dynamodb.py` - Automated DynamoDB setup
- `analyze_agentcore_dynamodb.py` - Analysis and testing tools

### **Gateway Creation**
- `create_agentcore_gateway.py` - Gateway creation (general)
- `create_agentcore_gateway_useast1.py` - us-east-1 specific setup
- `check_agentcore_status.py` - Service availability checker

### **Configuration Files**
- `agentcore-gateway-trust-policy.json` - IAM trust policy
- `agentcore-gateway-permissions.json` - IAM permissions
- `gateway-protocol-config.json` - MCP protocol configuration
- `gateway-authorizer-config.json` - JWT authorization config

### **Documentation**
- `US_EAST_1_SETUP_COMPLETE.md` - Complete setup guide
- `AGENTCORE_DYNAMODB_SUMMARY.md` - Integration summary
- `AGENTCORE_GATEWAY_SETUP.md` - Manual gateway setup

## 🚀 **Quick Start**

### **1. Test Current Setup**
```bash
# Check AgentCore service status
python3 check_agentcore_status.py

# Test DynamoDB integration
python3 agentcore_dynamodb_client.py

# Analyze current setup
python3 analyze_agentcore_dynamodb.py
```

### **2. Use the Client Library**
```python
from agentcore_dynamodb_client import AgentCoreDynamoDBClient

# Initialize client (uses us-east-1)
client = AgentCoreDynamoDBClient()

# Store conversation
client.store_conversation_context(
    session_id="user_123_session_456",
    user_message="How do I use AgentCore?",
    agent_response="AgentCore helps you build context-aware AI agents...",
    metadata={"topic": "agentcore", "intent": "help"}
)

# Retrieve history
history = client.get_conversation_history("user_123_session_456", limit=5)
```

## 🏗️ **Architecture**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Your Agent    │───▶│  AgentCore       │───▶│   DynamoDB      │
│   Application   │    │  Gateway         │    │ ContextStore    │
│                 │    │  (us-east-1)     │    │  (us-east-1)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   Context Data   │
                       │ • Conversations  │
                       │ • Knowledge Base │
                       │ • User Prefs     │
                       └──────────────────┘
```

## 📊 **DynamoDB Schema**

### **Table: AgentCoreContextStore**
- **Partition Key**: `session_id` (String)
- **Sort Key**: `timestamp` (Number)
- **GSI**: `ContextTypeIndex` (context_type, timestamp)
- **Region**: us-east-1
- **Billing**: Pay-per-request

### **Data Types**
1. **conversation**: User-agent interactions
2. **knowledge**: Knowledge base entries
3. **user_preference**: User settings and preferences

## 🔧 **Manual Gateway Setup**

Since IAM permissions may be limited, create the AgentCore Gateway manually:

1. **AWS Bedrock Console** → AgentCore → Gateways
2. **Create Gateway**:
   - Name: `AgentCoreDynamoDBGateway`
   - Protocol: `MCP`
   - Region: `us-east-1`
3. **Add DynamoDB Target**:
   - Target: `AgentCoreContextStore`
   - Access: Read/Write

## 🎯 **Current Status**

| Component | Status | Region | Notes |
|-----------|--------|---------|-------|
| DynamoDB Table | ✅ ACTIVE | us-east-1 | Ready with sample data |
| Client Library | ✅ READY | us-east-1 | Tested and working |
| IAM Service Role | ✅ EXISTS | Global | Pre-created by AWS |
| AgentCore Gateway | ⏳ MANUAL | us-east-1 | Create via AWS Console |

## 🚀 **Benefits**

- ✅ **No Marketplace Dependencies**: Works immediately
- ✅ **Highly Scalable**: DynamoDB handles any volume
- ✅ **Cost Effective**: Pay-per-request pricing
- ✅ **Fast Queries**: Optimized for agent workloads
- ✅ **AWS Native**: Seamless AgentCore integration
- ✅ **Production Ready**: Tested and documented

## 📚 **Next Steps**

1. **Create AgentCore Gateway** (manual via AWS Console)
2. **Connect to DynamoDB** (add target configuration)
3. **Start Building Agents** (use client library)
4. **Scale as Needed** (DynamoDB auto-scales)

## 🆘 **Support**

- Check `US_EAST_1_SETUP_COMPLETE.md` for detailed setup
- Use `check_agentcore_status.py` for troubleshooting
- Review client library examples in `agentcore_dynamodb_client.py`

---

**Ready to build context-aware AI agents with AWS AgentCore + DynamoDB!** 🎉

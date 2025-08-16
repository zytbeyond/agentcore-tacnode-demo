# 🚀 **Complete Fresh Environment Setup Guide**

## 📋 **Prerequisites Checklist**

Before running the setup scripts, ensure you have:

### **1. AWS Environment**
```bash
# AWS CLI configured with proper credentials
aws configure
# Verify access
aws sts get-caller-identity
```

### **2. Required IAM Permissions**
Your AWS user/role needs these permissions:
- `bedrock-agentcore:*` (for creating gateways)
- `lambda:*` (for creating Lambda functions)
- `iam:*` (for creating execution roles)
- `cognito-idp:*` (for authentication setup)
- `logs:*` (for CloudWatch logs)

### **3. Python Environment**
```bash
# Python 3.9+ required
python3 --version

# Install required packages
pip install boto3 requests bedrock-agentcore-starter-toolkit
```

### **4. TACNode Token**
You need to provide your TACNode Bearer token.

## 🔧 **Step-by-Step Setup**

### **Step 1: Clone Repository**
```bash
git clone https://github.com/zytbeyond/agentcore-tacnode-demo.git
cd agentcore-tacnode-demo
```

### **Step 2: Configure TACNode Token**
Edit `create_complete_agentcore_gateway_sdk.py` and replace the token:
```python
# Line 21 - Replace with your actual token
TACNODE_TOKEN = "YOUR_ACTUAL_TACNODE_TOKEN_HERE"
```

### **Step 3: Install Dependencies**
```bash
pip install bedrock-agentcore-starter-toolkit bedrock-agentcore boto3 requests
```

### **Step 4: Run Complete Setup**
```bash
python3 create_complete_agentcore_gateway_sdk.py
```

### **Step 5: Verify Integration**
```bash
python3 final_end_to_end_proof.py
```

## 🎯 **Expected Output**

### **Successful Setup:**
```
🎯 CREATING COMPLETE AGENTCORE GATEWAY INTEGRATION WITH SDK
✅ Created Cognito OAuth authorizer
✅ Created Gateway: augment-tacnode-gateway-XXXXXXXXXX
✅ Created Lambda target: XXXXXXXXXX
🏆 COMPLETE AGENTCORE GATEWAY CREATED SUCCESSFULLY!
```

### **Successful Test:**
```
🏆 FINAL END-TO-END PROOF: AGENTCORE → LAMBDA → TACNODE → POSTGRESQL
✅ Authentication successful
✅ SUCCESS: Real data retrieved!
📈 Records returned: 3
🎉 INTEGRATION COMPLETE - NO SIMULATION, NO MOCKING, REAL DATA!
```

## ⚠️ **Common Issues & Solutions**

### **Issue 1: Missing TACNode Token**
```
❌ TACNode token not configured
```
**Solution**: Update the token in `create_complete_agentcore_gateway_sdk.py`

### **Issue 2: AWS Permissions**
```
❌ AccessDenied: User is not authorized to perform bedrock-agentcore:CreateGateway
```
**Solution**: Add required IAM permissions (see prerequisites)

### **Issue 3: Package Not Found**
```
❌ ModuleNotFoundError: No module named 'bedrock_agentcore_starter_toolkit'
```
**Solution**: 
```bash
pip install bedrock-agentcore-starter-toolkit
```

### **Issue 4: Region Issues**
```
❌ Gateway creation failed
```
**Solution**: Ensure you're using `us-east-1` region:
```bash
export AWS_DEFAULT_REGION=us-east-1
```

## 🔄 **What Gets Created**

### **AWS Resources:**
1. **Cognito User Pool** - For OAuth authentication
2. **AgentCore Gateway** - Main integration endpoint
3. **Lambda Function** - Protocol bridge (augment-tacnode-bridge)
4. **IAM Roles** - Execution permissions
5. **Gateway Target** - Lambda connection

### **Configuration Files:**
- `augment-complete-sdk-gateway-config.json` - Complete setup config
- `augment-tacnode-lambda-config.json` - Lambda configuration

## 🧪 **Testing the Setup**

### **Test 1: Authentication**
```bash
# Should return access token
curl -X POST https://COGNITO_DOMAIN.auth.us-east-1.amazoncognito.com/oauth2/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=CLIENT_ID&client_secret=CLIENT_SECRET"
```

### **Test 2: Gateway Query**
```bash
# Should return real PostgreSQL data
curl -X POST https://GATEWAY_URL/mcp \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"augment-tacnode-lambda-target___query","arguments":{"sql":"SELECT COUNT(*) FROM test"}},"id":"test"}'
```

## 🎯 **Success Criteria**

✅ **Setup Complete When:**
- Gateway URL is accessible
- Cognito authentication working
- Lambda function deployed
- Real data retrieved from PostgreSQL
- All test scripts pass

## 📞 **Support**

If you encounter issues:
1. Check AWS CloudWatch logs for Lambda function
2. Verify IAM permissions
3. Ensure TACNode token is valid
4. Check AWS region is `us-east-1`

---

**With these files and this guide, you can recreate the complete AgentCore Gateway → Lambda → TACNode integration in any fresh AWS environment!** 🎉

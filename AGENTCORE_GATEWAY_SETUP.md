# 🏗️ Bedrock AgentCore Gateway Setup Guide

## Overview
This guide will help you create a Bedrock AgentCore Gateway for Tacnode Context Lake integration. Due to IAM permission limitations in the current environment, we'll provide both automated and manual approaches.

## 🎯 Goal
Create a **Bedrock AgentCore Gateway** that will allow you to:
1. Subscribe to **Tacnode Context Lake** on AWS Marketplace
2. Select it from a dropdown in the gateway configuration
3. Enable seamless integration with your AgentCore setup

## 📋 Prerequisites
- AWS Account with appropriate permissions
- Access to AWS Bedrock AgentCore (Preview)
- IAM permissions for creating gateways and roles

## 🔧 Method 1: Manual Setup (Recommended)

### Step 1: Create IAM Role for AgentCore Gateway

1. **Go to AWS IAM Console**
   - Navigate to: https://console.aws.amazon.com/iam/
   - Click "Roles" → "Create role"

2. **Configure Trust Policy**
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Principal": {
           "Service": "bedrock-agentcore.amazonaws.com"
         },
         "Action": "sts:AssumeRole"
       }
     ]
   }
   ```

3. **Attach Permissions Policy**
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "bedrock:InvokeModel",
           "bedrock:InvokeModelWithResponseStream",
           "bedrock-agentcore:*",
           "logs:CreateLogGroup",
           "logs:CreateLogStream",
           "logs:PutLogEvents",
           "kms:Decrypt",
           "kms:GenerateDataKey"
         ],
         "Resource": "*"
       }
     ]
   }
   ```

4. **Name the Role**: `TacnodeAgentCoreGatewayRole`

### Step 2: Create AgentCore Gateway

1. **Go to AWS Bedrock Console**
   - Navigate to: https://console.aws.amazon.com/bedrock/
   - Look for "AgentCore" or "Gateways" section

2. **Create New Gateway**
   - **Name**: `TacnodeContextLakeGateway`
   - **Description**: `Gateway for Tacnode Context Lake integration with AgentCore`
   - **Protocol Type**: `MCP` (Model Context Protocol)
   - **IAM Role**: Select the role created in Step 1

3. **Configure Protocol Settings**
   - **Supported Versions**: `2024-11-05`
   - **Instructions**: `Gateway for connecting to Tacnode Context Lake for real-time data processing and analytics`
   - **Search Type**: `SEMANTIC`

4. **Configure Authorization**
   - **Authorizer Type**: `CUSTOM_JWT`
   - **Discovery URL**: `https://tacnode.com/.well-known/openid_configuration`
   - **Allowed Audience**: `tacnode-context-lake`
   - **Allowed Clients**: `agentcore-gateway`

### Step 3: Subscribe to Tacnode Context Lake

1. **Go to AWS Marketplace**
   - Navigate to: https://aws.amazon.com/marketplace/
   - Search for "Tacnode Context Lake"

2. **Subscribe to the Product**
   - Click "Subscribe"
   - Follow the subscription process
   - Note the product details for gateway configuration

### Step 4: Configure Gateway Target

1. **Return to AgentCore Gateway**
   - Go back to your created gateway
   - Look for "Targets" or "Integrations" section

2. **Add Tacnode Context Lake Target**
   - **Target Name**: `TacnodeContextLake`
   - **Target Type**: Select from dropdown (should show Tacnode Context Lake after subscription)
   - **Configuration**: Follow the marketplace integration guide

## 🤖 Method 2: Automated Setup (If Permissions Allow)

If you have the necessary IAM permissions, you can use the provided Python script:

```bash
# Run the automated setup
python3 create_agentcore_gateway.py
```

## 🔍 Verification Steps

1. **Check Gateway Status**
   - Gateway should show "ACTIVE" status
   - Gateway URL should be available

2. **Test Connection**
   - Verify the gateway can communicate with Tacnode Context Lake
   - Check logs for any connection issues

3. **Validate Integration**
   - Test data flow between AgentCore and Tacnode Context Lake
   - Verify semantic search functionality

## 📊 Expected Configuration

After successful setup, you should have:

- **Gateway ID**: `gw-xxxxxxxxxx`
- **Gateway ARN**: `arn:aws:bedrock-agentcore:us-west-2:ACCOUNT:gateway/gw-xxxxxxxxxx`
- **Gateway URL**: `https://gateway-url.bedrock-agentcore.us-west-2.amazonaws.com`
- **Status**: `ACTIVE`

## 🎯 Next Steps

Once the gateway is created and Tacnode Context Lake is subscribed:

1. **Configure Data Sources**: Set up your data sources in Tacnode Context Lake
2. **Test Queries**: Verify semantic search and data retrieval
3. **Monitor Performance**: Check gateway metrics and logs
4. **Scale as Needed**: Adjust gateway configuration based on usage

## 🆘 Troubleshooting

### Common Issues:

1. **IAM Permission Errors**
   - Ensure the IAM role has correct trust policy
   - Verify all required permissions are attached

2. **Gateway Creation Fails**
   - Check region availability for AgentCore
   - Verify service quotas and limits

3. **Marketplace Integration Issues**
   - Ensure subscription is active
   - Check marketplace product configuration

### Support Resources:

- AWS Bedrock Documentation
- Tacnode Context Lake Documentation
- AWS Support (if you have a support plan)

## 📝 Notes

- AgentCore is currently in preview - features may change
- Ensure you're using the correct AWS region (us-west-2 recommended)
- Keep track of costs associated with gateway usage and marketplace subscriptions

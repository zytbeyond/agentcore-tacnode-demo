# AgentCore Demo Setup Requirements

## What You Need to Get Started

### 1. AWS Account and Credentials ✅ **REQUIRED**

**AWS Account Requirements:**
- Active AWS account with billing enabled
- Access to AWS Bedrock service
- Permissions for AgentCore Runtime (Preview)

**Credentials Setup:**
You have several options for AWS credentials:

#### Option A: AWS CLI Configuration (Recommended for Development)
```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key  
# Enter default region: us-west-2
# Enter default output format: json
```

#### Option B: Environment Variables
```bash
export AWS_ACCESS_KEY_ID=your_access_key_here
export AWS_SECRET_ACCESS_KEY=your_secret_key_here
export AWS_DEFAULT_REGION=us-west-2
```

#### Option C: IAM Roles (Recommended for Production)
- Attach IAM role to EC2 instance, Lambda function, or ECS task
- No need to manage credentials manually

**Required AWS Permissions:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream",
        "bedrock:ListFoundationModels"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow", 
      "Action": [
        "bedrock-agentcore:*"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream", 
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
```

### 2. AWS Bedrock Model Access ✅ **REQUIRED**

**Model Required:**
- Anthropic Claude 3.7 Sonnet

**Setup Steps:**
1. Go to AWS Bedrock Console: https://console.aws.amazon.com/bedrock/
2. Navigate to "Model access" in the left sidebar
3. Click "Request model access"
4. Select "Anthropic Claude 3.7 Sonnet"
5. Submit request (usually approved immediately)
6. Verify access in the model list

**Region:** us-west-2 (Oregon) - recommended for best AgentCore support

### 3. Tacnode Context Lake Subscription ✅ **REQUIRED**

**AWS Marketplace Subscription:**
- Product: Tacnode Context Lake
- URL: https://aws.amazon.com/marketplace/pp/prodview-ofzyfzpx52yni

**Subscription Process:**
1. Visit the AWS Marketplace link above
2. Click "View purchase options"
3. Review pricing (pay-per-use model at $0.01 per unit)
4. Click "Subscribe"
5. Configure your subscription settings
6. Complete the subscription process

**What You'll Get:**
- API endpoint for Tacnode Context Lake
- API key for authentication
- MCP (Model Context Protocol) token
- Access to the managed MCP server

**Post-Subscription Setup:**
1. Access your Tacnode dashboard
2. Create a new "Nodegroup" (database instance)
3. Generate MCP tokens from Nodegroup settings
4. Note down your endpoint URL and credentials

### 4. Development Environment Setup

**Required Software:**
- Python 3.10 or higher
- pip (Python package manager)
- Git
- Docker (optional, for containerized deployment)

**Installation Commands:**
```bash
# Check Python version
python --version  # Should be 3.10+

# Install required packages
pip install strands-agents strands-agents-tools boto3 aiohttp psycopg2-binary

# Clone the demo project
git clone <your-repo-url>
cd AgentCore

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install project dependencies
pip install -r requirements.txt
```

### 5. Environment Configuration

**Create .env file:**
```bash
# Copy the example file
cp .env.example .env

# Edit with your actual values
nano .env  # or use your preferred editor
```

**Required Environment Variables:**
```bash
# AWS Configuration
AWS_REGION=us-west-2
AWS_PROFILE=default  # or your AWS profile name

# Bedrock Configuration  
BEDROCK_MODEL_ID=anthropic.claude-3-7-sonnet-20241022-v1:0

# Tacnode Configuration (from your subscription)
TACNODE_ENDPOINT=https://your-instance.tacnode.io
TACNODE_API_KEY=your_api_key_here
TACNODE_MCP_TOKEN=your_mcp_token_here
```

## Quick Start Verification

### Test Your Setup:

1. **Test AWS Credentials:**
```bash
aws sts get-caller-identity
```

2. **Test Bedrock Access:**
```bash
aws bedrock list-foundation-models --region us-west-2
```

3. **Test Tacnode Connection:**
```bash
curl -H "Authorization: Bearer $TACNODE_API_KEY" $TACNODE_ENDPOINT/health
```

4. **Run the Demo:**
```bash
python src/agent/demo_agent.py
```

## What I Can Help You With

### ✅ I Can Assist With:
- Setting up the development environment
- Configuring the agent code
- Writing custom tools and integrations
- Debugging connection issues
- Creating demo scenarios
- Documentation and examples

### ❌ I Cannot Help With:
- Creating AWS accounts or managing billing
- Subscribing to AWS Marketplace products
- Generating AWS credentials
- Accessing your Tacnode dashboard
- Managing your cloud infrastructure

## Next Steps After Setup

1. **Verify Everything Works:**
   - Run `python examples/basic_usage.py`
   - Check that all health checks pass

2. **Explore the Demo:**
   - Try the interactive mode: `python src/agent/demo_agent.py`
   - Run demo scenarios: `python src/agent/demo_agent.py demo`

3. **Customize for Your Use Case:**
   - Modify the system prompt in `demo_agent.py`
   - Add custom tools in `src/tools/`
   - Create your own demo scenarios

4. **Deploy to Production:**
   - Follow the deployment guide in `docs/deployment-guide.md`
   - Set up monitoring and logging
   - Configure security and access controls

## Cost Considerations

**AWS Bedrock:**
- Pay per token for model usage
- Typical cost: $0.003 per 1K input tokens, $0.015 per 1K output tokens

**Tacnode Context Lake:**
- Pay-per-use model at $0.01 per unit
- Units based on compute and storage usage

**AWS Infrastructure:**
- Lambda: Pay per invocation and duration
- CloudWatch: Pay for logs and metrics storage
- Other AWS services as needed

## Support and Troubleshooting

**Common Issues:**
1. **"Access Denied" errors:** Check AWS credentials and permissions
2. **"Model not found" errors:** Verify Bedrock model access
3. **Tacnode connection failures:** Check API key and endpoint
4. **Import errors:** Ensure all dependencies are installed

**Getting Help:**
- Check the troubleshooting section in `docs/deployment-guide.md`
- Review AWS Bedrock documentation
- Contact Tacnode support for Context Lake issues
- Use the GitHub issues for code-related problems

## Summary

To get started, you need:
1. ✅ AWS account with Bedrock access
2. ✅ Tacnode Context Lake subscription  
3. ✅ Development environment setup
4. ✅ Proper configuration

The total setup time is typically 30-60 minutes, depending on AWS approval times and your familiarity with the services.

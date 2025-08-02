# Deployment Guide: AgentCore Demo

## Prerequisites

### 1. AWS Account Setup
- **AWS Account**: Active AWS account with billing enabled
- **IAM Permissions**: Administrator access or specific permissions for:
  - Amazon Bedrock (model access and AgentCore)
  - AWS Lambda (for serverless deployment)
  - Amazon CloudWatch (for monitoring)
  - AWS IAM (for role management)
  - Amazon VPC (for network configuration)

### 2. AWS Bedrock Model Access
- **Required Models**: Anthropic Claude 3.7 Sonnet
- **Region**: us-west-2 (recommended)
- **Setup Steps**:
  1. Navigate to AWS Bedrock console
  2. Go to "Model access" in the left sidebar
  3. Request access to Anthropic Claude 3.7 Sonnet
  4. Wait for approval (usually immediate)

### 3. Tacnode Context Lake Subscription
- **AWS Marketplace**: Subscribe to Tacnode Context Lake
- **Subscription Steps**:
  1. Visit [Tacnode Context Lake on AWS Marketplace](https://aws.amazon.com/marketplace/pp/prodview-ofzyfzpx52yni)
  2. Click "View purchase options"
  3. Configure subscription settings
  4. Complete subscription process
  5. Note the API endpoint and credentials

### 4. Development Environment
- **Python**: Version 3.10 or higher
- **Docker**: Latest version (for containerization)
- **Git**: For source code management
- **AWS CLI**: Configured with appropriate credentials

## Installation Steps

### Step 1: Clone and Setup Project
```bash
# Clone the repository
git clone <repository-url>
cd AgentCore

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables
Create a `.env` file in the project root:
```bash
# AWS Configuration
AWS_REGION=us-west-2
AWS_PROFILE=default

# Bedrock Configuration
BEDROCK_MODEL_ID=anthropic.claude-3-7-sonnet-20241022-v1:0
BEDROCK_AGENTCORE_ENDPOINT=https://bedrock-agentcore.us-west-2.amazonaws.com

# Tacnode Configuration
TACNODE_ENDPOINT=<your-tacnode-endpoint>
TACNODE_API_KEY=<your-tacnode-api-key>
TACNODE_MCP_TOKEN=<your-mcp-token>

# Agent Configuration
AGENT_TIMEOUT=300
MAX_CONCURRENT_SESSIONS=100
LOG_LEVEL=INFO
```

### Step 3: Configure AWS Credentials
```bash
# Option 1: AWS CLI configuration
aws configure

# Option 2: Environment variables
export AWS_ACCESS_KEY_ID=<your-access-key>
export AWS_SECRET_ACCESS_KEY=<your-secret-key>
export AWS_DEFAULT_REGION=us-west-2

# Option 3: IAM roles (recommended for production)
# Attach appropriate IAM role to your compute instance
```

### Step 4: Tacnode Setup
```bash
# Test Tacnode connectivity
python scripts/test_tacnode_connection.py

# Initialize sample data (optional)
python scripts/setup_sample_data.py

# Verify MCP server connectivity
python scripts/test_mcp_connection.py
```

## Deployment Options

### Option 1: Local Development Deployment

#### Quick Start
```bash
# Install dependencies
pip install strands-agents strands-agents-tools

# Run the demo agent
python src/agent/demo_agent.py
```

#### Local Testing
```bash
# Run unit tests
pytest tests/

# Run integration tests
pytest tests/integration/

# Start local development server
python src/app.py
```

### Option 2: AWS Lambda Deployment

#### Package and Deploy
```bash
# Build deployment package
python scripts/build_lambda_package.py

# Deploy using AWS CLI
aws lambda create-function \
  --function-name agentcore-demo \
  --runtime python3.10 \
  --role arn:aws:iam::ACCOUNT:role/lambda-execution-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://deployment/lambda-package.zip

# Configure environment variables
aws lambda update-function-configuration \
  --function-name agentcore-demo \
  --environment Variables="{$(cat .env | tr '\n' ',' | sed 's/,$//')}"
```

#### API Gateway Setup
```bash
# Create API Gateway
aws apigateway create-rest-api --name agentcore-demo-api

# Configure integration with Lambda
# (See deployment/api-gateway-config.json for full configuration)
```

### Option 3: AWS Bedrock AgentCore Runtime Deployment

#### AgentCore Configuration
```yaml
# agentcore-config.yaml
apiVersion: bedrock.aws.amazon.com/v1
kind: Agent
metadata:
  name: tacnode-demo-agent
spec:
  runtime:
    type: python3.10
    memory: 2048MB
    timeout: 300s
  model:
    provider: bedrock
    modelId: anthropic.claude-3-7-sonnet-20241022-v1:0
  tools:
    - name: tacnode-mcp
      type: mcp-server
      config:
        endpoint: ${TACNODE_ENDPOINT}
        authentication:
          type: bearer
          token: ${TACNODE_MCP_TOKEN}
  environment:
    - name: TACNODE_API_KEY
      valueFrom:
        secretKeyRef:
          name: tacnode-credentials
          key: api-key
```

#### Deploy to AgentCore
```bash
# Deploy agent configuration
aws bedrock-agentcore deploy-agent \
  --config-file agentcore-config.yaml \
  --region us-west-2

# Monitor deployment status
aws bedrock-agentcore describe-agent \
  --agent-name tacnode-demo-agent
```

### Option 4: Container Deployment

#### Docker Build
```bash
# Build Docker image
docker build -t agentcore-demo .

# Run locally
docker run -p 8080:8080 --env-file .env agentcore-demo

# Push to ECR (for AWS deployment)
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-west-2.amazonaws.com
docker tag agentcore-demo:latest <account>.dkr.ecr.us-west-2.amazonaws.com/agentcore-demo:latest
docker push <account>.dkr.ecr.us-west-2.amazonaws.com/agentcore-demo:latest
```

#### ECS Deployment
```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name agentcore-demo

# Register task definition
aws ecs register-task-definition --cli-input-json file://deployment/ecs-task-definition.json

# Create service
aws ecs create-service \
  --cluster agentcore-demo \
  --service-name agentcore-demo-service \
  --task-definition agentcore-demo:1 \
  --desired-count 2
```

## Configuration Management

### Environment-Specific Configurations

#### Development
```yaml
# config/development.yaml
agent:
  debug: true
  log_level: DEBUG
  timeout: 60
tacnode:
  endpoint: https://dev.tacnode.io
  connection_pool_size: 5
monitoring:
  enabled: false
```

#### Staging
```yaml
# config/staging.yaml
agent:
  debug: false
  log_level: INFO
  timeout: 300
tacnode:
  endpoint: https://staging.tacnode.io
  connection_pool_size: 10
monitoring:
  enabled: true
  metrics_endpoint: https://staging-metrics.example.com
```

#### Production
```yaml
# config/production.yaml
agent:
  debug: false
  log_level: WARN
  timeout: 300
tacnode:
  endpoint: https://api.tacnode.io
  connection_pool_size: 20
monitoring:
  enabled: true
  metrics_endpoint: https://metrics.example.com
security:
  encryption_at_rest: true
  audit_logging: true
```

## Monitoring and Observability

### CloudWatch Setup
```bash
# Create log group
aws logs create-log-group --log-group-name /aws/lambda/agentcore-demo

# Create custom metrics
aws cloudwatch put-metric-data \
  --namespace "AgentCore/Demo" \
  --metric-data MetricName=ResponseTime,Value=100,Unit=Milliseconds
```

### Dashboard Configuration
```json
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AgentCore/Demo", "ResponseTime"],
          ["AgentCore/Demo", "RequestCount"],
          ["AgentCore/Demo", "ErrorRate"]
        ],
        "period": 300,
        "stat": "Average",
        "region": "us-west-2",
        "title": "Agent Performance"
      }
    }
  ]
}
```

## Security Configuration

### IAM Role Setup
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "arn:aws:bedrock:us-west-2::foundation-model/anthropic.claude-3-7-sonnet*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:us-west-2:*:*"
    }
  ]
}
```

### VPC Configuration
```bash
# Create VPC for secure deployment
aws ec2 create-vpc --cidr-block 10.0.0.0/16

# Create private subnets
aws ec2 create-subnet --vpc-id vpc-12345678 --cidr-block 10.0.1.0/24

# Configure security groups
aws ec2 create-security-group \
  --group-name agentcore-demo-sg \
  --description "Security group for AgentCore demo"
```

## Troubleshooting

### Common Issues

#### 1. Bedrock Model Access Denied
```bash
# Check model access status
aws bedrock list-foundation-models --region us-west-2

# Request model access if needed
aws bedrock put-model-invocation-logging-configuration \
  --logging-config '{"cloudWatchConfig":{"logGroupName":"/aws/bedrock/modelinvocations","roleArn":"arn:aws:iam::ACCOUNT:role/service-role/AmazonBedrockExecutionRoleForModelInvocation"}}'
```

#### 2. Tacnode Connection Issues
```bash
# Test connectivity
curl -H "Authorization: Bearer $TACNODE_API_KEY" $TACNODE_ENDPOINT/health

# Verify MCP server
npx mcp-remote $TACNODE_ENDPOINT/mcp --header "Authorization: Bearer $TACNODE_MCP_TOKEN"
```

#### 3. Lambda Timeout Issues
```bash
# Increase timeout
aws lambda update-function-configuration \
  --function-name agentcore-demo \
  --timeout 300
```

### Debugging Commands
```bash
# Check logs
aws logs tail /aws/lambda/agentcore-demo --follow

# Monitor metrics
aws cloudwatch get-metric-statistics \
  --namespace "AgentCore/Demo" \
  --metric-name ResponseTime \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T23:59:59Z \
  --period 3600 \
  --statistics Average
```

## Next Steps

1. **Verify Deployment**: Run health checks and basic functionality tests
2. **Load Testing**: Use provided scripts to test performance under load
3. **Monitoring Setup**: Configure alerts and dashboards
4. **Security Review**: Implement additional security measures as needed
5. **Documentation**: Update configuration documentation for your environment

# AgentCore Demo Project

## Overview
This project demonstrates the integration of AWS Bedrock AgentCore runtime with Strands SDK, Bedrock Gateway, and Tacnode Context Lake to create a powerful AI agent solution.

## Architecture Components

### 1. AWS Bedrock AgentCore Runtime
- Secure, serverless runtime for AI agents
- Complete session isolation
- Support for long-running workloads (up to 8 hours)
- Enterprise-grade security and reliability

### 2. Strands SDK
- Open-source AI agents SDK
- Model-driven approach to building agents
- Supports multiple models and frameworks
- Simplified agent development with minimal code

### 3. Bedrock Gateway
- Converts APIs into agent-ready tools
- MCP (Model Context Protocol) compatible
- Seamless integration with existing services

### 4. Tacnode Context Lake
- Real-time data foundation for AI agents
- Single endpoint architecture
- Supports multiple data types (structured, JSON, GIS, vector)
- Millisecond-level latency
- PostgreSQL compatibility

## Project Structure
```
AgentCore/
├── README.md
├── docs/
│   ├── requirements.md
│   ├── technical-spec.md
│   ├── storyline.md
│   └── deployment-guide.md
├── src/
│   ├── agent/
│   ├── tools/
│   └── config/
├── examples/
├── tests/
└── deployment/
```

## Quick Start
1. Set up AWS credentials and Bedrock model access
2. Subscribe to Tacnode Context Lake in AWS Marketplace
3. Install dependencies
4. Configure environment variables
5. Run the demo agent

## Prerequisites
- AWS Account with Bedrock access
- Tacnode Context Lake subscription
- Python 3.10+
- Docker (for local development)

## Documentation
See the `docs/` directory for detailed documentation including:
- Technical specifications
- Requirements analysis
- Deployment guide
- Usage examples

## Support
For questions and support, please refer to the documentation or contact the development team.

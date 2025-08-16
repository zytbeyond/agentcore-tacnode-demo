#!/usr/bin/env python3
"""
Complete setup script for fresh environment
This script creates the entire AgentCore Gateway → Lambda → TACNode integration
"""

import json
import logging
import sys
import os
from datetime import datetime

def check_prerequisites():
    """Check if all prerequisites are met"""
    print("🔍 CHECKING PREREQUISITES...")
    print("=" * 50)
    
    # Check Python version
    import sys
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ required")
        return False
    print("✅ Python version OK")
    
    # Check AWS CLI
    try:
        import boto3
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"✅ AWS credentials OK - Account: {identity['Account']}")
    except Exception as e:
        print(f"❌ AWS credentials issue: {e}")
        return False
    
    # Check required packages
    try:
        from bedrock_agentcore_starter_toolkit.operations.gateway.client import GatewayClient
        print("✅ AgentCore SDK available")
    except ImportError:
        print("❌ AgentCore SDK not installed")
        print("Run: pip install bedrock-agentcore-starter-toolkit")
        return False
    
    return True

def get_tacnode_token():
    """Get TACNode token from user input or environment"""
    print("\n🔑 TACNODE TOKEN CONFIGURATION")
    print("=" * 50)
    
    # Check environment variable first
    token = os.environ.get('TACNODE_TOKEN')
    if token:
        print(f"✅ Found TACNode token in environment variable (length: {len(token)})")
        return token
    
    # Ask user for token
    print("Please provide your TACNode Bearer token:")
    print("(You can also set TACNODE_TOKEN environment variable)")
    token = input("TACNode Token: ").strip()
    
    if not token:
        print("❌ TACNode token is required!")
        return None
    
    print(f"✅ TACNode token provided (length: {len(token)})")
    return token

def create_lambda_function(tacnode_token):
    """Create the Lambda function with the provided token"""
    print("\n🚀 CREATING LAMBDA FUNCTION...")
    print("=" * 50)
    
    import boto3
    import zipfile
    import io
    
    # Lambda code that handles AgentCore Gateway requests
    lambda_code = f'''
import json
import urllib3
import os

def lambda_handler(event, context):
    """
    Lambda function to bridge AgentCore Gateway requests to TACNode
    """
    
    print(f"🔍 Received event: {{json.dumps(event, indent=2)}}")
    
    # TACNode token from environment
    tacnode_token = "{tacnode_token}"
    
    try:
        # AgentCore Gateway sends the SQL parameter directly
        if 'sql' in event and isinstance(event['sql'], str):
            sql_query = event['sql']
            print(f"📝 Detected AgentCore Gateway SQL request: {{sql_query}}")
            
            # Create JSON-RPC request for TACNode
            tacnode_request = {{
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {{
                    "name": "query",
                    "arguments": {{
                        "sql": sql_query
                    }}
                }},
                "id": 1
            }}
        else:
            # Handle other request formats
            if 'body' in event:
                if isinstance(event['body'], str):
                    request_body = json.loads(event['body'])
                else:
                    request_body = event['body']
            else:
                request_body = event
            
            # Default to tools/list if no SQL
            tacnode_request = {{
                "jsonrpc": "2.0",
                "method": request_body.get('method', 'tools/list'),
                "params": request_body.get('params', {{}}),
                "id": request_body.get('id', 1)
            }}
        
        print(f"🚀 Sending to TACNode: {{json.dumps(tacnode_request, indent=2)}}")
        
        # Make request to TACNode
        http = urllib3.PoolManager()
        
        headers = {{
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream',
            'Authorization': f'Bearer {{tacnode_token}}'
        }}
        
        response = http.request(
            'POST',
            'https://mcp-server.tacnode.io/mcp',
            body=json.dumps(tacnode_request),
            headers=headers
        )
        
        print(f"📥 TACNode response status: {{response.status}}")
        
        if response.status == 200:
            response_text = response.data.decode('utf-8')
            
            # Handle event-stream format
            if response_text.startswith('event: message'):
                lines = response_text.strip().split('\\n')
                for line in lines:
                    if line.startswith('data: '):
                        data_json = line[6:]
                        tacnode_response = json.loads(data_json)
                        break
            else:
                tacnode_response = json.loads(response_text)
            
            return {{
                'statusCode': 200,
                'headers': {{'Content-Type': 'application/json'}},
                'body': json.dumps(tacnode_response)
            }}
        else:
            error_response = {{
                'jsonrpc': '2.0',
                'error': {{
                    'code': response.status,
                    'message': f'TACNode request failed: {{response.data.decode("utf-8")}}'
                }},
                'id': tacnode_request.get('id', 1)
            }}
            
            return {{
                'statusCode': response.status,
                'headers': {{'Content-Type': 'application/json'}},
                'body': json.dumps(error_response)
            }}
            
    except Exception as e:
        print(f"❌ Error in Lambda: {{str(e)}}")
        error_response = {{
            'jsonrpc': '2.0',
            'error': {{
                'code': -32603,
                'message': f'Internal error: {{str(e)}}'
            }},
            'id': 1
        }}
        
        return {{
            'statusCode': 500,
            'headers': {{'Content-Type': 'application/json'}},
            'body': json.dumps(error_response)
        }}
'''
    
    # Create zip file
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', lambda_code)
    
    # Create Lambda function
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    # Create execution role first
    iam = boto3.client('iam', region_name='us-east-1')
    
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "lambda.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    role_name = "fresh-env-lambda-execution-role"
    
    try:
        role_response = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="Lambda execution role for fresh environment setup"
        )
        role_arn = role_response['Role']['Arn']
        
        # Attach basic execution policy
        iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
        )
        
        print(f"✅ Created IAM role: {role_arn}")
    except iam.exceptions.EntityAlreadyExistsException:
        role_response = iam.get_role(RoleName=role_name)
        role_arn = role_response['Role']['Arn']
        print(f"✅ Using existing IAM role: {role_arn}")
    
    # Wait for role to be available
    import time
    time.sleep(10)
    
    function_name = "fresh-env-tacnode-bridge"
    
    try:
        response = lambda_client.create_function(
            FunctionName=function_name,
            Runtime='python3.9',
            Role=role_arn,
            Handler='lambda_function.lambda_handler',
            Code={'ZipFile': zip_buffer.getvalue()},
            Description='Fresh environment - AgentCore Gateway to TACNode bridge',
            Timeout=30
        )
        
        lambda_arn = response['FunctionArn']
        print(f"✅ Created Lambda function: {lambda_arn}")
        return lambda_arn
        
    except lambda_client.exceptions.ResourceConflictException:
        # Update existing function
        lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_buffer.getvalue()
        )
        
        response = lambda_client.get_function(FunctionName=function_name)
        lambda_arn = response['Configuration']['FunctionArn']
        print(f"✅ Updated Lambda function: {lambda_arn}")
        return lambda_arn

def create_agentcore_gateway(lambda_arn):
    """Create the AgentCore Gateway using SDK"""
    print("\n🌐 CREATING AGENTCORE GATEWAY...")
    print("=" * 50)
    
    from bedrock_agentcore_starter_toolkit.operations.gateway.client import GatewayClient
    
    # Initialize client
    client = GatewayClient(region_name="us-east-1")
    
    # Create OAuth authorizer
    print("🔐 Creating OAuth authorizer...")
    cognito_response = client.create_oauth_authorizer_with_cognito("FreshEnvTACNodeGateway")
    
    # Create gateway
    print("🌐 Creating MCP Gateway...")
    import time
    unique_name = f"fresh-env-tacnode-gateway-{int(time.time())}"
    
    gateway = client.create_mcp_gateway(
        name=unique_name,
        authorizer_config=cognito_response["authorizer_config"],
        enable_semantic_search=True
    )
    
    # Create Lambda target
    print("🎯 Creating Lambda target...")
    tool_schema = [
        {
            "name": "query",
            "description": "Execute SQL queries on the TACNode PostgreSQL database",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "The SQL query to execute"
                    }
                },
                "required": ["sql"]
            }
        }
    ]
    
    lambda_target = client.create_mcp_gateway_target(
        gateway=gateway,
        name="fresh-env-tacnode-lambda-target",
        target_type="lambda",
        target_payload={
            "lambdaArn": lambda_arn,
            "toolSchema": {
                "inlinePayload": tool_schema
            }
        }
    )
    
    # Extract gateway info
    if hasattr(gateway, 'gateway_id'):
        gateway_id = gateway.gateway_id
        gateway_url = gateway.endpoint_url
    else:
        # Handle different response formats
        gateway_id = "Unknown"
        gateway_url = "Unknown"
    
    if hasattr(lambda_target, 'target_id'):
        target_id = lambda_target.target_id
    else:
        target_id = "Unknown"
    
    print(f"✅ Gateway created: {gateway_id}")
    print(f"✅ Gateway URL: {gateway_url}")
    print(f"✅ Target created: {target_id}")
    
    return {
        'gateway_id': gateway_id,
        'gateway_url': gateway_url,
        'target_id': target_id,
        'cognito': cognito_response['client_info']
    }

def main():
    """Main setup function"""
    print("🚀 FRESH ENVIRONMENT SETUP FOR AGENTCORE → TACNODE INTEGRATION")
    print("=" * 80)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please fix the issues above.")
        sys.exit(1)
    
    # Get TACNode token
    tacnode_token = get_tacnode_token()
    if not tacnode_token:
        print("\n❌ TACNode token required. Exiting.")
        sys.exit(1)
    
    # Create Lambda function
    lambda_arn = create_lambda_function(tacnode_token)
    
    # Create AgentCore Gateway
    gateway_config = create_agentcore_gateway(lambda_arn)
    
    # Save configuration
    config = {
        "lambda_arn": lambda_arn,
        "gateway": gateway_config,
        "created_at": datetime.now().isoformat(),
        "setup_type": "fresh_environment"
    }
    
    with open("fresh-env-agentcore-config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"\n🏆 FRESH ENVIRONMENT SETUP COMPLETE!")
    print("=" * 80)
    print(f"🌐 Gateway URL: {gateway_config['gateway_url']}")
    print(f"📋 Gateway ID: {gateway_config['gateway_id']}")
    print(f"🔐 Client ID: {gateway_config['cognito']['client_id']}")
    print(f"✅ Configuration saved to: fresh-env-agentcore-config.json")
    
    print(f"\n🧪 NEXT STEPS:")
    print(f"1. Test the integration: python3 test_fresh_environment.py")
    print(f"2. Check the configuration file for all details")
    print(f"3. Use the Gateway URL for your applications")

if __name__ == "__main__":
    main()

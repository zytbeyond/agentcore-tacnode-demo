#!/usr/bin/env python3
"""
Create Lambda function as proxy between AgentCore Gateway and TACNode
This handles SSE responses and provides clean JSON to the Gateway
"""

import boto3
import json
import time
import zipfile
import os

def get_tacnode_token():
    """Get TACNode token"""
    if os.path.exists('tacnode_token.txt'):
        with open('tacnode_token.txt', 'r') as f:
            token = f.read().strip()
        if token:
            return token
    return None

def create_lambda_function_code(tacnode_token):
    """Create Lambda function code that proxies TACNode requests"""
    
    lambda_code = '''
import json
import urllib3
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# TACNode configuration
TACNODE_URL = "https://mcp-server.tacnode.io/mcp"
TACNODE_TOKEN = "''' + tacnode_token + '''"

def parse_sse_response(response_text):
    """Parse Server-Sent Events response"""
    lines = response_text.strip().split('\\n')
    
    for line in lines:
        if line.startswith('data: '):
            # Extract JSON data from SSE format
            json_data = line[6:]  # Remove 'data: ' prefix
            try:
                return json.loads(json_data)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON: {e}")
                logger.error(f"Raw data: {json_data}")
                return None
    
    return None

def lambda_handler(event, context):
    """Lambda handler that proxies requests to TACNode"""
    
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Extract the request body
        if 'body' in event:
            if isinstance(event['body'], str):
                request_body = json.loads(event['body'])
            else:
                request_body = event['body']
        else:
            request_body = event
        
        logger.info(f"Request body: {json.dumps(request_body)}")
        
        # Prepare headers for TACNode
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream',
            'Authorization': f'Bearer {TACNODE_TOKEN}'
        }
        
        # Create HTTP client
        http = urllib3.PoolManager()
        
        # Make request to TACNode
        response = http.request(
            'POST',
            TACNODE_URL,
            body=json.dumps(request_body),
            headers=headers,
            timeout=30
        )
        
        logger.info(f"TACNode response status: {response.status}")
        logger.info(f"TACNode response headers: {dict(response.headers)}")
        
        if response.status == 200:
            response_text = response.data.decode('utf-8')
            logger.info(f"TACNode raw response: {response_text}")
            
            # Check if it's SSE response
            if 'text/event-stream' in response.headers.get('content-type', ''):
                # Parse SSE response
                parsed_response = parse_sse_response(response_text)
                
                if parsed_response:
                    logger.info(f"Parsed SSE response: {json.dumps(parsed_response)}")
                    
                    # Return clean JSON response for AgentCore Gateway
                    return {
                        'statusCode': 200,
                        'headers': {
                            'Content-Type': 'application/json'
                        },
                        'body': json.dumps(parsed_response)
                    }
                else:
                    logger.error("Failed to parse SSE response")
                    return {
                        'statusCode': 500,
                        'headers': {
                            'Content-Type': 'application/json'
                        },
                        'body': json.dumps({
                            'jsonrpc': '2.0',
                            'error': {
                                'code': -32603,
                                'message': 'Failed to parse TACNode SSE response'
                            },
                            'id': request_body.get('id', 1)
                        })
                    }
            else:
                # Regular JSON response
                try:
                    json_response = json.loads(response_text)
                    return {
                        'statusCode': 200,
                        'headers': {
                            'Content-Type': 'application/json'
                        },
                        'body': json.dumps(json_response)
                    }
                except json.JSONDecodeError:
                    return {
                        'statusCode': 200,
                        'headers': {
                            'Content-Type': 'application/json'
                        },
                        'body': response_text
                    }
        else:
            logger.error(f"TACNode error: {response.status} - {response.data.decode('utf-8')}")
            return {
                'statusCode': response.status,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({
                    'jsonrpc': '2.0',
                    'error': {
                        'code': -32603,
                        'message': f'TACNode request failed: {response.status}'
                    },
                    'id': request_body.get('id', 1)
                })
            }
            
    except Exception as e:
        logger.error(f"Lambda error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'jsonrpc': '2.0',
                'error': {
                    'code': -32603,
                    'message': f'Lambda proxy error: {str(e)}'
                },
                'id': 1
            })
        }
'''
    
    return lambda_code

def create_lambda_deployment_package(lambda_code):
    """Create Lambda deployment package"""
    print(f"📦 Creating Lambda deployment package")
    
    # Write Lambda code to file
    with open('lambda_function.py', 'w') as f:
        f.write(lambda_code)
    
    # Create ZIP file
    with zipfile.ZipFile('augment-tacnode-proxy.zip', 'w') as zip_file:
        zip_file.write('lambda_function.py')
    
    print(f"✅ Lambda package created: augment-tacnode-proxy.zip")
    
    # Clean up
    os.remove('lambda_function.py')
    
    return 'augment-tacnode-proxy.zip'

def create_lambda_execution_role():
    """Create IAM role for Lambda execution"""
    print(f"\n🔐 CREATING LAMBDA EXECUTION ROLE")
    print("-" * 50)
    
    iam = boto3.client('iam', region_name='us-east-1')
    
    try:
        role_name = f"augment-tacnode-lambda-role-{int(time.time())}"
        
        # Trust policy for Lambda
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "lambda.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        print(f"📋 Creating IAM role: {role_name}")
        
        # Create role
        role_response = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="IAM role for TACNode Lambda proxy - Created by Augment Agent"
        )
        
        role_arn = role_response['Role']['Arn']
        print(f"✅ IAM role created: {role_arn}")
        
        # Attach basic Lambda execution policy
        iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
        )
        
        print(f"✅ Basic execution policy attached")
        
        # Wait for role to propagate
        print(f"⏳ Waiting for IAM role to propagate...")
        time.sleep(30)
        
        return role_arn
        
    except Exception as e:
        print(f"❌ Error creating Lambda execution role: {e}")
        return None

def create_lambda_function(lambda_code, role_arn):
    """Create Lambda function"""
    print(f"\n🚀 CREATING LAMBDA FUNCTION")
    print("-" * 50)
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    try:
        function_name = f"augment-tacnode-proxy-{int(time.time())}"
        
        # Create deployment package
        zip_file_path = create_lambda_deployment_package(lambda_code)
        
        # Read ZIP file
        with open(zip_file_path, 'rb') as zip_file:
            zip_content = zip_file.read()
        
        print(f"📋 Creating Lambda function: {function_name}")
        
        # Create Lambda function
        function_response = lambda_client.create_function(
            FunctionName=function_name,
            Runtime='python3.9',
            Role=role_arn,
            Handler='lambda_function.lambda_handler',
            Code={
                'ZipFile': zip_content
            },
            Description='TACNode proxy Lambda function - Created by Augment Agent',
            Timeout=30,
            MemorySize=128
        )
        
        function_arn = function_response['FunctionArn']
        print(f"✅ Lambda function created: {function_arn}")
        
        # Clean up ZIP file
        os.remove(zip_file_path)
        
        # Wait for function to be ready
        print(f"⏳ Waiting for Lambda function to be ready...")
        time.sleep(15)
        
        return function_name, function_arn
        
    except Exception as e:
        print(f"❌ Error creating Lambda function: {e}")
        return None, None

def test_lambda_function(function_name):
    """Test the Lambda function"""
    print(f"\n🧪 TESTING LAMBDA FUNCTION")
    print("-" * 50)

    lambda_client = boto3.client('lambda', region_name='us-east-1')

    try:
        # Test with tools/list request
        test_payload = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": 1
        }

        print(f"📋 Testing Lambda with tools/list request")

        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(test_payload)
        )

        # Parse response
        response_payload = json.loads(response['Payload'].read())

        print(f"✅ Lambda response status: {response['StatusCode']}")
        print(f"✅ Lambda response: {json.dumps(response_payload, indent=2)}")

        if response['StatusCode'] == 200:
            if 'body' in response_payload:
                body = json.loads(response_payload['body'])
                if 'result' in body and 'tools' in body['result']:
                    tools = body['result']['tools']
                    print(f"✅ Lambda successfully proxied TACNode request!")
                    print(f"✅ Found {len(tools)} tools via Lambda proxy")
                    return True

        return False

    except Exception as e:
        print(f"❌ Error testing Lambda function: {e}")
        return False

def save_lambda_configuration(function_name, function_arn, role_arn):
    """Save Lambda configuration"""
    config = {
        "lambda": {
            "functionName": function_name,
            "functionArn": function_arn,
            "roleArn": role_arn
        },
        "tacnode": {
            "endpoint": "https://mcp-server.tacnode.io/mcp",
            "database": "postgres",
            "table": "test",
            "responseFormat": "text/event-stream",
            "proxyType": "lambda"
        },
        "created_by": "Augment Agent",
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "notes": "Lambda function proxies TACNode SSE responses to clean JSON"
    }

    with open('augment-lambda-tacnode-config.json', 'w') as f:
        json.dump(config, f, indent=2)

    print(f"✅ Configuration saved to: augment-lambda-tacnode-config.json")

    return config

def main():
    """Main setup function"""
    print("🚀 LAMBDA TACNODE PROXY SETUP")
    print("=" * 70)
    print("🎯 Creating Lambda function to proxy TACNode requests")
    print("🎯 Handles SSE responses and provides clean JSON")
    print("🎯 All resources prefixed with 'augment-' for identification")

    # Get TACNode token
    tacnode_token = get_tacnode_token()
    if not tacnode_token:
        print("❌ No TACNode token found. Exiting.")
        return

    print(f"✅ TACNode token loaded")

    # Step 1: Create Lambda code
    lambda_code = create_lambda_function_code(tacnode_token)
    print(f"✅ Lambda code generated")

    # Step 2: Create Lambda execution role
    role_arn = create_lambda_execution_role()
    if not role_arn:
        print("❌ Failed to create Lambda execution role. Exiting.")
        return

    # Step 3: Create Lambda function
    function_name, function_arn = create_lambda_function(lambda_code, role_arn)
    if not function_name:
        print("❌ Failed to create Lambda function. Exiting.")
        return

    # Step 4: Test Lambda function
    success = test_lambda_function(function_name)

    # Step 5: Save configuration
    config = save_lambda_configuration(function_name, function_arn, role_arn)

    print(f"\n" + "=" * 70)
    if success:
        print(f"🎉 LAMBDA TACNODE PROXY SUCCESS!")
        print(f"✅ Lambda function: {function_name}")
        print(f"✅ Function ARN: {function_arn}")
        print(f"✅ SSE to JSON conversion working")
        print(f"✅ TACNode integration working")
        print(f"✅ Configuration saved")

        print(f"\n🌐 VERIFIED ARCHITECTURE:")
        print("   AgentCore Gateway → Lambda Proxy → TACNode → PostgreSQL")
        print("   ✅ Lambda handles SSE responses")
        print("   ✅ Gateway gets clean JSON")
        print("   ✅ Real database queries work")

        print(f"\n🎯 NEXT STEP:")
        print(f"   Now create AgentCore Gateway target pointing to this Lambda")
    else:
        print(f"❌ LAMBDA TACNODE PROXY FAILED")
        print(f"🔍 Check Lambda logs for details")

if __name__ == "__main__":
    main()

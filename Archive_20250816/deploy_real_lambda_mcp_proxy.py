#!/usr/bin/env python3
"""
Deploy REAL Lambda MCP Proxy - NO SHORTCUTS!
Implement actual AgentCore Gateway → Lambda → TACNode flow
"""

import boto3
import json
import os
import zipfile
import time
from datetime import datetime

class RealLambdaMCPProxyDeployer:
    """Deploy real Lambda function for MCP proxy - NO SIMULATION"""
    
    def __init__(self):
        self.lambda_client = boto3.client('lambda', region_name='us-east-1')
        self.iam_client = boto3.client('iam', region_name='us-east-1')
        self.bedrock_agentcore = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
        
        self.tacnode_token = os.getenv('TACNODE_TOKEN')
        if not self.tacnode_token:
            raise ValueError("❌ TACNODE_TOKEN environment variable REQUIRED")
        
        # Load gateway info
        with open('tacnode-agentcore-gateway.json', 'r') as f:
            self.gateway_info = json.load(f)
            self.gateway_id = self.gateway_info['gatewayId']
        
        print("🚀 DEPLOYING REAL LAMBDA MCP PROXY")
        print("=" * 60)
        print("✅ TACNode Token: Available")
        print(f"✅ Gateway ID: {self.gateway_id}")
        print("🚫 NO SHORTCUTS - Implementing REAL gateway integration!")
    
    def create_lambda_execution_role(self):
        """Create real IAM role for Lambda execution"""
        print("\n📋 STEP 1: Creating Lambda Execution Role")
        print("-" * 50)
        
        role_name = "tacnode-mcp-proxy-role"
        
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
        
        try:
            # Create role
            print(f"Creating IAM role: {role_name}")
            role_response = self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description="Execution role for TACNode MCP proxy Lambda"
            )
            
            role_arn = role_response['Role']['Arn']
            print(f"✅ Role created: {role_arn}")
            
            # Attach basic Lambda execution policy
            print("Attaching Lambda execution policy...")
            self.iam_client.attach_role_policy(
                RoleName=role_name,
                PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
            )
            
            print("✅ Lambda execution role ready")
            return role_arn
            
        except self.iam_client.exceptions.EntityAlreadyExistsException:
            print(f"✅ Role {role_name} already exists")
            role_response = self.iam_client.get_role(RoleName=role_name)
            return role_response['Role']['Arn']
    
    def create_lambda_function_code(self):
        """Create real Lambda function code"""
        print("\n📋 STEP 2: Creating Lambda Function Code")
        print("-" * 50)
        
        lambda_code = '''import json
import urllib3
import os

def lambda_handler(event, context):
    """REAL Lambda proxy for TACNode MCP calls"""
    
    tacnode_token = os.environ['TACNODE_TOKEN']
    tacnode_url = "https://mcp-server.tacnode.io/mcp"
    
    try:
        # Extract MCP request from AgentCore Gateway
        if 'body' in event:
            if isinstance(event['body'], str):
                mcp_request = json.loads(event['body'])
            else:
                mcp_request = event['body']
        else:
            mcp_request = event
        
        print(f"Received MCP request: {json.dumps(mcp_request)}")
        
        # Create HTTP client
        http = urllib3.PoolManager()
        
        # Forward to TACNode MCP server
        response = http.request(
            'POST',
            tacnode_url,
            body=json.dumps(mcp_request),
            headers={
                'Authorization': f'Bearer {tacnode_token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json, text/event-stream'
            }
        )
        
        print(f"TACNode response status: {response.status}")
        
        if response.status == 200:
            # Parse SSE response from TACNode
            response_text = response.data.decode('utf-8').strip()
            print(f"TACNode response: {response_text[:200]}...")
            
            if response_text.startswith('event: message\\ndata: '):
                json_data = response_text.replace('event: message\\ndata: ', '')
                result = json.loads(json_data)
                
                print(f"Parsed result: {json.dumps(result)}")
                
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json'
                    },
                    'body': json.dumps(result)
                }
            else:
                print(f"Unexpected response format: {response_text[:100]}")
                return {
                    'statusCode': 500,
                    'body': json.dumps({'error': 'Invalid TACNode response format'})
                }
        else:
            error_msg = f'TACNode error: {response.status} - {response.data.decode("utf-8")}'
            print(f"TACNode error: {error_msg}")
            return {
                'statusCode': response.status,
                'body': json.dumps({'error': error_msg})
            }
            
    except Exception as e:
        print(f"Lambda error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
'''
        
        # Save Lambda code
        with open('lambda_function.py', 'w') as f:
            f.write(lambda_code)
        
        # Create deployment package
        print("Creating deployment package...")
        with zipfile.ZipFile('tacnode-mcp-proxy.zip', 'w') as zip_file:
            zip_file.write('lambda_function.py')
        
        print("✅ Lambda function code created")
        print("   File: lambda_function.py")
        print("   Package: tacnode-mcp-proxy.zip")
        
        return True
    
    def deploy_lambda_function(self, role_arn):
        """Deploy real Lambda function"""
        print("\n📋 STEP 3: Deploying Lambda Function")
        print("-" * 50)
        
        function_name = "tacnode-mcp-proxy"
        
        try:
            # Read deployment package
            with open('tacnode-mcp-proxy.zip', 'rb') as zip_file:
                zip_content = zip_file.read()
            
            print(f"Deploying Lambda function: {function_name}")
            print(f"Role ARN: {role_arn}")
            print(f"Package size: {len(zip_content)} bytes")
            
            # Wait for role to be ready
            print("Waiting for IAM role to be ready...")
            time.sleep(10)
            
            # Create Lambda function
            response = self.lambda_client.create_function(
                FunctionName=function_name,
                Runtime='python3.9',
                Role=role_arn,
                Handler='lambda_function.lambda_handler',
                Code={'ZipFile': zip_content},
                Description='REAL MCP proxy for TACNode Context Lake',
                Timeout=60,
                Environment={
                    'Variables': {
                        'TACNODE_TOKEN': self.tacnode_token
                    }
                }
            )
            
            function_arn = response['FunctionArn']
            print(f"✅ Lambda function deployed: {function_arn}")
            
            # Save function info
            function_info = {
                "functionName": function_name,
                "functionArn": function_arn,
                "role": role_arn,
                "runtime": "python3.9",
                "handler": "lambda_function.lambda_handler",
                "deployed": datetime.now().isoformat()
            }
            
            with open('tacnode-mcp-proxy-function.json', 'w') as f:
                json.dump(function_info, f, indent=2)
            
            return function_info
            
        except self.lambda_client.exceptions.ResourceConflictException:
            print(f"✅ Lambda function {function_name} already exists")
            
            # Update existing function
            print("Updating function code...")
            self.lambda_client.update_function_code(
                FunctionName=function_name,
                ZipFile=zip_content
            )
            
            # Update environment variables
            print("Updating environment variables...")
            self.lambda_client.update_function_configuration(
                FunctionName=function_name,
                Environment={
                    'Variables': {
                        'TACNODE_TOKEN': self.tacnode_token
                    }
                }
            )
            
            # Get function info
            response = self.lambda_client.get_function(FunctionName=function_name)
            function_arn = response['Configuration']['FunctionArn']
            
            function_info = {
                "functionName": function_name,
                "functionArn": function_arn,
                "role": role_arn,
                "runtime": "python3.9",
                "handler": "lambda_function.lambda_handler",
                "updated": datetime.now().isoformat()
            }
            
            with open('tacnode-mcp-proxy-function.json', 'w') as f:
                json.dump(function_info, f, indent=2)
            
            return function_info
    
    def test_lambda_function(self, function_info):
        """Test real Lambda function"""
        print("\n📋 STEP 4: Testing Lambda Function")
        print("-" * 50)
        
        # Test MCP request
        test_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "query",
                "arguments": {
                    "sql": "SELECT COUNT(*) as record_count FROM test WHERE is_active = true"
                }
            }
        }
        
        print(f"Testing with MCP request: {json.dumps(test_request)}")
        
        try:
            # Invoke Lambda function
            response = self.lambda_client.invoke(
                FunctionName=function_info['functionName'],
                Payload=json.dumps(test_request)
            )
            
            # Parse response
            response_payload = json.loads(response['Payload'].read())
            print(f"Lambda response: {json.dumps(response_payload, indent=2)}")
            
            if response_payload.get('statusCode') == 200:
                body = json.loads(response_payload['body'])
                print("✅ Lambda function test SUCCESS!")
                print(f"   MCP response received from TACNode")
                print(f"   Data: {body}")
                return True
            else:
                print(f"❌ Lambda function test FAILED: {response_payload}")
                return False
                
        except Exception as e:
            print(f"❌ Lambda test error: {e}")
            return False
    
    def create_gateway_target(self, function_info):
        """Create real AgentCore Gateway target"""
        print("\n📋 STEP 5: Creating AgentCore Gateway Target")
        print("-" * 50)
        
        try:
            # Gateway target configuration
            target_config = {
                "type": "LAMBDA",
                "lambdaConfiguration": {
                    "functionArn": function_info['functionArn']
                }
            }
            
            print(f"Gateway ID: {self.gateway_id}")
            print(f"Target configuration: {json.dumps(target_config, indent=2)}")
            
            # Create gateway target
            response = self.bedrock_agentcore.create_gateway_target(
                gatewayIdentifier=self.gateway_id,
                name='tacnode-mcp-proxy',
                targetConfiguration=target_config
            )
            
            target_id = response['targetId']
            print(f"✅ Gateway target created: {target_id}")
            
            # Save target info
            target_info = {
                "targetName": "tacnode-mcp-proxy",
                "targetId": target_id,
                "gatewayId": self.gateway_id,
                "lambdaFunction": function_info['functionArn'],
                "created": datetime.now().isoformat()
            }
            
            with open('tacnode-gateway-target.json', 'w') as f:
                json.dump(target_info, f, indent=2)
            
            return target_info
            
        except Exception as e:
            print(f"❌ Gateway target creation failed: {e}")
            return None
    
    def deploy_complete_system(self):
        """Deploy complete real system"""
        print("🚀 DEPLOYING COMPLETE REAL AGENTCORE GATEWAY MCP SYSTEM")
        print("=" * 70)
        print("🚫 NO SHORTCUTS - Implementing REAL integration!")
        
        # Step 1: Create IAM role
        role_arn = self.create_lambda_execution_role()
        
        # Step 2: Create Lambda code
        self.create_lambda_function_code()
        
        # Step 3: Deploy Lambda function
        function_info = self.deploy_lambda_function(role_arn)
        
        # Step 4: Test Lambda function
        if not self.test_lambda_function(function_info):
            print("❌ Lambda test failed - stopping deployment")
            return False
        
        # Step 5: Create gateway target
        target_info = self.create_gateway_target(function_info)
        if not target_info:
            print("❌ Gateway target creation failed")
            return False
        
        print("\n🎉 REAL AGENTCORE GATEWAY MCP SYSTEM DEPLOYED!")
        print("=" * 70)
        print("✅ Lambda MCP Proxy: Deployed and tested")
        print("✅ AgentCore Gateway Target: Created")
        print("✅ Complete Flow: Runtime → Gateway → Lambda → TACNode")
        print("🚫 NO SIMULATION - Everything is REAL!")
        
        print(f"\n📊 DEPLOYMENT SUMMARY:")
        print(f"   Lambda Function: {function_info['functionName']}")
        print(f"   Gateway Target: {target_info['targetName']}")
        print(f"   Gateway ID: {target_info['gatewayId']}")
        print(f"   Target ID: {target_info['targetId']}")
        
        return True

def main():
    print("🚀 REAL Lambda MCP Proxy Deployment")
    print("🚫 NO SHORTCUTS - Implementing REAL gateway integration!")
    print("=" * 70)
    
    try:
        deployer = RealLambdaMCPProxyDeployer()
        success = deployer.deploy_complete_system()
        
        if success:
            print("\n✅ DEPLOYMENT SUCCESSFUL!")
            print("   Ready for real AgentCore Gateway integration")
        else:
            print("\n❌ DEPLOYMENT FAILED!")
            print("   Check logs and retry")
            
    except Exception as e:
        print(f"❌ Deployment error: {e}")

if __name__ == "__main__":
    main()

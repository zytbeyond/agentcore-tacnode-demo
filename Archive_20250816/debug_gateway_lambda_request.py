#!/usr/bin/env python3
"""
Debug the Gateway → Lambda request format and fix the issue
"""

import boto3
import json

def debug_gateway_lambda_request():
    """Debug what the Gateway is sending to Lambda"""
    print("🔍 DEBUGGING GATEWAY → LAMBDA REQUEST FORMAT")
    print("=" * 70)
    
    # Load Lambda configuration
    try:
        with open('augment-lambda-tacnode-config.json', 'r') as f:
            lambda_config = json.load(f)
        
        function_name = lambda_config['lambda']['functionName']
        print(f"✅ Lambda Function: {function_name}")
        
    except FileNotFoundError:
        print("❌ Lambda configuration not found.")
        return False
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    # Test what Gateway sends to Lambda
    print(f"\n📋 TESTING GATEWAY → LAMBDA REQUEST FORMAT")
    print("-" * 50)
    
    # This is what the Gateway sends to Lambda (based on the error response)
    gateway_to_lambda_request = {
        "name": "augment-lambda-tacnode-target___query",
        "arguments": {
            "sql": "SELECT 'DEBUG_TEST' as test_type, NOW() as timestamp FROM test LIMIT 1"
        }
    }
    
    print(f"🌐 Gateway sends this to Lambda:")
    print(f"   {json.dumps(gateway_to_lambda_request, indent=2)}")
    
    # Test Lambda with Gateway format
    try:
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(gateway_to_lambda_request)
        )
        
        if response['StatusCode'] == 200:
            lambda_response = json.loads(response['Payload'].read())
            print(f"\n📡 Lambda Response to Gateway format:")
            print(f"   {json.dumps(lambda_response, indent=2)}")
            
            # Check if this is the 400 error we're seeing
            if lambda_response.get('statusCode') == 400:
                print(f"\n❌ FOUND THE PROBLEM!")
                print(f"   Lambda is receiving Gateway format but expecting JSON-RPC format")
                print(f"   Need to update Lambda to handle Gateway's request format")
                return True
        else:
            print(f"❌ Lambda invocation failed: {response['StatusCode']}")
            
    except Exception as e:
        print(f"❌ Lambda test failed: {e}")
    
    return False

def create_fixed_lambda_function():
    """Create updated Lambda function that handles Gateway requests correctly"""
    print(f"\n🔧 CREATING FIXED LAMBDA FUNCTION")
    print("-" * 50)
    
    # Load TACNode token
    try:
        with open('tacnode_token.txt', 'r') as f:
            tacnode_token = f.read().strip()
        print(f"✅ TACNode token loaded")
    except FileNotFoundError:
        print("❌ TACNode token not found")
        return False
    
    # Fixed Lambda code that handles both Gateway and direct JSON-RPC formats
    fixed_lambda_code = f'''
import json
import urllib3
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# TACNode configuration
TACNODE_URL = "https://mcp-server.tacnode.io/mcp"
TACNODE_TOKEN = "{tacnode_token}"

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
                logger.error(f"Failed to parse JSON: {{e}}")
                logger.error(f"Raw data: {{json_data}}")
                return None
    
    return None

def lambda_handler(event, context):
    """Lambda handler that handles both Gateway and direct JSON-RPC requests"""
    
    logger.info(f"Received event: {{json.dumps(event)}}")
    
    try:
        # Determine request format and convert to TACNode JSON-RPC format
        if 'name' in event and 'arguments' in event:
            # Gateway format: {{"name": "tool_name", "arguments": {{"sql": "..."}}}}
            logger.info("Detected Gateway request format")
            
            tool_name = event['name']
            arguments = event['arguments']
            
            # Extract actual tool name (remove target prefix)
            actual_tool_name = tool_name.split('___')[-1] if '___' in tool_name else tool_name
            
            # Convert to TACNode JSON-RPC format
            tacnode_request = {{
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {{
                    "name": actual_tool_name,
                    "arguments": arguments
                }},
                "id": 1
            }}
            
            logger.info(f"Converted to TACNode format: {{json.dumps(tacnode_request)}}")
            
        elif 'jsonrpc' in event:
            # Direct JSON-RPC format
            logger.info("Detected direct JSON-RPC request format")
            tacnode_request = event
            
        else:
            # Try to extract from body if it's an HTTP request
            if 'body' in event:
                if isinstance(event['body'], str):
                    request_body = json.loads(event['body'])
                else:
                    request_body = event['body']
                
                if 'name' in request_body and 'arguments' in request_body:
                    # Gateway format in body
                    tool_name = request_body['name']
                    arguments = request_body['arguments']
                    actual_tool_name = tool_name.split('___')[-1] if '___' in tool_name else tool_name
                    
                    tacnode_request = {{
                        "jsonrpc": "2.0",
                        "method": "tools/call",
                        "params": {{
                            "name": actual_tool_name,
                            "arguments": arguments
                        }},
                        "id": 1
                    }}
                else:
                    tacnode_request = request_body
            else:
                logger.error("Unknown request format")
                return {{
                    'statusCode': 400,
                    'headers': {{'Content-Type': 'application/json'}},
                    'body': json.dumps({{
                        'jsonrpc': '2.0',
                        'error': {{
                            'code': -32600,
                            'message': 'Invalid request format'
                        }},
                        'id': 1
                    }})
                }}
        
        logger.info(f"Final TACNode request: {{json.dumps(tacnode_request)}}")
        
        # Prepare headers for TACNode
        headers = {{
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream',
            'Authorization': f'Bearer {{TACNODE_TOKEN}}'
        }}
        
        # Create HTTP client
        http = urllib3.PoolManager()
        
        # Make request to TACNode
        response = http.request(
            'POST',
            TACNODE_URL,
            body=json.dumps(tacnode_request),
            headers=headers,
            timeout=30
        )
        
        logger.info(f"TACNode response status: {{response.status}}")
        logger.info(f"TACNode response headers: {{dict(response.headers)}}")
        
        if response.status == 200:
            response_text = response.data.decode('utf-8')
            logger.info(f"TACNode raw response: {{response_text}}")
            
            # Check if it's SSE response
            if 'text/event-stream' in response.headers.get('content-type', ''):
                # Parse SSE response
                parsed_response = parse_sse_response(response_text)
                
                if parsed_response:
                    logger.info(f"Parsed SSE response: {{json.dumps(parsed_response)}}")
                    
                    # Return clean JSON response for AgentCore Gateway
                    return {{
                        'statusCode': 200,
                        'headers': {{
                            'Content-Type': 'application/json'
                        }},
                        'body': json.dumps(parsed_response)
                    }}
                else:
                    logger.error("Failed to parse SSE response")
                    return {{
                        'statusCode': 500,
                        'headers': {{
                            'Content-Type': 'application/json'
                        }},
                        'body': json.dumps({{
                            'jsonrpc': '2.0',
                            'error': {{
                                'code': -32603,
                                'message': 'Failed to parse TACNode SSE response'
                            }},
                            'id': tacnode_request.get('id', 1)
                        }})
                    }}
            else:
                # Regular JSON response
                try:
                    json_response = json.loads(response_text)
                    return {{
                        'statusCode': 200,
                        'headers': {{
                            'Content-Type': 'application/json'
                        }},
                        'body': json.dumps(json_response)
                    }}
                except json.JSONDecodeError:
                    return {{
                        'statusCode': 200,
                        'headers': {{
                            'Content-Type': 'application/json'
                        }},
                        'body': response_text
                    }}
        else:
            logger.error(f"TACNode error: {{response.status}} - {{response.data.decode('utf-8')}}")
            return {{
                'statusCode': response.status,
                'headers': {{
                    'Content-Type': 'application/json'
                }},
                'body': json.dumps({{
                    'jsonrpc': '2.0',
                    'error': {{
                        'code': -32603,
                        'message': f'TACNode request failed: {{response.status}}'
                    }},
                    'id': tacnode_request.get('id', 1)
                }})
            }}
            
    except Exception as e:
        logger.error(f"Lambda error: {{str(e)}}")
        return {{
            'statusCode': 500,
            'headers': {{
                'Content-Type': 'application/json'
            }},
            'body': json.dumps({{
                'jsonrpc': '2.0',
                'error': {{
                    'code': -32603,
                    'message': f'Lambda proxy error: {{str(e)}}'
                }},
                'id': 1
            }})
        }}
'''
    
    # Update the Lambda function
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    try:
        with open('augment-lambda-tacnode-config.json', 'r') as f:
            lambda_config = json.load(f)
        
        function_name = lambda_config['lambda']['functionName']
        
        print(f"📋 Updating Lambda function: {function_name}")
        
        # Update function code
        update_response = lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=create_lambda_zip(fixed_lambda_code)
        )
        
        print(f"✅ Lambda function updated successfully")
        print(f"✅ New version: {update_response['Version']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating Lambda function: {e}")
        return False

def create_lambda_zip(lambda_code):
    """Create ZIP file for Lambda deployment"""
    import zipfile
    import io
    
    # Create in-memory ZIP file
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', lambda_code)
    
    zip_buffer.seek(0)
    return zip_buffer.read()

def test_fixed_lambda():
    """Test the fixed Lambda function with Gateway format"""
    print(f"\n🧪 TESTING FIXED LAMBDA FUNCTION")
    print("-" * 50)
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    try:
        with open('augment-lambda-tacnode-config.json', 'r') as f:
            lambda_config = json.load(f)
        
        function_name = lambda_config['lambda']['functionName']
        
        # Test with Gateway format
        gateway_request = {
            "name": "augment-lambda-tacnode-target___query",
            "arguments": {
                "sql": "SELECT 'FIXED_LAMBDA_TEST' as test_type, 'GATEWAY_FORMAT' as format_type, NOW() as timestamp, COUNT(*) as record_count FROM test"
            }
        }
        
        print(f"📋 Testing with Gateway format:")
        print(f"   {json.dumps(gateway_request, indent=2)}")
        
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(gateway_request)
        )
        
        if response['StatusCode'] == 200:
            lambda_response = json.loads(response['Payload'].read())
            print(f"\n📡 Fixed Lambda Response:")
            print(f"   Status: {lambda_response.get('statusCode', 'Unknown')}")
            print(f"   Response: {json.dumps(lambda_response, indent=2)}")
            
            if lambda_response.get('statusCode') == 200:
                body = json.loads(lambda_response['body'])
                if 'result' in body and not body['result'].get('isError', False):
                    content = body['result'].get('content', [])
                    if content and len(content) > 0:
                        text_content = content[0].get('text', '')
                        print(f"\n✅ LAMBDA FIX SUCCESSFUL!")
                        print(f"   Database response: {text_content}")
                        
                        try:
                            if text_content.startswith('[') and text_content.endswith(']'):
                                records = json.loads(text_content)
                                for record in records:
                                    for key, value in record.items():
                                        print(f"     {key}: {value}")
                        except json.JSONDecodeError:
                            pass
                        
                        return True
            else:
                print(f"❌ Lambda still returning error: {lambda_response}")
        else:
            print(f"❌ Lambda invocation failed: {response['StatusCode']}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    return False

def main():
    """Main debug and fix function"""
    print("🔧 DEBUGGING AND FIXING GATEWAY → LAMBDA → TACNODE")
    print("=" * 70)
    print("🎯 Step 1: Debug Gateway → Lambda request format")
    print("🎯 Step 2: Fix Lambda to handle Gateway format")
    print("🎯 Step 3: Test fixed Lambda function")
    
    # Step 1: Debug the issue
    debug_success = debug_gateway_lambda_request()
    
    if debug_success:
        # Step 2: Fix Lambda function
        fix_success = create_fixed_lambda_function()
        
        if fix_success:
            # Step 3: Test fixed Lambda
            test_success = test_fixed_lambda()
            
            if test_success:
                print(f"\n🎉 GATEWAY → LAMBDA → TACNODE FIX COMPLETE!")
                print(f"✅ Lambda now handles Gateway request format correctly")
                print(f"✅ Ready to test real Gateway → Lambda → TACNode flow")
                return True
    
    print(f"\n❌ FAILED TO FIX GATEWAY → LAMBDA → TACNODE")
    return False

if __name__ == "__main__":
    main()

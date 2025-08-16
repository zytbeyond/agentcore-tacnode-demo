#!/usr/bin/env python3
"""
Update the Lambda function to correctly handle AgentCore Gateway requests
"""

import boto3
import json
import zipfile
import io

def create_updated_lambda_code():
    """Create the updated Lambda function code that handles AgentCore Gateway format"""
    lambda_code = '''
import json
import urllib3
import os

def lambda_handler(event, context):
    """
    Lambda function to bridge AgentCore Gateway requests to TACNode
    Handles the specific format that AgentCore Gateway sends
    """
    
    print(f"🔍 Received event: {json.dumps(event, indent=2)}")
    
    # Get TACNode token from environment
    tacnode_token = os.environ.get('TACNODE_TOKEN')
    if not tacnode_token:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'TACNode token not configured',
                'isError': True
            })
        }
    
    try:
        # AgentCore Gateway sends the SQL parameter directly
        # Check if this is a direct SQL parameter from AgentCore Gateway
        if 'sql' in event and isinstance(event['sql'], str):
            sql_query = event['sql']
            print(f"📝 Detected AgentCore Gateway SQL request: {sql_query}")
            
            # Create JSON-RPC request for TACNode
            tacnode_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "query",
                    "arguments": {
                        "sql": sql_query
                    }
                },
                "id": 1
            }
        else:
            # Handle other request formats (for backward compatibility)
            # Extract the request from the event
            if 'body' in event:
                if isinstance(event['body'], str):
                    request_body = json.loads(event['body'])
                else:
                    request_body = event['body']
            else:
                request_body = event
            
            print(f"📝 Parsed request body: {json.dumps(request_body, indent=2)}")
            
            # Transform to TACNode JSON-RPC format
            if request_body.get('method') == 'tools/call':
                # Extract SQL query from the request
                params = request_body.get('params', {})
                tool_name = params.get('name', '')
                arguments = params.get('arguments', {})
                
                if tool_name == 'query' and 'sql' in arguments:
                    sql_query = arguments['sql']
                    
                    # Create JSON-RPC request for TACNode
                    tacnode_request = {
                        "jsonrpc": "2.0",
                        "method": "tools/call",
                        "params": {
                            "name": "query",
                            "arguments": {
                                "sql": sql_query
                            }
                        },
                        "id": request_body.get('id', 1)
                    }
                else:
                    # Handle other tool calls or list tools
                    tacnode_request = {
                        "jsonrpc": "2.0",
                        "method": request_body.get('method', 'tools/list'),
                        "params": request_body.get('params', {}),
                        "id": request_body.get('id', 1)
                    }
            else:
                # Pass through other requests (like tools/list)
                tacnode_request = {
                    "jsonrpc": "2.0",
                    "method": request_body.get('method', 'tools/list'),
                    "params": request_body.get('params', {}),
                    "id": request_body.get('id', 1)
                }
        
        print(f"🚀 Sending to TACNode: {json.dumps(tacnode_request, indent=2)}")
        
        # Make request to TACNode
        http = urllib3.PoolManager()
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream',
            'Authorization': f'Bearer {tacnode_token}'
        }
        
        response = http.request(
            'POST',
            'https://mcp-server.tacnode.io/mcp',
            body=json.dumps(tacnode_request),
            headers=headers
        )
        
        print(f"📥 TACNode response status: {response.status}")
        print(f"📥 TACNode response data: {response.data.decode('utf-8')}")
        
        if response.status == 200:
            # Parse the response - TACNode returns event-stream format
            response_text = response.data.decode('utf-8')
            
            # Handle event-stream format
            if response_text.startswith('event: message'):
                lines = response_text.strip().split('\\n')
                for line in lines:
                    if line.startswith('data: '):
                        data_json = line[6:]  # Remove 'data: ' prefix
                        tacnode_response = json.loads(data_json)
                        break
            else:
                # Direct JSON response
                tacnode_response = json.loads(response_text)
            
            print(f"✅ Parsed TACNode response: {json.dumps(tacnode_response, indent=2)}")
            
            # Return the response in the format expected by AgentCore Gateway
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps(tacnode_response)
            }
        else:
            error_response = {
                'jsonrpc': '2.0',
                'error': {
                    'code': response.status,
                    'message': f'TACNode request failed: {response.data.decode("utf-8")}'
                },
                'id': tacnode_request.get('id', 1)
            }
            
            return {
                'statusCode': response.status,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps(error_response)
            }
            
    except Exception as e:
        print(f"❌ Error in Lambda: {str(e)}")
        error_response = {
            'jsonrpc': '2.0',
            'error': {
                'code': -32603,
                'message': f'Internal error: {str(e)}'
            },
            'id': 1
        }
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps(error_response)
        }
'''
    
    # Create a zip file with the Lambda code
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', lambda_code)
    
    return zip_buffer.getvalue()

def update_lambda_function():
    """Update the Lambda function with the corrected code"""
    print("🔧 UPDATING LAMBDA FUNCTION FOR AGENTCORE GATEWAY")
    print("=" * 60)
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    function_name = "augment-tacnode-bridge"
    
    try:
        # Update function code
        print("📝 Updating Lambda function code...")
        lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=create_updated_lambda_code()
        )
        
        print("✅ Lambda function updated successfully!")
        print("🔧 The function now correctly handles AgentCore Gateway requests")
        
        # Wait for update to complete
        print("⏳ Waiting for update to complete...")
        import time
        time.sleep(5)
        
        print("✅ Lambda function is ready for testing!")
        
    except Exception as e:
        print(f"❌ Error updating Lambda function: {e}")

if __name__ == "__main__":
    update_lambda_function()

import json
import urllib3
import os

def lambda_handler(event, context):
    """Translate MCP calls to TACNode API calls"""
    
    tacnode_token = os.environ['TACNODE_TOKEN']
    
    try:
        # Extract MCP request
        if 'body' in event:
            if isinstance(event['body'], str):
                mcp_request = json.loads(event['body'])
            else:
                mcp_request = event['body']
        else:
            mcp_request = event
        
        print(f"Received MCP request: {json.dumps(mcp_request)}")
        
        # Extract method and params
        method = mcp_request.get('method')
        params = mcp_request.get('params', {})
        request_id = mcp_request.get('id', 1)
        
        # Create HTTP client
        http = urllib3.PoolManager()
        
        if method == "tools/call":
            # Handle tools/call - translate to API calls
            tool_name = params.get('name')
            arguments = params.get('arguments', {})
            
            if tool_name == "executeQuery":
                # Execute SQL query via TACNode API
                sql = arguments.get('sql')
                
                # Call TACNode MCP endpoint (since TACNode only provides MCP, not separate API)
                mcp_url = "https://mcp-server.tacnode.io/mcp"
                mcp_payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": "query",
                        "arguments": {"sql": sql}
                    }
                }
                
                response = http.request(
                    'POST',
                    mcp_url,
                    body=json.dumps(mcp_payload),
                    headers={
                        'Authorization': f'Bearer {tacnode_token}',
                        'Content-Type': 'application/json',
                        'Accept': 'application/json, text/event-stream'
                    }
                )
                
                if response.status == 200:
                    # Parse TACNode MCP response (handles SSE format)
                    response_text = response.data.decode('utf-8').strip()

                    if response_text.startswith('event: message\ndata: '):
                        # Parse SSE format
                        json_data = response_text.replace('event: message\ndata: ', '')
                        tacnode_mcp_response = json.loads(json_data)
                    else:
                        # Parse direct JSON
                        tacnode_mcp_response = json.loads(response_text)

                    # Forward TACNode MCP response
                    if 'result' in tacnode_mcp_response:
                        mcp_response = {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": tacnode_mcp_response['result']
                        }
                    else:
                        # Forward error from TACNode
                        mcp_response = tacnode_mcp_response
                    
                    return {
                        'statusCode': 200,
                        'headers': {'Content-Type': 'application/json'},
                        'body': json.dumps(mcp_response)
                    }
                else:
                    error_msg = f'TACNode MCP error: {response.status} - {response.data.decode("utf-8")}'
                    mcp_error = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32000,
                            "message": error_msg
                        }
                    }
                    return {
                        'statusCode': 200,
                        'headers': {'Content-Type': 'application/json'},
                        'body': json.dumps(mcp_error)
                    }
            
            elif tool_name == "listSchemas":
                # List schemas via TACNode API
                api_url = "https://api.tacnode.io/schemas"
                
                response = http.request(
                    'GET',
                    api_url,
                    headers={
                        'Authorization': f'Bearer {tacnode_token}',
                        'Content-Type': 'application/json'
                    }
                )
                
                if response.status == 200:
                    api_result = json.loads(response.data.decode('utf-8'))
                    
                    mcp_response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": json.dumps(api_result)
                                }
                            ],
                            "isError": False
                        }
                    }
                    
                    return {
                        'statusCode': 200,
                        'headers': {'Content-Type': 'application/json'},
                        'body': json.dumps(mcp_response)
                    }
        
        # Default response for unsupported methods
        mcp_error = {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}"
            }
        }
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(mcp_error)
        }
            
    except Exception as e:
        print(f"Lambda error: {str(e)}")
        mcp_error = {
            "jsonrpc": "2.0",
            "id": 1,
            "error": {
                "code": -32603,
                "message": str(e)
            }
        }
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(mcp_error)
        }

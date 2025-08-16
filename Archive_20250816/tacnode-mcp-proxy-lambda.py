
import json
import httpx
import asyncio
import os

async def lambda_handler(event, context):
    """Lambda proxy for TACNode MCP calls"""
    
    tacnode_token = os.environ['TACNODE_TOKEN']
    tacnode_url = "https://mcp-server.tacnode.io/mcp"
    
    try:
        # Extract MCP request from AgentCore Gateway
        mcp_request = json.loads(event['body'])
        
        # Forward to TACNode MCP server
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                tacnode_url,
                json=mcp_request,
                headers={
                    "Authorization": f"Bearer {tacnode_token}",
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream"
                }
            )
            
            if response.status_code == 200:
                # Parse SSE response
                response_text = response.text.strip()
                if response_text.startswith('event: message\ndata: '):
                    json_data = response_text.replace('event: message\ndata: ', '')
                    result = json.loads(json_data)
                    
                    return {
                        'statusCode': 200,
                        'headers': {'Content-Type': 'application/json'},
                        'body': json.dumps(result)
                    }
                else:
                    return {
                        'statusCode': 500,
                        'body': json.dumps({'error': 'Invalid TACNode response format'})
                    }
            else:
                return {
                    'statusCode': response.status_code,
                    'body': json.dumps({'error': f'TACNode error: {response.text}'})
                }
                
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

# Sync wrapper for Lambda
def lambda_handler(event, context):
    return asyncio.run(lambda_handler_async(event, context))

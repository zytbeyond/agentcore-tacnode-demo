#!/usr/bin/env python3
"""
Update Lambda function to log exact messages received from Gateway and sent to TACNode
"""

import boto3
import json

def get_tacnode_token():
    """Get TACNode token"""
    try:
        with open('tacnode_token.txt', 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def create_lambda_with_message_logging():
    """Create Lambda function that logs all real messages"""
    
    tacnode_token = get_tacnode_token()
    if not tacnode_token:
        print("❌ TACNode token not found")
        return False
    
    # Lambda code with detailed message logging
    lambda_code_with_logging = f'''
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
            json_data = line[6:]  # Remove 'data: ' prefix
            try:
                return json.loads(json_data)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON: {{e}}")
                return None
    
    return None

def lambda_handler(event, context):
    """Lambda handler with REAL MESSAGE LOGGING"""
    
    # LOG EXACT MESSAGE RECEIVED FROM AGENTCORE GATEWAY
    logger.info("=" * 80)
    logger.info("🔍 REAL MESSAGE RECEIVED FROM AGENTCORE GATEWAY:")
    logger.info(f"Raw event: {{json.dumps(event, indent=2)}}")
    logger.info("=" * 80)
    
    try:
        # Handle Gateway format: {{"sql": "SELECT ..."}}
        if 'sql' in event and isinstance(event['sql'], str):
            logger.info("✅ Detected Gateway direct SQL format")
            
            # Convert Gateway format to TACNode JSON-RPC format
            tacnode_request = {{
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {{
                    "name": "query",
                    "arguments": {{
                        "sql": event['sql']
                    }}
                }},
                "id": 1
            }}
            
            logger.info("✅ Converted Gateway format to TACNode JSON-RPC")
            
        elif 'jsonrpc' in event:
            logger.info("✅ Detected direct JSON-RPC format")
            tacnode_request = event
            
        else:
            logger.error(f"❌ Unknown request format from Gateway")
            return {{
                'statusCode': 400,
                'headers': {{'Content-Type': 'application/json'}},
                'body': json.dumps({{
                    'jsonrpc': '2.0',
                    'error': {{
                        'code': -32600,
                        'message': 'Invalid request format - expected SQL or JSON-RPC'
                    }},
                    'id': 1
                }})
            }}
        
        # LOG EXACT MESSAGE BEING SENT TO TACNODE
        logger.info("=" * 80)
        logger.info("🌐 REAL MESSAGE BEING SENT TO TACNODE:")
        logger.info(f"URL: {{TACNODE_URL}}")
        logger.info(f"Headers: Content-Type: application/json, Accept: application/json, text/event-stream, Authorization: Bearer [TOKEN]")
        logger.info(f"Body: {{json.dumps(tacnode_request, indent=2)}}")
        logger.info("=" * 80)
        
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
        
        # LOG EXACT RESPONSE RECEIVED FROM TACNODE
        logger.info("=" * 80)
        logger.info("📡 REAL RESPONSE RECEIVED FROM TACNODE:")
        logger.info(f"Status: {{response.status}}")
        logger.info(f"Headers: {{dict(response.headers)}}")
        
        if response.status == 200:
            response_text = response.data.decode('utf-8')
            logger.info(f"Raw response body: {{response_text}}")
            logger.info("=" * 80)
            
            # Check if it's SSE response
            if 'text/event-stream' in response.headers.get('content-type', ''):
                logger.info("✅ TACNode returned SSE response - parsing...")
                
                # Parse SSE response
                parsed_response = parse_sse_response(response_text)
                
                if parsed_response:
                    logger.info("=" * 80)
                    logger.info("🎉 PARSED SSE RESPONSE FROM TACNODE:")
                    logger.info(f"{{json.dumps(parsed_response, indent=2)}}")
                    logger.info("=" * 80)
                    
                    # LOG EXACT MESSAGE BEING SENT BACK TO GATEWAY
                    gateway_response = {{
                        'statusCode': 200,
                        'headers': {{
                            'Content-Type': 'application/json'
                        }},
                        'body': json.dumps(parsed_response)
                    }}
                    
                    logger.info("=" * 80)
                    logger.info("🔄 REAL MESSAGE BEING SENT BACK TO AGENTCORE GATEWAY:")
                    logger.info(f"{{json.dumps(gateway_response, indent=2)}}")
                    logger.info("=" * 80)
                    
                    return gateway_response
                else:
                    logger.error("❌ Failed to parse SSE response from TACNode")
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
                logger.info("✅ TACNode returned regular JSON response")
                try:
                    json_response = json.loads(response_text)
                    
                    gateway_response = {{
                        'statusCode': 200,
                        'headers': {{
                            'Content-Type': 'application/json'
                        }},
                        'body': json.dumps(json_response)
                    }}
                    
                    logger.info("=" * 80)
                    logger.info("🔄 REAL MESSAGE BEING SENT BACK TO AGENTCORE GATEWAY:")
                    logger.info(f"{{json.dumps(gateway_response, indent=2)}}")
                    logger.info("=" * 80)
                    
                    return gateway_response
                except json.JSONDecodeError:
                    return {{
                        'statusCode': 200,
                        'headers': {{
                            'Content-Type': 'application/json'
                        }},
                        'body': response_text
                    }}
        else:
            error_text = response.data.decode('utf-8')
            logger.error(f"❌ TACNode error: {{response.status}} - {{error_text}}")
            logger.info("=" * 80)
            
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
        logger.error(f"❌ Lambda error: {{str(e)}}")
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
    print("🔧 UPDATING LAMBDA WITH MESSAGE LOGGING")
    print("=" * 70)
    print("🎯 Lambda will now log:")
    print("   • Exact message received from AgentCore Gateway")
    print("   • Exact message sent to TACNode")
    print("   • Exact response received from TACNode")
    print("   • Exact message sent back to Gateway")
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    try:
        # Load secure Lambda configuration
        with open('secure-lambda-tacnode-config.json', 'r') as f:
            lambda_config = json.load(f)
        
        function_name = lambda_config['lambda']['functionName']
        
        print(f"📋 Updating Lambda function: {function_name}")
        
        # Create ZIP file for deployment
        import zipfile
        import io
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr('lambda_function.py', lambda_code_with_logging)
        zip_buffer.seek(0)
        
        # Update function code
        update_response = lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_buffer.read()
        )
        
        print(f"✅ Lambda function updated with message logging")
        print(f"✅ New version: {update_response['Version']}")
        print(f"✅ Lambda will now capture all real messages")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating Lambda function: {e}")
        return False

def main():
    """Main function"""
    print("🔍 LAMBDA MESSAGE LOGGING UPDATE")
    print("=" * 70)
    print("🎯 OBJECTIVE: Capture real messages flowing through Lambda")
    print("🎯 LOGGING: Gateway → Lambda, Lambda → TACNode, TACNode → Lambda, Lambda → Gateway")
    print("🎯 NO SIMULATION: All messages will be real and logged")
    
    success = create_lambda_with_message_logging()
    
    if success:
        print(f"\n🎉 LAMBDA MESSAGE LOGGING ENABLED!")
        print(f"✅ Lambda will now log all real messages")
        print(f"✅ Check CloudWatch Logs after next Gateway request")
        print(f"✅ Ready to capture real message flow")
        
        print(f"\n📋 NEXT STEPS:")
        print(f"   1. Send request to AgentCore Gateway")
        print(f"   2. Check Lambda CloudWatch Logs")
        print(f"   3. See exact messages received and sent")
    else:
        print(f"\n❌ FAILED TO ENABLE MESSAGE LOGGING")

if __name__ == "__main__":
    main()

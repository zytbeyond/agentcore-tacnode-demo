#!/usr/bin/env python3
"""
Test the Lambda function directly
"""

import boto3
import json
import base64

def test_lambda_function():
    """Test the Lambda function"""
    print("🧪 Testing Lambda MCP to API proxy function...")
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    # Test MCP request
    test_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "executeQuery",
            "arguments": {
                "sql": "SELECT COUNT(*) as record_count FROM test WHERE is_active = true"
            }
        }
    }
    
    print(f"Test payload: {json.dumps(test_payload, indent=2)}")
    
    try:
        # Invoke Lambda function
        response = lambda_client.invoke(
            FunctionName='tacnode-mcp-to-api-proxy',
            Payload=json.dumps(test_payload)
        )
        
        print(f"Lambda invoke response status: {response['StatusCode']}")
        
        # Read response payload
        response_payload = response['Payload'].read()
        
        if isinstance(response_payload, bytes):
            response_text = response_payload.decode('utf-8')
        else:
            response_text = str(response_payload)
        
        print(f"Lambda response payload: {response_text}")
        
        # Try to parse as JSON
        try:
            response_json = json.loads(response_text)
            print(f"Parsed response: {json.dumps(response_json, indent=2)}")
            
            if response_json.get('statusCode') == 200:
                body = json.loads(response_json['body'])
                print("✅ Lambda function test SUCCESS!")
                print(f"MCP response: {json.dumps(body, indent=2)}")
                return True
            else:
                print(f"❌ Lambda function returned error: {response_json}")
                return False
                
        except json.JSONDecodeError as e:
            print(f"❌ Could not parse Lambda response as JSON: {e}")
            print(f"Raw response: {response_text}")
            return False
            
    except Exception as e:
        print(f"❌ Lambda test error: {e}")
        return False

if __name__ == "__main__":
    test_lambda_function()

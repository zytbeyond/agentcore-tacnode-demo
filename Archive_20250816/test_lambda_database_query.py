#!/usr/bin/env python3
"""
Test the Lambda function with database queries
"""

import boto3
import json

def test_lambda_database_query():
    """Test Lambda function with database queries"""
    print("🧪 TESTING LAMBDA DATABASE QUERIES")
    print("=" * 70)
    
    # Load Lambda configuration
    try:
        with open('augment-lambda-tacnode-config.json', 'r') as f:
            config = json.load(f)
        
        function_name = config['lambda']['functionName']
        print(f"✅ Testing Lambda function: {function_name}")
        
    except FileNotFoundError:
        print("❌ Lambda configuration not found. Run lambda_tacnode_proxy.py first.")
        return
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    # Test queries
    test_queries = [
        {
            "name": "Count Records",
            "sql": "SELECT COUNT(*) as total_records FROM test"
        },
        {
            "name": "Sample Data",
            "sql": "SELECT 'LAMBDA_PROXY_SUCCESS' as status, 'SSE_TO_JSON' as conversion, NOW() as test_time, COUNT(*) as record_count FROM test LIMIT 3"
        },
        {
            "name": "Server Info",
            "sql": "SELECT version() as postgres_version, CURRENT_TIMESTAMP as server_time"
        }
    ]
    
    success_count = 0
    
    for i, test_query in enumerate(test_queries, 1):
        print(f"\n📋 TEST {i}: {test_query['name']}")
        print("-" * 50)
        print(f"SQL: {test_query['sql']}")
        
        # Create Lambda payload for database query
        lambda_payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "query",
                "arguments": {
                    "sql": test_query['sql']
                }
            },
            "id": i
        }
        
        try:
            # Invoke Lambda function
            response = lambda_client.invoke(
                FunctionName=function_name,
                InvocationType='RequestResponse',
                Payload=json.dumps(lambda_payload)
            )
            
            # Parse response
            response_payload = json.loads(response['Payload'].read())
            
            print(f"Lambda status: {response['StatusCode']}")
            
            if response['StatusCode'] == 200 and response_payload.get('statusCode') == 200:
                # Parse the body
                body = json.loads(response_payload['body'])
                
                if 'result' in body and not body['result'].get('isError', False):
                    content = body['result'].get('content', [])
                    if content and len(content) > 0:
                        text_content = content[0].get('text', '')
                        print(f"✅ Query successful!")
                        print(f"📊 Result: {text_content}")
                        
                        # Try to parse the JSON data
                        try:
                            if text_content.startswith('[') and text_content.endswith(']'):
                                data = json.loads(text_content)
                                if isinstance(data, list) and len(data) > 0:
                                    print(f"📊 Parsed data:")
                                    for record in data:
                                        for key, value in record.items():
                                            print(f"   {key}: {value}")
                        except:
                            print(f"📊 Raw data: {text_content}")
                        
                        success_count += 1
                    else:
                        print(f"❌ No content in result")
                else:
                    error_content = body['result'].get('content', [{}])[0].get('text', '')
                    print(f"❌ Query error: {error_content}")
            else:
                print(f"❌ Lambda error: {response_payload}")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    print(f"\n" + "=" * 70)
    print(f"📊 LAMBDA DATABASE TEST RESULTS: {success_count}/{len(test_queries)} successful")
    
    if success_count == len(test_queries):
        print(f"🎉 ALL LAMBDA DATABASE TESTS PASSED!")
        print(f"✅ Lambda proxy handles database queries perfectly")
        print(f"✅ SSE to JSON conversion working")
        print(f"✅ Real data retrieval working")
        print(f"✅ Ready for AgentCore Gateway integration")
        
        print(f"\n🌐 VERIFIED END-TO-END:")
        print("   Lambda → TACNode → PostgreSQL → SSE Response → JSON Conversion")
        print("   ✅ Complete data pipeline working")
        
        return True
    else:
        print(f"❌ Some tests failed")
        return False

def main():
    """Main test function"""
    print("🧪 LAMBDA DATABASE QUERY TEST")
    print("=" * 70)
    print("🎯 Testing Lambda proxy with real database queries")
    print("🎯 Verifying SSE to JSON conversion")
    print("🎯 Confirming end-to-end data pipeline")
    
    success = test_lambda_database_query()
    
    if success:
        print(f"\n🎯 NEXT STEP: Create AgentCore Gateway target pointing to Lambda")
    else:
        print(f"\n🔍 Check Lambda logs for debugging")

if __name__ == "__main__":
    main()

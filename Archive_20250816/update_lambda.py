#!/usr/bin/env python3
"""
Update Lambda function with corrected code
"""

import boto3
import zipfile
import json

def update_lambda():
    """Update the Lambda function"""
    print("🔄 Updating Lambda function with corrected code...")
    
    # Create deployment package
    with zipfile.ZipFile('tacnode-mcp-to-api-proxy-updated.zip', 'w') as zip_file:
        zip_file.write('mcp_to_api_lambda_function.py', 'lambda_function.py')
    
    print("✅ Deployment package created")
    
    # Update Lambda function
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    with open('tacnode-mcp-to-api-proxy-updated.zip', 'rb') as zip_file:
        zip_content = zip_file.read()
    
    try:
        response = lambda_client.update_function_code(
            FunctionName='tacnode-mcp-to-api-proxy',
            ZipFile=zip_content
        )
        
        print(f"✅ Lambda function updated: {response['FunctionName']}")
        print(f"   Last Modified: {response['LastModified']}")
        print(f"   Code SHA256: {response['CodeSha256']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Lambda update failed: {e}")
        return False

if __name__ == "__main__":
    update_lambda()

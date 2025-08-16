#!/usr/bin/env python3
"""
Fix Lambda Function URL access permissions
"""

import boto3
import json

def fix_lambda_url_access():
    """Fix Lambda Function URL access permissions"""
    print("🔧 FIXING LAMBDA FUNCTION URL ACCESS")
    print("=" * 70)
    
    # Load Lambda configuration
    try:
        with open('augment-lambda-tacnode-config.json', 'r') as f:
            config = json.load(f)
        
        function_name = config['lambda']['functionName']
        print(f"✅ Function name: {function_name}")
        
    except FileNotFoundError:
        print("❌ Lambda configuration not found.")
        return False
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    try:
        # Get current function URL config
        print(f"\n📋 Getting current Function URL configuration...")
        
        try:
            url_config = lambda_client.get_function_url_config(FunctionName=function_name)
            print(f"✅ Current URL: {url_config['FunctionUrl']}")
            print(f"✅ Current Auth Type: {url_config['AuthType']}")
        except Exception as e:
            print(f"❌ No Function URL exists: {e}")
            return False
        
        # Remove existing resource-based policy statements
        print(f"\n📋 Removing existing permissions...")
        
        try:
            lambda_client.remove_permission(
                FunctionName=function_name,
                StatementId='AllowPublicAccess'
            )
            print(f"✅ Removed old permission")
        except Exception as e:
            print(f"⚠️ No existing permission to remove: {e}")
        
        # Add comprehensive permission for Function URL
        print(f"\n📋 Adding comprehensive Function URL permission...")
        
        lambda_client.add_permission(
            FunctionName=function_name,
            StatementId='AllowFunctionUrlInvoke',
            Action='lambda:InvokeFunctionUrl',
            Principal='*',
            FunctionUrlAuthType='NONE'
        )
        
        print(f"✅ Added Function URL invoke permission")
        
        # Also add regular invoke permission
        try:
            lambda_client.add_permission(
                FunctionName=function_name,
                StatementId='AllowPublicInvoke',
                Action='lambda:InvokeFunction',
                Principal='*'
            )
            print(f"✅ Added general invoke permission")
        except Exception as e:
            print(f"⚠️ General invoke permission may already exist: {e}")
        
        # Get the Function URL again
        url_config = lambda_client.get_function_url_config(FunctionName=function_name)
        function_url = url_config['FunctionUrl']
        
        print(f"\n📋 Testing Lambda Function URL access...")
        
        # Test with a simple request
        import requests
        
        test_payload = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": 1
        }
        
        response = requests.post(
            function_url,
            json=test_payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"✅ Test response status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Lambda Function URL is now accessible!")
            print(f"✅ URL: {function_url}")
            
            # Update the configuration file
            config['gateway']['url'] = function_url
            config['access_fixed'] = True
            
            with open('augment-real-gateway-config.json', 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"✅ Configuration updated")
            return True
        else:
            print(f"❌ Still getting error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing Lambda URL access: {e}")
        return False

def main():
    """Main function"""
    print("🔧 LAMBDA FUNCTION URL ACCESS FIX")
    print("=" * 70)
    print("🎯 Fixing 403 Forbidden error on Lambda Function URL")
    
    success = fix_lambda_url_access()
    
    if success:
        print(f"\n🎉 LAMBDA URL ACCESS FIXED!")
        print(f"✅ Function URL is now publicly accessible")
        print(f"✅ Ready for real end-to-end testing")
    else:
        print(f"\n❌ FAILED TO FIX LAMBDA URL ACCESS")
        print(f"🔍 May need to check Lambda configuration manually")

if __name__ == "__main__":
    main()

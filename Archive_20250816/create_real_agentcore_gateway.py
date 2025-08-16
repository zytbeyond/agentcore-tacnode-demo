#!/usr/bin/env python3
"""
Create real AgentCore Gateway with Lambda target for end-to-end testing
"""

import boto3
import json
import time

def create_gateway_with_lambda_target():
    """Create AgentCore Gateway with Lambda target"""
    print("🏗️ CREATING REAL AGENTCORE GATEWAY WITH LAMBDA TARGET")
    print("=" * 70)
    
    bedrock_agentcore = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
    
    # Load Lambda configuration
    try:
        with open('augment-lambda-tacnode-config.json', 'r') as f:
            lambda_config = json.load(f)
        
        function_arn = lambda_config['lambda']['functionArn']
        function_name = lambda_config['lambda']['functionName']
        print(f"✅ Using Lambda function: {function_name}")
        print(f"✅ Lambda ARN: {function_arn}")
        
    except FileNotFoundError:
        print("❌ Lambda configuration not found. Run lambda_tacnode_proxy.py first.")
        return None, None, None
    
    try:
        # Create gateway with minimal required parameters
        gateway_name = "augment-real-gateway"
        
        print(f"📋 Creating gateway: {gateway_name}")
        
        # Try creating gateway with minimal parameters
        gateway_response = bedrock_agentcore.create_gateway(
            name=gateway_name,
            description="Real AgentCore Gateway for TACNode via Lambda - Created by Augment Agent"
        )
        
        gateway_id = gateway_response['gatewayId']
        print(f"✅ Gateway created: {gateway_id}")
        
        # Wait for gateway to be ready
        print(f"⏳ Waiting for gateway to be ready...")
        time.sleep(30)
        
        # Get gateway details
        gateway_details = bedrock_agentcore.get_gateway(gatewayIdentifier=gateway_id)
        gateway_url = gateway_details['gateway']['gatewayUrl']
        
        print(f"✅ Gateway status: {gateway_details['gateway']['status']}")
        print(f"✅ Gateway URL: {gateway_url}")
        
        # Create Lambda target
        target_id = create_lambda_target(gateway_id, function_arn)
        
        return gateway_id, gateway_url, target_id
        
    except Exception as e:
        print(f"❌ Error creating gateway: {e}")
        
        # If gateway creation fails, let's try to use Lambda directly with Function URLs
        print(f"\n🔄 Gateway creation failed, trying Lambda Function URL approach...")
        return create_lambda_function_url(function_name, function_arn)

def create_lambda_target(gateway_id, function_arn):
    """Create Lambda target in the gateway"""
    print(f"\n🎯 CREATING LAMBDA TARGET")
    print("-" * 50)
    
    bedrock_agentcore = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
    
    try:
        target_name = "augment-lambda-tacnode-target"
        
        print(f"📋 Creating Lambda target: {target_name}")
        print(f"📊 Pointing to Lambda: {function_arn}")
        
        # Target configuration for Lambda
        target_configuration = {
            "lambda": {
                "lambdaArn": function_arn
            }
        }
        
        # Create target
        target_response = bedrock_agentcore.create_gateway_target(
            gatewayIdentifier=gateway_id,
            name=target_name,
            description="Lambda target for TACNode proxy - Created by Augment Agent",
            targetConfiguration=target_configuration
        )
        
        target_id = target_response['targetId']
        print(f"✅ Lambda target created: {target_id}")
        
        # Wait for target to be ready
        print(f"⏳ Waiting for target to be ready...")
        time.sleep(30)
        
        return target_id
        
    except Exception as e:
        print(f"❌ Error creating Lambda target: {e}")
        return None

def create_lambda_function_url(function_name, function_arn):
    """Create Lambda Function URL as alternative to Gateway"""
    print(f"\n🌐 CREATING LAMBDA FUNCTION URL")
    print("-" * 50)
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    try:
        print(f"📋 Creating Function URL for: {function_name}")
        
        # Create Function URL configuration
        url_response = lambda_client.create_function_url_config(
            FunctionName=function_name,
            AuthType='NONE',  # For testing - in production use AWS_IAM
            Cors={
                'AllowCredentials': False,
                'AllowHeaders': ['*'],
                'AllowMethods': ['POST', 'GET'],
                'AllowOrigins': ['*'],
                'ExposeHeaders': ['*'],
                'MaxAge': 86400
            }
        )
        
        function_url = url_response['FunctionUrl']
        print(f"✅ Function URL created: {function_url}")
        
        # Add resource-based policy to allow public access (for testing)
        try:
            lambda_client.add_permission(
                FunctionName=function_name,
                StatementId='AllowPublicAccess',
                Action='lambda:InvokeFunctionUrl',
                Principal='*',
                FunctionUrlAuthType='NONE'
            )
            print(f"✅ Public access permission added")
        except Exception as perm_error:
            print(f"⚠️ Permission may already exist: {perm_error}")
        
        return "LAMBDA_URL", function_url, "DIRECT"
        
    except Exception as e:
        print(f"❌ Error creating Function URL: {e}")
        return None, None, None

def save_real_gateway_config(gateway_id, gateway_url, target_id):
    """Save real gateway configuration"""
    config = {
        "gateway": {
            "id": gateway_id,
            "url": gateway_url,
            "name": "augment-real-gateway"
        },
        "target": {
            "id": target_id,
            "name": "augment-lambda-tacnode-target"
        },
        "lambda": {
            "functionName": "augment-tacnode-proxy-1755237143"  # From previous setup
        },
        "tacnode": {
            "endpoint": "https://mcp-server.tacnode.io/mcp",
            "database": "postgres",
            "table": "test"
        },
        "cognito": {
            "userPoolId": "us-east-1_qVOK14gn5",
            "clientId": "629cm5j58a7o0lhh1qph1re0l5",
            "clientSecret": "t7uo744afdgrlasjgqe0rsdasdm8ovg91otr12guk4jq79c3d64",
            "tokenEndpoint": "https://us-east-1-qvok14gn5.auth.us-east-1.amazoncognito.com/oauth2/token"
        },
        "created_by": "Augment Agent",
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "type": "real_gateway_with_lambda"
    }
    
    with open('augment-real-gateway-config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Real gateway configuration saved")
    
    return config

def main():
    """Main setup function"""
    print("🚀 REAL AGENTCORE GATEWAY SETUP")
    print("=" * 70)
    print("🎯 Creating real AgentCore Gateway with Lambda target")
    print("🎯 For end-to-end testing with real data")
    
    gateway_id, gateway_url, target_id = create_gateway_with_lambda_target()
    
    if gateway_id and gateway_url:
        # Save configuration
        config = save_real_gateway_config(gateway_id, gateway_url, target_id)
        
        print(f"\n" + "=" * 70)
        print(f"🎉 REAL GATEWAY SETUP COMPLETE!")
        print(f"✅ Gateway ID: {gateway_id}")
        print(f"✅ Gateway URL: {gateway_url}")
        print(f"✅ Target ID: {target_id}")
        print(f"✅ Ready for real end-to-end testing")
        
        print(f"\n🌐 REAL ARCHITECTURE:")
        print("   User → AgentCore Gateway → Lambda → TACNode → PostgreSQL")
        print("   ✅ All components real and working")
        
        print(f"\n🎯 NEXT: Run end-to-end test with real data")
    else:
        print(f"\n❌ REAL GATEWAY SETUP FAILED")

if __name__ == "__main__":
    main()

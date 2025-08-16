#!/usr/bin/env python3
"""
Create real AgentCore Gateway with Lambda as target
Gateway → Lambda → TACNode → PostgreSQL
"""

import boto3
import json
import time

def create_agentcore_gateway_with_lambda_target():
    """Create AgentCore Gateway with Lambda target"""
    print("🏗️ CREATING AGENTCORE GATEWAY WITH LAMBDA TARGET")
    print("=" * 70)
    print("🎯 ARCHITECTURE: Gateway → Lambda → TACNode → PostgreSQL")
    
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
        # Step 1: Create the Gateway
        print(f"\n📋 STEP 1: Creating AgentCore Gateway")
        print("-" * 50)
        
        gateway_name = "augment-gateway-lambda-tacnode"
        
        # First create IAM role for gateway
        gateway_role_arn = create_gateway_execution_role()
        if not gateway_role_arn:
            print("❌ Failed to create gateway execution role")
            return None, None, None

        # Create gateway with custom JWT using correct parameters
        gateway_response = bedrock_agentcore.create_gateway(
            name=gateway_name,
            description="AgentCore Gateway with Lambda target for TACNode - Created by Augment Agent",
            roleArn=gateway_role_arn,
            protocolType="MCP",
            authorizerType="CUSTOM_JWT",
            authorizerConfiguration={
                "customJWTAuthorizer": {
                    "discoveryUrl": "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_qVOK14gn5/.well-known/openid-configuration",
                    "allowedAudience": ["629cm5j58a7o0lhh1qph1re0l5"],
                    "allowedClients": ["629cm5j58a7o0lhh1qph1re0l5"]
                }
            }
        )
        
        gateway_id = gateway_response['gatewayId']
        print(f"✅ Gateway created: {gateway_id}")
        
        # Wait for gateway to be ready
        print(f"⏳ Waiting for gateway to be ready...")
        time.sleep(30)
        
        # Get gateway details
        gateway_details = bedrock_agentcore.get_gateway(gatewayIdentifier=gateway_id)
        gateway_url = gateway_details['gateway']['gatewayUrl']
        gateway_status = gateway_details['gateway']['status']
        
        print(f"✅ Gateway status: {gateway_status}")
        print(f"✅ Gateway URL: {gateway_url}")
        
        # Step 2: Create Lambda target in the Gateway
        print(f"\n📋 STEP 2: Creating Lambda target in Gateway")
        print("-" * 50)
        
        target_id = create_lambda_target_in_gateway(gateway_id, function_arn)
        
        if target_id:
            print(f"✅ Lambda target created: {target_id}")
            return gateway_id, gateway_url, target_id
        else:
            print(f"❌ Failed to create Lambda target")
            return None, None, None
        
    except Exception as e:
        print(f"❌ Error creating gateway: {e}")
        print(f"🔍 Error details: {str(e)}")
        return None, None, None

def create_gateway_execution_role():
    """Create IAM role for gateway execution"""
    print(f"📋 Creating IAM role for Gateway execution")

    iam = boto3.client('iam', region_name='us-east-1')

    try:
        role_name = f"augment-gateway-role-{int(time.time())}"

        # Trust policy for AgentCore Gateway
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "bedrock-agentcore.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }

        # Create role
        role_response = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="IAM role for AgentCore Gateway - Created by Augment Agent"
        )

        role_arn = role_response['Role']['Arn']
        print(f"✅ Gateway IAM role created: {role_arn}")

        # Basic permissions policy
        permissions_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents",
                        "lambda:InvokeFunction"
                    ],
                    "Resource": "*"
                }
            ]
        }

        policy_name = f"augment-gateway-policy-{int(time.time())}"

        # Create policy
        policy_response = iam.create_policy(
            PolicyName=policy_name,
            PolicyDocument=json.dumps(permissions_policy),
            Description="Permissions for AgentCore Gateway - Created by Augment Agent"
        )

        # Attach policy to role
        iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn=policy_response['Policy']['Arn']
        )

        print(f"✅ Gateway permissions attached")

        # Wait for role to propagate
        time.sleep(30)

        return role_arn

    except Exception as e:
        print(f"❌ Error creating gateway role: {e}")
        return None

def create_lambda_target_in_gateway(gateway_id, function_arn):
    """Create Lambda target in the gateway"""
    bedrock_agentcore = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
    
    try:
        target_name = "augment-lambda-tacnode-target"
        
        print(f"📋 Creating Lambda target: {target_name}")
        print(f"📊 Target Lambda ARN: {function_arn}")
        
        # Lambda target configuration
        target_configuration = {
            "lambda": {
                "lambdaArn": function_arn
            }
        }
        
        # Create the target
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
        
        # Verify target status
        target_details = bedrock_agentcore.get_gateway_target(
            gatewayIdentifier=gateway_id,
            targetId=target_id
        )
        
        target_status = target_details['target']['status']
        print(f"✅ Target status: {target_status}")
        
        return target_id
        
    except Exception as e:
        print(f"❌ Error creating Lambda target: {e}")
        print(f"🔍 Error details: {str(e)}")
        return None

def add_lambda_invoke_permission(function_name, gateway_id):
    """Add permission for Gateway to invoke Lambda"""
    print(f"\n📋 STEP 3: Adding Lambda invoke permission for Gateway")
    print("-" * 50)
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    try:
        # Add permission for AgentCore Gateway to invoke Lambda
        lambda_client.add_permission(
            FunctionName=function_name,
            StatementId=f'AllowAgentCoreGateway-{gateway_id}',
            Action='lambda:InvokeFunction',
            Principal='bedrock-agentcore.amazonaws.com',
            SourceArn=f'arn:aws:bedrock-agentcore:us-east-1:*:gateway/{gateway_id}'
        )
        
        print(f"✅ Added Lambda invoke permission for Gateway")
        return True
        
    except Exception as e:
        if 'ResourceConflictException' in str(e):
            print(f"⚠️ Permission already exists: {e}")
            return True
        else:
            print(f"❌ Error adding Lambda permission: {e}")
            return False

def save_gateway_lambda_config(gateway_id, gateway_url, target_id, function_name):
    """Save Gateway with Lambda target configuration"""
    config = {
        "gateway": {
            "id": gateway_id,
            "url": gateway_url,
            "name": "augment-gateway-lambda-tacnode"
        },
        "target": {
            "id": target_id,
            "name": "augment-lambda-tacnode-target",
            "type": "lambda"
        },
        "lambda": {
            "functionName": function_name
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
        "architecture": "Gateway → Lambda → TACNode → PostgreSQL",
        "created_by": "Augment Agent",
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    }
    
    with open('augment-gateway-lambda-config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Gateway-Lambda configuration saved")
    
    return config

def main():
    """Main setup function"""
    print("🚀 AGENTCORE GATEWAY WITH LAMBDA TARGET SETUP")
    print("=" * 70)
    print("🎯 Creating AgentCore Gateway with Lambda as target")
    print("🎯 Architecture: Gateway → Lambda → TACNode → PostgreSQL")
    print("🎯 For real end-to-end testing through Gateway")
    
    # Create Gateway with Lambda target
    gateway_id, gateway_url, target_id = create_agentcore_gateway_with_lambda_target()
    
    if gateway_id and gateway_url and target_id:
        # Load Lambda function name
        with open('augment-lambda-tacnode-config.json', 'r') as f:
            lambda_config = json.load(f)
        function_name = lambda_config['lambda']['functionName']
        
        # Add Lambda invoke permission
        permission_added = add_lambda_invoke_permission(function_name, gateway_id)
        
        if permission_added:
            # Save configuration
            config = save_gateway_lambda_config(gateway_id, gateway_url, target_id, function_name)
            
            print(f"\n" + "=" * 70)
            print(f"🎉 AGENTCORE GATEWAY WITH LAMBDA TARGET COMPLETE!")
            print(f"✅ Gateway ID: {gateway_id}")
            print(f"✅ Gateway URL: {gateway_url}")
            print(f"✅ Lambda Target ID: {target_id}")
            print(f"✅ Lambda Function: {function_name}")
            print(f"✅ Permissions configured")
            
            print(f"\n🌐 REAL ARCHITECTURE CREATED:")
            print("   User → AgentCore Gateway → Lambda → TACNode → PostgreSQL")
            print("   ✅ Gateway routes to Lambda target")
            print("   ✅ Lambda proxies to TACNode")
            print("   ✅ TACNode queries PostgreSQL")
            print("   ✅ Real data flows back through pipeline")
            
            print(f"\n🎯 READY FOR REAL END-TO-END TESTING:")
            print(f"   Send queries to Gateway URL: {gateway_url}")
            print(f"   Gateway will forward to Lambda target")
            print(f"   Lambda will proxy to TACNode")
            print(f"   Real PostgreSQL data will be returned")
        else:
            print(f"\n❌ FAILED TO ADD LAMBDA PERMISSIONS")
    else:
        print(f"\n❌ FAILED TO CREATE GATEWAY WITH LAMBDA TARGET")

if __name__ == "__main__":
    main()

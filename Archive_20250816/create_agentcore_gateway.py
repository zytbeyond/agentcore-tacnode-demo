#!/usr/bin/env python3
"""
Create Bedrock AgentCore Gateway for Tacnode Context Lake integration
"""

import boto3
import json
import sys
from botocore.exceptions import ClientError, NoCredentialsError

def create_agentcore_gateway():
    """Create the AgentCore Gateway for Tacnode Context Lake"""
    
    try:
        # Initialize the bedrock-agentcore-control client
        client = boto3.client('bedrock-agentcore-control', region_name='us-west-2')
        
        # Try to create a service-linked role first
        try:
            iam_client = boto3.client('iam', region_name='us-west-2')
            print("🔧 Attempting to create service-linked role for Bedrock AgentCore...")

            service_linked_role = iam_client.create_service_linked_role(
                AWSServiceName='bedrock-agentcore.amazonaws.com',
                Description='Service-linked role for Bedrock AgentCore Gateway'
            )
            role_arn = service_linked_role['Role']['Arn']
            print(f"✅ Service-linked role created: {role_arn}")

        except ClientError as e:
            if e.response['Error']['Code'] == 'InvalidInput':
                # Service-linked role already exists or service doesn't support it
                print("ℹ️  Using existing service permissions...")
                role_arn = None
            else:
                print(f"⚠️  Could not create service-linked role: {e.response['Error']['Message']}")
                role_arn = None

        # Gateway configuration - try without role first
        gateway_config = {
            'name': 'TacnodeContextLakeGateway',
            'description': 'Gateway for Tacnode Context Lake integration with AgentCore',
            'protocolType': 'MCP',
            'protocolConfiguration': {
                'mcp': {
                    'supportedVersions': ['2024-11-05'],
                    'instructions': 'Gateway for connecting to Tacnode Context Lake for real-time data processing and analytics',
                    'searchType': 'SEMANTIC'
                }
            },
            'authorizerType': 'CUSTOM_JWT',
            'authorizerConfiguration': {
                'customJWTAuthorizer': {
                    'discoveryUrl': 'https://tacnode.com/.well-known/openid_configuration',
                    'allowedAudience': ['tacnode-context-lake'],
                    'allowedClients': ['agentcore-gateway']
                }
            }
        }

        # Add role if we have one
        if role_arn:
            gateway_config['roleArn'] = role_arn
        
        print("🏗️  Creating Bedrock AgentCore Gateway...")
        print(f"   Name: {gateway_config['name']}")
        print(f"   Protocol: {gateway_config['protocolType']}")
        print(f"   Region: us-west-2")
        print()
        
        # Create the gateway
        response = client.create_gateway(**gateway_config)
        
        print("✅ Gateway created successfully!")
        print(f"   Gateway ID: {response['gatewayId']}")
        print(f"   Gateway ARN: {response['gatewayArn']}")
        print(f"   Gateway URL: {response['gatewayUrl']}")
        print(f"   Status: {response['status']}")
        print()
        
        # Save gateway details to file
        gateway_details = {
            'gatewayId': response['gatewayId'],
            'gatewayArn': response['gatewayArn'],
            'gatewayUrl': response['gatewayUrl'],
            'status': response['status'],
            'name': response['name'],
            'description': response['description']
        }
        
        with open('agentcore-gateway-details.json', 'w') as f:
            json.dump(gateway_details, f, indent=2)
        
        print("📄 Gateway details saved to: agentcore-gateway-details.json")
        print()
        print("🎯 Next Steps:")
        print("   1. Subscribe to Tacnode Context Lake on AWS Marketplace")
        print("   2. Add Tacnode Context Lake as a gateway target")
        print("   3. Configure the gateway target in the dropdown")
        
        return response
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        
        if error_code == 'UnauthorizedOperation':
            print("❌ Error: Insufficient permissions to create AgentCore Gateway")
            print("   Required permissions: bedrock-agentcore-control:CreateGateway")
        elif error_code == 'InvalidParameterValue':
            print(f"❌ Error: Invalid parameter - {error_message}")
        elif error_code == 'ResourceAlreadyExistsException':
            print("❌ Error: Gateway with this name already exists")
        else:
            print(f"❌ Error: {error_code} - {error_message}")
        
        return None
        
    except NoCredentialsError:
        print("❌ Error: AWS credentials not found")
        print("   Please configure AWS credentials using 'aws configure'")
        return None
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return None

def list_existing_gateways():
    """List existing AgentCore Gateways"""
    try:
        client = boto3.client('bedrock-agentcore-control', region_name='us-west-2')
        
        print("📋 Listing existing AgentCore Gateways...")
        response = client.list_gateways()
        
        if response.get('gateways'):
            for gateway in response['gateways']:
                print(f"   • {gateway['name']} ({gateway['gatewayId']}) - {gateway['status']}")
        else:
            print("   No existing gateways found")
        print()
        
    except Exception as e:
        print(f"❌ Error listing gateways: {str(e)}")

if __name__ == "__main__":
    print("🚀 Bedrock AgentCore Gateway Creator")
    print("=" * 50)
    print()
    
    # List existing gateways first
    list_existing_gateways()
    
    # Create the gateway
    result = create_agentcore_gateway()
    
    if result:
        sys.exit(0)
    else:
        sys.exit(1)

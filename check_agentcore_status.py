#!/usr/bin/env python3
"""
Check Bedrock AgentCore Gateway status and provide setup guidance
"""

import boto3
import json
from botocore.exceptions import ClientError, NoCredentialsError

def check_agentcore_availability():
    """Check if AgentCore services are available in the region"""
    try:
        client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
        
        print("🔍 Checking AgentCore service availability...")
        
        # Try to list gateways to test service availability
        response = client.list_gateways()
        print("✅ Bedrock AgentCore service is available!")
        
        if response.get('gateways'):
            print(f"📋 Found {len(response['gateways'])} existing gateway(s):")
            for gateway in response['gateways']:
                print(f"   • {gateway['name']} ({gateway['gatewayId']}) - Status: {gateway['status']}")
        else:
            print("📋 No existing gateways found")
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'UnauthorizedOperation':
            print("❌ AgentCore service available but insufficient permissions")
            print("   Required: bedrock-agentcore-control:ListGateways")
        else:
            print(f"❌ AgentCore service error: {error_code}")
        return False
        
    except Exception as e:
        print(f"❌ AgentCore service not available: {str(e)}")
        return False

def check_iam_permissions():
    """Check IAM permissions for creating gateways"""
    try:
        iam_client = boto3.client('iam', region_name='us-east-1')
        
        print("\n🔐 Checking IAM permissions...")
        
        # Try to list roles to check basic IAM access
        try:
            response = iam_client.list_roles(MaxItems=1)
            print("✅ Basic IAM access available")
            
            # Check for existing Bedrock roles
            roles_response = iam_client.list_roles()
            bedrock_roles = [role for role in roles_response['Roles'] 
                           if 'bedrock' in role['RoleName'].lower() or 'agent' in role['RoleName'].lower()]
            
            if bedrock_roles:
                print(f"📋 Found {len(bedrock_roles)} potential Bedrock role(s):")
                for role in bedrock_roles:
                    print(f"   • {role['RoleName']} - {role['Arn']}")
            else:
                print("📋 No existing Bedrock-related roles found")
                
        except ClientError as e:
            print(f"❌ Limited IAM access: {e.response['Error']['Code']}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ IAM service error: {str(e)}")
        return False

def check_marketplace_access():
    """Check AWS Marketplace access"""
    try:
        marketplace_client = boto3.client('marketplace-catalog', region_name='us-east-1')  # Marketplace is in us-east-1
        
        print("\n🛒 Checking AWS Marketplace access...")
        
        # Try to list entities to test marketplace access
        try:
            response = marketplace_client.list_entities(
                Catalog='AWSMarketplace',
                EntityType='DataProduct',
                MaxResults=1
            )
            print("✅ AWS Marketplace access available")
            return True
            
        except ClientError as e:
            print(f"❌ Limited Marketplace access: {e.response['Error']['Code']}")
            return False
            
    except Exception as e:
        print(f"❌ Marketplace service error: {str(e)}")
        return False

def provide_setup_guidance():
    """Provide setup guidance based on current status"""
    print("\n" + "="*60)
    print("🎯 SETUP GUIDANCE")
    print("="*60)
    
    print("\n📋 Current Status Summary:")
    
    agentcore_available = check_agentcore_availability()
    iam_available = check_iam_permissions()
    marketplace_available = check_marketplace_access()
    
    print(f"\n🔧 Recommended Next Steps:")
    
    if not agentcore_available:
        print("1. ❌ Enable Bedrock AgentCore service in your AWS account")
        print("   - Go to AWS Bedrock Console")
        print("   - Enable AgentCore preview features")
        print("   - Ensure you're in a supported region (us-east-1)")
    
    if not iam_available:
        print("2. ❌ Request IAM permissions for gateway creation")
        print("   - Contact your AWS administrator")
        print("   - Request permissions: iam:CreateRole, iam:AttachRolePolicy")
        print("   - Request permissions: bedrock-agentcore-control:*")
    else:
        print("2. ✅ IAM permissions look good")
    
    if not marketplace_available:
        print("3. ❌ Request AWS Marketplace access")
        print("   - Contact your AWS administrator")
        print("   - Request marketplace subscription permissions")
    else:
        print("3. ✅ Marketplace access available")
    
    print("\n🏗️ Manual Setup Options:")
    print("   Option A: Use AWS Console (Recommended)")
    print("   - Follow the guide in AGENTCORE_GATEWAY_SETUP.md")
    print("   - Create gateway manually through Bedrock Console")
    print("   - Subscribe to Tacnode Context Lake via Marketplace")
    
    print("\n   Option B: Request Admin Assistance")
    print("   - Share the setup guide with your AWS administrator")
    print("   - Have them create the gateway and IAM role")
    print("   - You can then configure the integration")
    
    print("\n📄 Documentation:")
    print("   - Setup Guide: ./AGENTCORE_GATEWAY_SETUP.md")
    print("   - AWS Bedrock AgentCore Documentation")
    print("   - Tacnode Context Lake Marketplace Page")

def main():
    print("🚀 Bedrock AgentCore Gateway Status Checker")
    print("=" * 60)
    
    try:
        # Check AWS credentials
        sts_client = boto3.client('sts')
        identity = sts_client.get_caller_identity()
        print(f"🔑 AWS Account: {identity['Account']}")
        print(f"🔑 User/Role: {identity['Arn']}")
        
        # Provide guidance
        provide_setup_guidance()
        
    except NoCredentialsError:
        print("❌ AWS credentials not found")
        print("   Please configure AWS credentials using 'aws configure'")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()

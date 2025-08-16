#!/usr/bin/env python3
"""
Debug Gateway details and find execution role
"""

import boto3
import json

def debug_gateway_details():
    """Debug Gateway details to understand the structure"""
    print("🔍 DEBUGGING GATEWAY DETAILS")
    print("=" * 70)
    
    bedrock_agentcore = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
    
    gateway_id = "pureawstacnodegateway-l0f1tg5t8o"
    
    try:
        # Get Gateway details
        print(f"📋 Getting Gateway details for: {gateway_id}")
        
        gateway_response = bedrock_agentcore.get_gateway(gatewayIdentifier=gateway_id)
        
        print(f"\n📊 Full Gateway Response:")
        print(json.dumps(gateway_response, indent=2, default=str))
        
        # Try to find execution role in different locations
        if 'gateway' in gateway_response:
            gateway_details = gateway_response['gateway']
            print(f"\n🔍 Gateway Details Keys: {list(gateway_details.keys())}")
            
            # Check for execution role
            execution_role = gateway_details.get('executionRoleArn')
            if execution_role:
                print(f"✅ Found execution role: {execution_role}")
            else:
                print(f"❌ No executionRoleArn found")
                
                # Check for other role-related fields
                for key, value in gateway_details.items():
                    if 'role' in key.lower() or 'arn' in key.lower():
                        print(f"🔍 Found role-related field: {key} = {value}")
        
        # List all gateways to see structure
        print(f"\n📋 Listing all gateways for comparison:")
        gateways_response = bedrock_agentcore.list_gateways()
        
        for gateway in gateways_response.get('gateways', []):
            print(f"\nGateway: {gateway.get('gatewayId', 'Unknown')}")
            print(f"  Keys: {list(gateway.keys())}")
            if 'executionRoleArn' in gateway:
                print(f"  Execution Role: {gateway['executionRoleArn']}")
            else:
                print(f"  No execution role found")
        
        return gateway_response
        
    except Exception as e:
        print(f"❌ Error getting gateway details: {e}")
        return None

def check_iam_roles():
    """Check IAM roles that might be related to AgentCore"""
    print(f"\n🔍 CHECKING IAM ROLES FOR AGENTCORE")
    print("=" * 50)
    
    iam = boto3.client('iam', region_name='us-east-1')
    
    try:
        # List roles that might be related to AgentCore
        roles_response = iam.list_roles()
        
        agentcore_roles = []
        for role in roles_response['Roles']:
            role_name = role['RoleName']
            if any(keyword in role_name.lower() for keyword in ['agentcore', 'bedrock', 'gateway']):
                agentcore_roles.append(role)
                print(f"🔍 Found potential AgentCore role: {role_name}")
                print(f"   ARN: {role['Arn']}")
                print(f"   Created: {role['CreateDate']}")
        
        if not agentcore_roles:
            print(f"❌ No AgentCore-related roles found")
        
        return agentcore_roles
        
    except Exception as e:
        print(f"❌ Error checking IAM roles: {e}")
        return []

def check_cloudwatch_logs():
    """Check existing CloudWatch logs for AgentCore"""
    print(f"\n🔍 CHECKING CLOUDWATCH LOGS")
    print("=" * 50)
    
    logs_client = boto3.client('logs', region_name='us-east-1')
    
    try:
        # List log groups that might be related to AgentCore
        log_groups = logs_client.describe_log_groups()
        
        agentcore_logs = []
        for log_group in log_groups['logGroups']:
            log_group_name = log_group['logGroupName']
            if any(keyword in log_group_name.lower() for keyword in ['agentcore', 'bedrock', 'gateway']):
                agentcore_logs.append(log_group)
                print(f"🔍 Found AgentCore log group: {log_group_name}")
                
                # Get recent log events
                try:
                    streams = logs_client.describe_log_streams(
                        logGroupName=log_group_name,
                        orderBy='LastEventTime',
                        descending=True,
                        limit=1
                    )
                    
                    if streams['logStreams']:
                        latest_stream = streams['logStreams'][0]
                        print(f"   Latest stream: {latest_stream['logStreamName']}")
                        print(f"   Last event: {latest_stream.get('lastEventTime', 'No events')}")
                        
                        # Get recent events
                        events = logs_client.get_log_events(
                            logGroupName=log_group_name,
                            logStreamName=latest_stream['logStreamName'],
                            limit=5
                        )
                        
                        print(f"   Recent events:")
                        for event in events['events'][-3:]:  # Last 3 events
                            print(f"     {event['timestamp']}: {event['message'][:100]}...")
                            
                except Exception as e:
                    print(f"   ⚠️ Could not get log events: {e}")
        
        if not agentcore_logs:
            print(f"❌ No AgentCore-related log groups found")
        
        return agentcore_logs
        
    except Exception as e:
        print(f"❌ Error checking CloudWatch logs: {e}")
        return []

def main():
    """Debug Gateway and find execution role"""
    print("🔍 GATEWAY DEBUGGING AND ROLE DISCOVERY")
    print("=" * 70)
    
    # Debug Gateway details
    gateway_details = debug_gateway_details()
    
    # Check IAM roles
    iam_roles = check_iam_roles()
    
    # Check CloudWatch logs
    log_groups = check_cloudwatch_logs()
    
    print(f"\n" + "=" * 70)
    print(f"🔍 DEBUGGING SUMMARY:")
    
    if gateway_details:
        print(f"✅ Gateway details retrieved")
    else:
        print(f"❌ Could not get Gateway details")
    
    if iam_roles:
        print(f"✅ Found {len(iam_roles)} potential AgentCore IAM roles")
    else:
        print(f"❌ No AgentCore IAM roles found")
    
    if log_groups:
        print(f"✅ Found {len(log_groups)} AgentCore log groups")
    else:
        print(f"❌ No AgentCore log groups found")

if __name__ == "__main__":
    main()

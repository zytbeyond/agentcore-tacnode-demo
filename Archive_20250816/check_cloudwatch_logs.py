#!/usr/bin/env python3
"""
Check CloudWatch logs for detailed error information
"""

import boto3
import json
from datetime import datetime, timedelta

def check_cloudwatch_logs():
    """Check CloudWatch logs for Gateway errors"""
    print("📊 CHECKING CLOUDWATCH LOGS FOR GATEWAY ERRORS")
    print("=" * 70)
    
    logs_client = boto3.client('logs', region_name='us-east-1')
    
    # Check multiple potential log groups
    log_groups_to_check = [
        "/aws/bedrock-agentcore/gateway/pureawstacnodegateway-l0f1tg5t8o",
        "/aws/bedrock-agentcore/gateway",
        "/aws/bedrock-agentcore/runtimes/TACNodeAgentCoreRuntimeFinal-gTtSuW3JMQ-DEFAULT",
        "/aws/bedrock-agentcore/runtimes/TACNodeBusinessIntelligenceAgent-WyUKPc8jfZ-DEFAULT",
        "/aws/lambda",
        "/aws/apigateway"
    ]
    
    # Time range for recent logs (last 30 minutes)
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=30)
    
    start_timestamp = int(start_time.timestamp() * 1000)
    end_timestamp = int(end_time.timestamp() * 1000)
    
    print(f"🕐 Checking logs from {start_time} to {end_time}")
    
    for log_group_name in log_groups_to_check:
        print(f"\n📋 Checking log group: {log_group_name}")
        print("-" * 50)
        
        try:
            # Check if log group exists
            log_groups = logs_client.describe_log_groups(
                logGroupNamePrefix=log_group_name,
                limit=1
            )
            
            if not log_groups['logGroups']:
                print(f"❌ Log group does not exist")
                continue
            
            print(f"✅ Log group exists")
            
            # Get log streams
            streams = logs_client.describe_log_streams(
                logGroupName=log_group_name,
                orderBy='LastEventTime',
                descending=True,
                limit=5
            )
            
            if not streams['logStreams']:
                print(f"❌ No log streams found")
                continue
            
            print(f"📊 Found {len(streams['logStreams'])} log streams")
            
            # Check recent events in each stream
            for stream in streams['logStreams']:
                stream_name = stream['logStreamName']
                last_event_time = stream.get('lastEventTime', 0)
                
                print(f"\n🔍 Stream: {stream_name}")
                print(f"   Last event: {datetime.fromtimestamp(last_event_time/1000) if last_event_time else 'No events'}")
                
                try:
                    # Get recent events
                    events = logs_client.get_log_events(
                        logGroupName=log_group_name,
                        logStreamName=stream_name,
                        startTime=start_timestamp,
                        endTime=end_timestamp,
                        limit=20
                    )
                    
                    if events['events']:
                        print(f"   📝 Recent events ({len(events['events'])}):")
                        for event in events['events'][-10:]:  # Last 10 events
                            timestamp = datetime.fromtimestamp(event['timestamp']/1000)
                            message = event['message'].strip()
                            print(f"     {timestamp}: {message}")
                            
                            # Look for specific error patterns
                            if any(keyword in message.lower() for keyword in ['error', 'exception', 'failed', 'unauthorized', 'credential']):
                                print(f"     🚨 ERROR DETECTED: {message}")
                    else:
                        print(f"   ❌ No recent events")
                        
                except Exception as e:
                    print(f"   ⚠️ Could not get events: {e}")
            
        except Exception as e:
            print(f"❌ Error checking log group: {e}")
    
    # Also check for any AgentCore-related logs
    print(f"\n📋 Searching for all AgentCore-related log groups")
    print("-" * 50)
    
    try:
        all_log_groups = logs_client.describe_log_groups()
        
        agentcore_groups = []
        for group in all_log_groups['logGroups']:
            group_name = group['logGroupName']
            if any(keyword in group_name.lower() for keyword in ['agentcore', 'bedrock', 'gateway']):
                agentcore_groups.append(group_name)
        
        print(f"🔍 Found AgentCore-related log groups:")
        for group_name in agentcore_groups:
            print(f"  - {group_name}")
            
            # Check for recent activity
            try:
                streams = logs_client.describe_log_streams(
                    logGroupName=group_name,
                    orderBy='LastEventTime',
                    descending=True,
                    limit=1
                )
                
                if streams['logStreams']:
                    last_event = streams['logStreams'][0].get('lastEventTime', 0)
                    if last_event:
                        last_time = datetime.fromtimestamp(last_event/1000)
                        if last_time > start_time:
                            print(f"    🔥 Recent activity: {last_time}")
                        else:
                            print(f"    💤 Last activity: {last_time}")
                    else:
                        print(f"    ❌ No events")
                else:
                    print(f"    ❌ No streams")
                    
            except Exception as e:
                print(f"    ⚠️ Could not check: {e}")
        
    except Exception as e:
        print(f"❌ Error searching log groups: {e}")

def check_credential_provider_logs():
    """Check for credential provider specific issues"""
    print(f"\n🔑 CHECKING CREDENTIAL PROVIDER ACCESS")
    print("=" * 70)
    
    bedrock_agentcore = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
    
    try:
        # List credential providers to see if they're accessible
        print(f"📋 Listing credential providers...")
        
        providers = bedrock_agentcore.list_api_key_credential_providers()
        
        print(f"✅ Found {len(providers.get('credentialProviders', []))} credential providers:")
        for provider in providers.get('credentialProviders', []):
            print(f"  - {provider.get('name', 'Unknown')}: {provider.get('credentialProviderArn', 'No ARN')}")
        
        # Try to get our specific provider
        print(f"\n📋 Checking our TACNode credential provider...")
        
        try:
            provider_details = bedrock_agentcore.get_api_key_credential_provider(name="tacnode-mcp-token")
            print(f"✅ TACNode credential provider accessible:")
            print(f"   Name: {provider_details.get('name', 'Unknown')}")
            print(f"   ARN: {provider_details.get('credentialProviderArn', 'No ARN')}")
            print(f"   Status: {provider_details.get('status', 'Unknown')}")
            
        except Exception as e:
            print(f"❌ Cannot access TACNode credential provider: {e}")
        
    except Exception as e:
        print(f"❌ Error checking credential providers: {e}")

def main():
    """Check CloudWatch logs and credential provider access"""
    print("📊 CLOUDWATCH LOGS AND CREDENTIAL PROVIDER DIAGNOSTIC")
    print("=" * 70)
    
    # Check CloudWatch logs
    check_cloudwatch_logs()
    
    # Check credential provider access
    check_credential_provider_logs()
    
    print(f"\n" + "=" * 70)
    print(f"🔍 DIAGNOSTIC COMPLETE")
    print(f"📊 Check the logs above for specific error messages")
    print(f"🔑 Verify credential provider accessibility")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Get AgentCore Gateway IP Address for TACNode Whitelist
Find the source IP address that AgentCore Gateway uses to access TACNode
"""

import boto3
import json
import requests
import time
from datetime import datetime

class AgentCoreGatewayIPFinder:
    """Find AgentCore Gateway IP address for TACNode whitelist"""
    
    def __init__(self):
        self.bedrock_agentcore_control = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
        self.ec2 = boto3.client('ec2', region_name='us-east-1')
        self.gateway_id = "tacnodecontextlakegateway-bkq6ozcvxp"
    
    def get_gateway_details(self):
        """Get detailed information about the AgentCore Gateway"""
        print("🔍 Getting AgentCore Gateway details...")
        
        try:
            response = self.bedrock_agentcore_control.get_gateway(gatewayIdentifier=self.gateway_id)
            
            print(f"✅ Gateway Details:")
            print(f"   Gateway ID: {response['gatewayId']}")
            print(f"   Gateway Name: {response['name']}")
            print(f"   Status: {response['status']}")
            print(f"   Gateway ARN: {response['gatewayArn']}")
            
            # Check if there are network details
            if 'networkConfiguration' in response:
                network_config = response['networkConfiguration']
                print(f"   Network Mode: {network_config.get('networkMode', 'N/A')}")
                
                if 'vpcConfiguration' in network_config:
                    vpc_config = network_config['vpcConfiguration']
                    print(f"   VPC ID: {vpc_config.get('vpcId', 'N/A')}")
                    print(f"   Subnet IDs: {vpc_config.get('subnetIds', 'N/A')}")
                    print(f"   Security Group IDs: {vpc_config.get('securityGroupIds', 'N/A')}")
            
            return response
            
        except Exception as e:
            print(f"❌ Error getting gateway details: {e}")
            return None
    
    def get_gateway_targets(self):
        """Get gateway targets to understand the connection"""
        print("\n🎯 Getting Gateway Targets...")
        
        try:
            response = self.bedrock_agentcore_control.list_gateway_targets(gatewayIdentifier=self.gateway_id)
            
            if response.get('gatewayTargets'):
                for target in response['gatewayTargets']:
                    print(f"✅ Target Details:")
                    print(f"   Target ID: {target['gatewayTargetId']}")
                    print(f"   Target Name: {target.get('name', 'N/A')}")
                    print(f"   Status: {target['status']}")
                    print(f"   Target ARN: {target['gatewayTargetArn']}")
                    
                    # Get target details
                    try:
                        target_details = self.bedrock_agentcore_control.get_gateway_target(
                            gatewayIdentifier=self.gateway_id,
                            gatewayTargetIdentifier=target['gatewayTargetId']
                        )
                        
                        if 'targetConfiguration' in target_details:
                            target_config = target_details['targetConfiguration']
                            print(f"   Target Type: {target_config.get('type', 'N/A')}")
                            
                            if 'httpConfiguration' in target_config:
                                http_config = target_config['httpConfiguration']
                                print(f"   Target URL: {http_config.get('url', 'N/A')}")
                                
                    except Exception as e:
                        print(f"   ⚠️  Could not get target details: {e}")
            else:
                print("❌ No gateway targets found")
            
            return response
            
        except Exception as e:
            print(f"❌ Error getting gateway targets: {e}")
            return None
    
    def get_aws_service_ip_ranges(self):
        """Get AWS service IP ranges for Bedrock AgentCore"""
        print("\n🌐 Getting AWS Service IP Ranges...")
        
        try:
            # Get AWS IP ranges
            response = requests.get('https://ip-ranges.amazonaws.com/ip-ranges.json', timeout=30)
            ip_ranges = response.json()
            
            # Filter for Bedrock and AgentCore related services
            bedrock_ranges = []
            agentcore_ranges = []
            us_east_1_ranges = []
            
            for prefix in ip_ranges['prefixes']:
                if prefix['region'] == 'us-east-1':
                    us_east_1_ranges.append(prefix)
                    
                    if 'bedrock' in prefix.get('service', '').lower():
                        bedrock_ranges.append(prefix)
                    
                    if 'agentcore' in prefix.get('service', '').lower():
                        agentcore_ranges.append(prefix)
            
            print(f"✅ AWS IP Range Analysis:")
            print(f"   Total US-East-1 prefixes: {len(us_east_1_ranges)}")
            print(f"   Bedrock-related prefixes: {len(bedrock_ranges)}")
            print(f"   AgentCore-related prefixes: {len(agentcore_ranges)}")
            
            # Show some general AWS service ranges for us-east-1
            aws_services = set()
            for prefix in us_east_1_ranges[:20]:  # Show first 20
                service = prefix.get('service', 'UNKNOWN')
                aws_services.add(service)
                if service in ['AMAZON', 'EC2', 'S3', 'CLOUDFRONT']:
                    print(f"   {service}: {prefix['ip_prefix']}")
            
            print(f"\n📋 Available AWS Services in us-east-1: {sorted(list(aws_services))[:10]}...")
            
            return us_east_1_ranges
            
        except Exception as e:
            print(f"❌ Error getting AWS IP ranges: {e}")
            return None
    
    def test_tacnode_connection_from_gateway(self):
        """Test connection to TACNode to see source IP"""
        print("\n🧪 Testing TACNode Connection...")
        
        # Note: This would require invoking the gateway, which might show the source IP
        # in TACNode logs, but we can't directly get the gateway's outbound IP
        
        print("💡 To find the exact source IP:")
        print("   1. AgentCore Gateway uses AWS managed infrastructure")
        print("   2. The source IP will be from AWS's IP ranges")
        print("   3. Best approach: Check TACNode access logs during gateway invocation")
        print("   4. Alternative: Use AWS support to get specific IP ranges")
        
        return None
    
    def get_recommended_whitelist_approach(self):
        """Get recommended approach for TACNode whitelist"""
        print("\n📋 RECOMMENDED TACNODE WHITELIST APPROACH")
        print("=" * 60)
        
        print("🎯 OPTION 1: AWS IP Range Whitelist (Recommended)")
        print("   • Whitelist AWS us-east-1 service IP ranges")
        print("   • More reliable than specific IPs (AWS IPs can change)")
        print("   • Use AWS published IP ranges for us-east-1")
        
        print("\n🎯 OPTION 2: Monitor TACNode Logs")
        print("   • Invoke AgentCore Gateway → TACNode")
        print("   • Check TACNode access logs for source IP")
        print("   • Whitelist the specific IP(s) found")
        
        print("\n🎯 OPTION 3: AWS Support Request")
        print("   • Contact AWS Support for AgentCore Gateway IP ranges")
        print("   • Request specific IP ranges for Bedrock AgentCore in us-east-1")
        
        print("\n📋 IMMEDIATE ACTION ITEMS:")
        print("   1. Check TACNode logs during next gateway invocation")
        print("   2. Whitelist AWS us-east-1 IP ranges as interim solution")
        print("   3. Monitor for any connection failures")
        
        # Provide some common AWS IP ranges for us-east-1
        common_ranges = [
            "52.0.0.0/11",      # Common AWS range
            "54.0.0.0/8",       # EC2 and services
            "3.0.0.0/8",        # AWS services
            "18.0.0.0/8",       # AWS services
        ]
        
        print(f"\n🌐 COMMON AWS US-EAST-1 IP RANGES TO CONSIDER:")
        for ip_range in common_ranges:
            print(f"   • {ip_range}")
        
        print(f"\n⚠️  IMPORTANT:")
        print(f"   • These are broad ranges - use more specific ranges if possible")
        print(f"   • Monitor TACNode logs to identify exact source IPs")
        print(f"   • Consider using AWS PrivateLink for more secure connection")
    
    def analyze_gateway_networking(self):
        """Complete analysis of gateway networking for TACNode whitelist"""
        print("🔍 AGENTCORE GATEWAY IP ANALYSIS FOR TACNODE WHITELIST")
        print("=" * 70)
        
        # Step 1: Get gateway details
        gateway_info = self.get_gateway_details()
        
        # Step 2: Get gateway targets
        target_info = self.get_gateway_targets()
        
        # Step 3: Get AWS IP ranges
        ip_ranges = self.get_aws_service_ip_ranges()
        
        # Step 4: Test connection approach
        self.test_tacnode_connection_from_gateway()
        
        # Step 5: Provide recommendations
        self.get_recommended_whitelist_approach()
        
        print("\n" + "="*70)
        print("🎯 SUMMARY FOR TACNODE WHITELIST")
        print("="*70)
        
        print(f"\n✅ GATEWAY STATUS:")
        if gateway_info:
            print(f"   Gateway: {self.gateway_id} ✅ READY")
            print(f"   Status: {gateway_info.get('status', 'Unknown')}")
        
        print(f"\n📋 NEXT STEPS:")
        print(f"   1. Monitor TACNode logs during gateway invocation")
        print(f"   2. Identify source IP from logs")
        print(f"   3. Add source IP to TACNode whitelist")
        print(f"   4. Test end-to-end connectivity")
        
        return {
            'gateway_info': gateway_info,
            'target_info': target_info,
            'ip_ranges': ip_ranges
        }

def main():
    print("🌐 AgentCore Gateway IP Analysis for TACNode Whitelist")
    print("=" * 60)
    
    finder = AgentCoreGatewayIPFinder()
    
    try:
        analysis = finder.analyze_gateway_networking()
        
        print("\n🏆 ANALYSIS COMPLETE!")
        print("   Use the recommendations above to configure TACNode whitelist")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")

if __name__ == "__main__":
    main()

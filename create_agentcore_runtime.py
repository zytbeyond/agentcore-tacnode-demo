#!/usr/bin/env python3
"""
Create Bedrock AgentCore Runtime for TACNode Context Lake Integration
"""

import boto3
import json
import time
import os
from datetime import datetime

class AgentCoreRuntimeManager:
    """Manage Bedrock AgentCore Runtime creation and deployment"""
    
    def __init__(self):
        self.bedrock_agentcore_control = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
        self.bedrock_agentcore = boto3.client('bedrock-agentcore', region_name='us-east-1')
        self.iam = boto3.client('iam', region_name='us-east-1')
        self.gateway_id = "tacnodecontextlakegateway-bkq6ozcvxp"
        self.gateway_arn = "arn:aws:bedrock-agentcore:us-east-1:560155322832:gateway/tacnodecontextlakegateway-bkq6ozcvxp"
        
    def create_runtime_service_role(self):
        """Create IAM service role for AgentCore Runtime"""
        print("🔐 Creating AgentCore Runtime service role...")
        
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "bedrock-agentcore.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole",
                    "Condition": {
                        "StringEquals": {
                            "aws:SourceAccount": "560155322832"
                        }
                    }
                }
            ]
        }
        
        runtime_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "bedrock:InvokeModel",
                        "bedrock:InvokeModelWithResponseStream"
                    ],
                    "Resource": [
                        "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0",
                        "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-haiku-20241022-v1:0"
                    ]
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "bedrock-agentcore:InvokeGateway",
                        "bedrock-agentcore:GetGateway",
                        "bedrock-agentcore:ListGateways"
                    ],
                    "Resource": [
                        self.gateway_arn,
                        "arn:aws:bedrock-agentcore:us-east-1:560155322832:gateway/*"
                    ]
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents"
                    ],
                    "Resource": "arn:aws:logs:us-east-1:560155322832:*"
                }
            ]
        }
        
        role_name = "AmazonBedrockAgentCoreRuntimeServiceRole"
        
        try:
            # Create role
            role_response = self.iam.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description="Service role for Bedrock AgentCore Runtime to access TACNode Context Lake",
                MaxSessionDuration=3600
            )
            
            role_arn = role_response['Role']['Arn']
            print(f"✅ Created runtime service role: {role_arn}")
            
            # Create and attach policy
            policy_name = "AmazonBedrockAgentCoreRuntimePolicy"
            policy_response = self.iam.create_policy(
                PolicyName=policy_name,
                PolicyDocument=json.dumps(runtime_policy),
                Description="Policy for Bedrock AgentCore Runtime to access models and gateways"
            )
            
            policy_arn = policy_response['Policy']['Arn']
            print(f"✅ Created runtime policy: {policy_arn}")
            
            # Attach policy to role
            self.iam.attach_role_policy(
                RoleName=role_name,
                PolicyArn=policy_arn
            )
            
            print("✅ Attached policy to role")
            
            # Wait for role to be available
            print("⏳ Waiting for role to be available...")
            time.sleep(10)
            
            return role_arn
            
        except self.iam.exceptions.EntityAlreadyExistsException:
            print("✅ Runtime service role already exists")
            role_arn = f"arn:aws:iam::560155322832:role/{role_name}"
            return role_arn
        except Exception as e:
            print(f"❌ Error creating runtime service role: {e}")
            return None
    
    def create_runtime(self, role_arn):
        """Create Bedrock AgentCore Runtime"""
        print("🚀 Creating Bedrock AgentCore Runtime...")
        
        runtime_config = {
            'name': 'TACNodeContextLakeRuntime',
            'description': 'AgentCore Runtime for TACNode Context Lake real-time data analytics',
            'roleArn': role_arn,
            'runtimeConfiguration': {
                'compute': {
                    'type': 'SERVERLESS'
                },
                'networking': {
                    'type': 'PUBLIC'
                }
            },
            'tags': {
                'Project': 'TACNodeContextLakeDemo',
                'Environment': 'Demo',
                'Purpose': 'AgentCoreIntegration'
            }
        }
        
        try:
            response = self.bedrock_agentcore_control.create_agent_runtime(**runtime_config)
            
            runtime_arn = response['runtimeArn']
            runtime_id = response['runtimeId']
            
            print(f"✅ Created AgentCore Runtime:")
            print(f"   Runtime ARN: {runtime_arn}")
            print(f"   Runtime ID: {runtime_id}")
            
            # Save runtime configuration
            runtime_info = {
                'runtimeArn': runtime_arn,
                'runtimeId': runtime_id,
                'name': runtime_config['name'],
                'description': runtime_config['description'],
                'roleArn': role_arn,
                'gatewayId': self.gateway_id,
                'gatewayArn': self.gateway_arn,
                'createdAt': datetime.now().isoformat(),
                'status': 'CREATING'
            }
            
            with open('tacnode-agentcore-runtime.json', 'w') as f:
                json.dump(runtime_info, f, indent=2)
            
            print("✅ Runtime configuration saved to: tacnode-agentcore-runtime.json")
            
            return runtime_id, runtime_arn
            
        except Exception as e:
            print(f"❌ Error creating runtime: {e}")
            return None, None
    
    def wait_for_runtime_ready(self, runtime_id):
        """Wait for runtime to be ready"""
        print("⏳ Waiting for runtime to be ready...")
        
        max_attempts = 30
        attempt = 0
        
        while attempt < max_attempts:
            try:
                response = self.bedrock_agentcore_control.get_agent_runtime(agentRuntimeId=runtime_id)
                status = response['status']
                
                print(f"   Runtime status: {status} (attempt {attempt + 1}/{max_attempts})")
                
                if status == 'ACTIVE':
                    print("✅ Runtime is ready!")
                    return True
                elif status in ['FAILED', 'DELETING', 'DELETED']:
                    print(f"❌ Runtime failed with status: {status}")
                    return False
                
                time.sleep(10)
                attempt += 1
                
            except Exception as e:
                print(f"❌ Error checking runtime status: {e}")
                time.sleep(10)
                attempt += 1
        
        print("❌ Timeout waiting for runtime to be ready")
        return False
    
    def create_agent_configuration(self, runtime_id):
        """Create agent configuration for the runtime"""
        print("🤖 Creating agent configuration...")
        
        agent_config = {
            'name': 'TACNodeDataAnalyst',
            'description': 'AI agent for analyzing TACNode Context Lake business data',
            'runtimeId': runtime_id,
            'foundationModel': 'anthropic.claude-3-5-sonnet-20241022-v2:0',
            'instruction': '''You are a business data analyst AI agent with access to real-time business data through TACNode Context Lake.

Your capabilities include:
- Querying live business data from TACNode Context Lake
- Performing data analytics and generating insights
- Answering questions about business metrics, trends, and patterns
- Providing data-driven recommendations

You have access to business records with the following structure:
- id: Unique identifier
- category: Business category (Category 1, 2, 3)
- value: Monetary value (can be positive or negative)
- timestamp: When the record was created
- active: Whether the record is currently active

Use the TACNode Context Lake tools to query data and provide accurate, insightful responses based on real data.''',
            'gateways': [
                {
                    'gatewayId': self.gateway_id,
                    'alias': 'tacnode_data'
                }
            ],
            'guardrailConfiguration': {
                'guardrailIdentifier': 'NONE'
            }
        }
        
        try:
            response = self.bedrock_agentcore.create_agent(**agent_config)
            
            agent_arn = response['agentArn']
            agent_id = response['agentId']
            
            print(f"✅ Created AI Agent:")
            print(f"   Agent ARN: {agent_arn}")
            print(f"   Agent ID: {agent_id}")
            
            # Save agent configuration
            agent_info = {
                'agentArn': agent_arn,
                'agentId': agent_id,
                'name': agent_config['name'],
                'description': agent_config['description'],
                'runtimeId': runtime_id,
                'foundationModel': agent_config['foundationModel'],
                'gatewayId': self.gateway_id,
                'createdAt': datetime.now().isoformat(),
                'status': 'CREATING'
            }
            
            with open('tacnode-agentcore-agent.json', 'w') as f:
                json.dump(agent_info, f, indent=2)
            
            print("✅ Agent configuration saved to: tacnode-agentcore-agent.json")
            
            return agent_id, agent_arn
            
        except Exception as e:
            print(f"❌ Error creating agent: {e}")
            return None, None

def main():
    print("🚀 Creating Bedrock AgentCore Runtime for TACNode Context Lake")
    print("=" * 70)
    
    manager = AgentCoreRuntimeManager()
    
    try:
        # Step 1: Create service role
        role_arn = manager.create_runtime_service_role()
        if not role_arn:
            print("❌ Failed to create service role")
            return
        
        # Step 2: Create runtime
        runtime_id, runtime_arn = manager.create_runtime(role_arn)
        if not runtime_id:
            print("❌ Failed to create runtime")
            return
        
        # Step 3: Wait for runtime to be ready
        if not manager.wait_for_runtime_ready(runtime_id):
            print("❌ Runtime failed to become ready")
            return
        
        # Step 4: Create agent
        agent_id, agent_arn = manager.create_agent_configuration(runtime_id)
        if not agent_id:
            print("❌ Failed to create agent")
            return
        
        print("\n" + "="*70)
        print("🎉 BEDROCK AGENTCORE RUNTIME SETUP COMPLETE!")
        print("="*70)
        
        print("\n✅ INFRASTRUCTURE CREATED:")
        print(f"   🏗️  Runtime ID: {runtime_id}")
        print(f"   🤖 Agent ID: {agent_id}")
        print(f"   🌉 Gateway ID: {manager.gateway_id}")
        print(f"   🔐 Service Role: {role_arn}")
        
        print("\n✅ CAPABILITIES ENABLED:")
        print("   📊 Real-time TACNode Context Lake data access")
        print("   🤖 AI-powered business data analysis")
        print("   🔍 Live data querying and insights")
        print("   📈 Business metrics and trend analysis")
        
        print("\n🎯 NEXT STEPS:")
        print("   1. Test the agent with real queries")
        print("   2. Query business data through the runtime")
        print("   3. Generate insights from TACNode Context Lake")
        print("   4. Demonstrate end-to-end functionality")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")

if __name__ == "__main__":
    main()

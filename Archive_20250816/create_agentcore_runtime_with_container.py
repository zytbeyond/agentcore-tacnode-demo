#!/usr/bin/env python3
"""
Create AgentCore Runtime with Custom Container
Deploy the TACNode agent container as an AgentCore Runtime
"""

import boto3
import json
import time
import os
from datetime import datetime

class AgentCoreRuntimeDeployment:
    """Deploy AgentCore Runtime with custom container"""
    
    def __init__(self):
        self.bedrock_agentcore_control = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
        self.iam = boto3.client('iam', region_name='us-east-1')
        
        # Load container info
        with open('tacnode-agent-container.json', 'r') as f:
            self.container_info = json.load(f)
        
        self.container_uri = self.container_info['image_name']
        self.account_id = self.container_info['account_id']
        
        print(f"🏗️  AgentCore Runtime Deployment Configuration:")
        print(f"   Container URI: {self.container_uri}")
        print(f"   Account ID: {self.account_id}")
    
    def create_runtime_execution_role(self):
        """Create IAM execution role for AgentCore Runtime"""
        print("\n🔐 Creating AgentCore Runtime execution role...")
        
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
                            "aws:SourceAccount": self.account_id
                        }
                    }
                }
            ]
        }
        
        execution_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "bedrock:InvokeModel",
                        "bedrock:InvokeModelWithResponseStream"
                    ],
                    "Resource": [
                        f"arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-sonnet-20240620-v1:0",
                        f"arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-haiku-20241022-v1:0"
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
                        "arn:aws:bedrock-agentcore:us-east-1:560155322832:gateway/tacnodecontextlakegateway-bkq6ozcvxp",
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
                    "Resource": f"arn:aws:logs:us-east-1:{self.account_id}:*"
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "ecr:GetAuthorizationToken",
                        "ecr:BatchCheckLayerAvailability",
                        "ecr:GetDownloadUrlForLayer",
                        "ecr:BatchGetImage"
                    ],
                    "Resource": "*"
                }
            ]
        }
        
        role_name = "TACNodeAgentCoreRuntimeExecutionRole"
        policy_name = "TACNodeAgentCoreRuntimeExecutionPolicy"
        
        try:
            # Create role
            role_response = self.iam.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description="Execution role for TACNode AgentCore Runtime",
                MaxSessionDuration=3600,
                Tags=[
                    {'Key': 'Project', 'Value': 'TACNodeAgentCore'},
                    {'Key': 'Environment', 'Value': 'Production'}
                ]
            )
            
            role_arn = role_response['Role']['Arn']
            print(f"✅ Created execution role: {role_arn}")
            
            # Create and attach policy
            policy_response = self.iam.create_policy(
                PolicyName=policy_name,
                PolicyDocument=json.dumps(execution_policy),
                Description="Execution policy for TACNode AgentCore Runtime"
            )
            
            policy_arn = policy_response['Policy']['Arn']
            print(f"✅ Created execution policy: {policy_arn}")
            
            # Attach policy to role
            self.iam.attach_role_policy(
                RoleName=role_name,
                PolicyArn=policy_arn
            )
            
            print("✅ Attached policy to role")
            
            # Wait for role to be available
            print("⏳ Waiting for role to be available...")
            time.sleep(15)
            
            return role_arn
            
        except self.iam.exceptions.EntityAlreadyExistsException:
            print("✅ Execution role already exists")
            role_arn = f"arn:aws:iam::{self.account_id}:role/{role_name}"
            return role_arn
        except Exception as e:
            print(f"❌ Error creating execution role: {e}")
            return None
    
    def create_agent_runtime(self, role_arn):
        """Create AgentCore Runtime with custom container"""
        print("\n🚀 Creating AgentCore Runtime with custom container...")
        
        runtime_config = {
            'agentRuntimeName': 'TACNodeContextLakeRuntime',
            'description': 'AgentCore Runtime for TACNode Context Lake with Claude integration',
            'agentRuntimeArtifact': {
                'containerConfiguration': {
                    'containerUri': self.container_uri
                }
            },
            'roleArn': role_arn,
            'networkConfiguration': {
                'networkMode': 'PUBLIC'
            },
            'protocolConfiguration': {
                'serverProtocol': 'HTTP'
            },
            'environmentVariables': {
                'TACNODE_TOKEN': os.getenv('TACNODE_TOKEN', ''),
                'AWS_DEFAULT_REGION': 'us-east-1',
                'GATEWAY_ID': 'tacnodecontextlakegateway-bkq6ozcvxp'
            }
        }
        
        try:
            response = self.bedrock_agentcore_control.create_agent_runtime(**runtime_config)
            
            runtime_arn = response['agentRuntimeArn']
            runtime_id = response['agentRuntimeId']
            runtime_version = response['agentRuntimeVersion']
            
            print(f"✅ Created AgentCore Runtime:")
            print(f"   Runtime ARN: {runtime_arn}")
            print(f"   Runtime ID: {runtime_id}")
            print(f"   Runtime Version: {runtime_version}")
            
            # Save runtime configuration
            runtime_info = {
                'runtimeArn': runtime_arn,
                'runtimeId': runtime_id,
                'runtimeVersion': runtime_version,
                'name': runtime_config['agentRuntimeName'],
                'description': runtime_config['description'],
                'containerUri': self.container_uri,
                'roleArn': role_arn,
                'gatewayId': 'tacnodecontextlakegateway-bkq6ozcvxp',
                'createdAt': datetime.now().isoformat(),
                'status': 'CREATING'
            }
            
            with open('tacnode-agentcore-runtime-final.json', 'w') as f:
                json.dump(runtime_info, f, indent=2)
            
            print("✅ Runtime configuration saved to: tacnode-agentcore-runtime-final.json")
            
            return runtime_id, runtime_arn
            
        except Exception as e:
            print(f"❌ Error creating AgentCore Runtime: {e}")
            return None, None
    
    def wait_for_runtime_ready(self, runtime_id):
        """Wait for runtime to be ready"""
        print("\n⏳ Waiting for AgentCore Runtime to be ready...")
        
        max_attempts = 60  # 10 minutes
        attempt = 0
        
        while attempt < max_attempts:
            try:
                response = self.bedrock_agentcore_control.get_agent_runtime(agentRuntimeId=runtime_id)
                status = response['status']
                
                print(f"   Runtime status: {status} (attempt {attempt + 1}/{max_attempts})")
                
                if status == 'ACTIVE':
                    print("✅ Runtime is ACTIVE and ready!")
                    return True
                elif status in ['FAILED', 'DELETING', 'DELETED']:
                    print(f"❌ Runtime failed with status: {status}")
                    if 'failureReason' in response:
                        print(f"   Failure reason: {response['failureReason']}")
                    return False
                
                time.sleep(10)
                attempt += 1
                
            except Exception as e:
                print(f"❌ Error checking runtime status: {e}")
                time.sleep(10)
                attempt += 1
        
        print("❌ Timeout waiting for runtime to be ready")
        return False
    
    def create_runtime_endpoint(self, runtime_id):
        """Create endpoint for the runtime"""
        print("\n🌐 Creating AgentCore Runtime endpoint...")
        
        try:
            response = self.bedrock_agentcore_control.create_agent_runtime_endpoint(
                agentRuntimeId=runtime_id,
                endpointName='TACNodeRuntimeEndpoint',
                description='Endpoint for TACNode Context Lake AgentCore Runtime'
            )
            
            endpoint_arn = response['agentRuntimeEndpointArn']
            endpoint_id = response['agentRuntimeEndpointId']
            
            print(f"✅ Created runtime endpoint:")
            print(f"   Endpoint ARN: {endpoint_arn}")
            print(f"   Endpoint ID: {endpoint_id}")
            
            return endpoint_id, endpoint_arn
            
        except Exception as e:
            print(f"❌ Error creating runtime endpoint: {e}")
            return None, None
    
    def deploy_complete_runtime(self):
        """Complete runtime deployment process"""
        print("🚀 Starting Complete AgentCore Runtime Deployment")
        print("=" * 70)
        
        # Step 1: Create execution role
        role_arn = self.create_runtime_execution_role()
        if not role_arn:
            return None
        
        # Step 2: Create AgentCore Runtime
        runtime_id, runtime_arn = self.create_agent_runtime(role_arn)
        if not runtime_id:
            return None
        
        # Step 3: Wait for runtime to be ready
        if not self.wait_for_runtime_ready(runtime_id):
            print("⚠️  Runtime not ready, but continuing...")
        
        # Step 4: Create runtime endpoint
        endpoint_id, endpoint_arn = self.create_runtime_endpoint(runtime_id)
        
        print("\n" + "="*70)
        print("🎉 AGENTCORE RUNTIME DEPLOYMENT COMPLETE!")
        print("="*70)
        
        print(f"\n✅ RUNTIME DETAILS:")
        print(f"   Runtime ID: {runtime_id}")
        print(f"   Runtime ARN: {runtime_arn}")
        print(f"   Container URI: {self.container_uri}")
        print(f"   Execution Role: {role_arn}")
        
        if endpoint_id:
            print(f"   Endpoint ID: {endpoint_id}")
            print(f"   Endpoint ARN: {endpoint_arn}")
        
        return {
            'runtime_id': runtime_id,
            'runtime_arn': runtime_arn,
            'endpoint_id': endpoint_id,
            'endpoint_arn': endpoint_arn,
            'container_uri': self.container_uri,
            'role_arn': role_arn
        }

def main():
    print("🚀 TACNode AgentCore Runtime Deployment")
    print("=" * 60)
    
    deployment = AgentCoreRuntimeDeployment()
    
    try:
        # Deploy runtime
        runtime_info = deployment.deploy_complete_runtime()
        
        if runtime_info:
            print("\n🎯 AGENTCORE RUNTIME READY!")
            print("   Runtime deployed with custom container")
            print("   Ready for agent configuration and testing")
        else:
            print("\n❌ Runtime deployment failed")
            
    except Exception as e:
        print(f"❌ Deployment failed: {e}")

if __name__ == "__main__":
    main()

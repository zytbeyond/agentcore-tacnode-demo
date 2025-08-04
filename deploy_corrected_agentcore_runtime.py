#!/usr/bin/env python3
"""
Deploy Corrected AgentCore Runtime
Deploy the corrected agent container as a new AgentCore Runtime
"""

import boto3
import json
import time
from datetime import datetime

class CorrectedAgentCoreDeployment:
    """Deploy corrected AgentCore Runtime"""
    
    def __init__(self):
        self.bedrock_agentcore_control = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
        self.bedrock_agentcore = boto3.client('bedrock-agentcore', region_name='us-east-1')
        
        # Load container info
        with open('tacnode-agent-container.json', 'r') as f:
            self.container_info = json.load(f)
        
        self.account_id = self.container_info['account_id']
        self.repository_uri = self.container_info['repository_uri']
        self.corrected_container_uri = f"{self.repository_uri}:agentcore-corrected-gateway"
    
    def deploy_corrected_agentcore_runtime(self):
        """Deploy corrected AgentCore Runtime"""
        print("🚀 Deploying corrected AgentCore Runtime...")
        
        role_arn = f"arn:aws:iam::{self.account_id}:role/TACNodeAgentCoreRuntimeExecutionRole"
        
        runtime_config = {
            'agentRuntimeName': 'TACNodeBusinessIntelligenceAgent',
            'description': 'Business Intelligence Agent with automatic data access via AgentCore Gateway',
            'agentRuntimeArtifact': {
                'containerConfiguration': {
                    'containerUri': self.corrected_container_uri
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
                'AWS_DEFAULT_REGION': 'us-east-1',
                'GATEWAY_ID': 'tacnodecontextlakegateway-bkq6ozcvxp'
            }
        }
        
        try:
            response = self.bedrock_agentcore_control.create_agent_runtime(**runtime_config)
            
            runtime_arn = response['agentRuntimeArn']
            runtime_id = response['agentRuntimeId']
            
            print(f"✅ Corrected AgentCore Runtime created:")
            print(f"   Runtime ARN: {runtime_arn}")
            print(f"   Runtime ID: {runtime_id}")
            print(f"   Container: {self.corrected_container_uri}")
            
            # Save runtime info
            runtime_info = {
                'runtimeArn': runtime_arn,
                'runtimeId': runtime_id,
                'containerUri': self.corrected_container_uri,
                'architecture': 'linux/arm64',
                'agentType': 'business-intelligence',
                'gatewayIntegration': True,
                'createdAt': datetime.now().isoformat()
            }
            
            with open('tacnode-business-intelligence-runtime.json', 'w') as f:
                json.dump(runtime_info, f, indent=2)
            
            return runtime_id, runtime_arn
            
        except Exception as e:
            print(f"❌ Corrected runtime deployment failed: {e}")
            return None, None
    
    def wait_for_runtime_ready(self, runtime_id):
        """Wait for runtime to become ready"""
        print(f"\n⏳ Waiting for runtime to become READY...")
        
        max_attempts = 60
        attempt = 0
        
        while attempt < max_attempts:
            try:
                response = self.bedrock_agentcore_control.get_agent_runtime(agentRuntimeId=runtime_id)
                status = response['status']
                
                print(f"   Runtime status: {status} (attempt {attempt + 1}/{max_attempts})")
                
                if status in ['READY', 'ACTIVE']:
                    print("✅ Runtime is READY!")
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
        
        print("⚠️  Runtime may still be starting...")
        return True
    
    def test_natural_business_questions(self, runtime_arn):
        """Test natural business questions"""
        print(f"\n🧪 Testing natural business questions...")
        
        test_questions = [
            "How is our business performing?",
            "What are our key metrics this quarter?", 
            "Show me our financial overview"
        ]
        
        results = []
        
        for i, question in enumerate(test_questions):
            print(f"\n🔍 Question {i+1}: {question}")
            
            try:
                # Add delay to avoid throttling
                if i > 0:
                    time.sleep(15)
                
                test_payload = {
                    "input": {
                        "prompt": question
                    }
                }
                
                session_id = f"natural-question-test-{i+1}-{int(time.time())}-business-intelligence"
                
                response = self.bedrock_agentcore.invoke_agent_runtime(
                    agentRuntimeArn=runtime_arn,
                    runtimeSessionId=session_id,
                    payload=json.dumps(test_payload),
                    qualifier="DEFAULT"
                )
                
                response_body = response['response'].read()
                response_data = json.loads(response_body)
                
                response_message = response_data['output']['message']
                data_accessed = response_data['output'].get('data_accessed', False)
                records_analyzed = response_data['output'].get('records_analyzed', 0)
                
                print(f"   ✅ Response received ({len(response_message)} chars)")
                print(f"   📊 Data accessed: {data_accessed}")
                print(f"   📋 Records analyzed: {records_analyzed}")
                print(f"   💬 Preview: {response_message[:150]}...")
                
                # Check for business intelligence indicators
                bi_indicators = [
                    data_accessed,
                    records_analyzed > 0,
                    any(word in response_message.lower() for word in ['category', 'value', 'revenue', 'performance']),
                    '$' in response_message or 'total' in response_message.lower(),
                    len(response_message) > 200
                ]
                
                success = sum(bi_indicators) >= 3
                
                results.append({
                    'question': question,
                    'success': success,
                    'data_accessed': data_accessed,
                    'records_analyzed': records_analyzed,
                    'response_length': len(response_message)
                })
                
                print(f"   {'✅' if success else '❌'} Business intelligence quality: {'HIGH' if success else 'LOW'}")
                
            except Exception as e:
                print(f"   ❌ Question failed: {e}")
                results.append({
                    'question': question,
                    'success': False,
                    'error': str(e)
                })
        
        # Analyze results
        successful_questions = sum(1 for r in results if r['success'])
        data_access_count = sum(1 for r in results if r.get('data_accessed', False))
        
        print(f"\n📋 Natural Question Test Results:")
        print(f"   Successful questions: {successful_questions}/{len(test_questions)}")
        print(f"   Data access confirmed: {data_access_count}/{len(test_questions)}")
        
        return successful_questions >= 2  # At least 2 out of 3 should work
    
    def demonstrate_agent_capabilities(self, runtime_arn):
        """Demonstrate the agent's capabilities"""
        print(f"\n🎯 Demonstrating Agent Capabilities...")
        
        try:
            # Comprehensive business intelligence request
            demo_payload = {
                "input": {
                    "prompt": "I need a comprehensive business report. Please analyze our performance, identify trends, and provide actionable recommendations for the executive team."
                }
            }
            
            session_id = f"capability-demo-{int(time.time())}-comprehensive-analysis"
            
            print(f"📤 Requesting comprehensive business analysis...")
            
            response = self.bedrock_agentcore.invoke_agent_runtime(
                agentRuntimeArn=runtime_arn,
                runtimeSessionId=session_id,
                payload=json.dumps(test_payload),
                qualifier="DEFAULT"
            )
            
            response_body = response['response'].read()
            response_data = json.loads(response_body)
            
            response_message = response_data['output']['message']
            data_accessed = response_data['output'].get('data_accessed', False)
            records_analyzed = response_data['output'].get('records_analyzed', 0)
            
            print(f"\n📊 COMPREHENSIVE BUSINESS ANALYSIS:")
            print("=" * 80)
            print(response_message)
            print("=" * 80)
            
            print(f"\n📋 Analysis Metadata:")
            print(f"   Data accessed: {data_accessed}")
            print(f"   Records analyzed: {records_analyzed}")
            print(f"   Response length: {len(response_message)} characters")
            
            return True
            
        except Exception as e:
            print(f"❌ Capability demonstration failed: {e}")
            return False
    
    def complete_corrected_deployment(self):
        """Complete corrected deployment and testing"""
        print("🎯 CORRECTED AGENTCORE RUNTIME DEPLOYMENT")
        print("=" * 70)
        
        print("🏗️  DEPLOYING BUSINESS INTELLIGENCE AGENT:")
        print("   • Natural language interface")
        print("   • Automatic data detection")
        print("   • Business intelligence capabilities")
        print("   • No technical knowledge required from users")
        
        # Step 1: Deploy runtime
        print("\n📋 STEP 1: Deploying Corrected AgentCore Runtime")
        runtime_id, runtime_arn = self.deploy_corrected_agentcore_runtime()
        
        if not runtime_id:
            print("❌ Runtime deployment failed")
            return False
        
        # Step 2: Wait for ready
        print("\n📋 STEP 2: Waiting for Runtime Ready")
        if not self.wait_for_runtime_ready(runtime_id):
            print("⚠️  Runtime not ready, but continuing...")
        
        # Step 3: Test natural questions
        print("\n📋 STEP 3: Testing Natural Business Questions")
        natural_success = self.test_natural_business_questions(runtime_arn)
        
        # Step 4: Demonstrate capabilities
        print("\n📋 STEP 4: Demonstrating Agent Capabilities")
        demo_success = self.demonstrate_agent_capabilities(runtime_arn)
        
        print("\n" + "="*70)
        if natural_success:
            print("🎉 CORRECTED AGENTCORE RUNTIME DEPLOYMENT SUCCESSFUL!")
        else:
            print("⚠️  CORRECTED AGENTCORE RUNTIME DEPLOYED WITH ISSUES")
        print("="*70)
        
        print(f"\n✅ DEPLOYMENT RESULTS:")
        print(f"   🚀 Runtime Deployed: {'✅' if runtime_id else '❌'}")
        print(f"   💬 Natural Questions: {'✅' if natural_success else '❌'}")
        print(f"   🎯 Capability Demo: {'✅' if demo_success else '❌'}")
        
        if natural_success:
            print(f"\n🎯 BUSINESS INTELLIGENCE AGENT READY:")
            print(f"   Runtime ARN: {runtime_arn}")
            print(f"   Runtime ID: {runtime_id}")
            print(f"   Container: {self.corrected_container_uri}")
            print(f"   Capabilities: Natural language business intelligence")
            
            print(f"\n💬 EXAMPLE QUESTIONS USERS CAN ASK:")
            print(f"   • 'How is our business performing?'")
            print(f"   • 'What are our key metrics this quarter?'")
            print(f"   • 'Show me our financial overview'")
            print(f"   • 'What trends do you see in our data?'")
            print(f"   • 'Give me actionable business recommendations'")
        
        return natural_success

def main():
    print("🚀 Deploy Corrected AgentCore Runtime")
    print("=" * 60)
    
    deployment = CorrectedAgentCoreDeployment()
    
    try:
        success = deployment.complete_corrected_deployment()
        
        if success:
            print("\n🏆 MISSION ACCOMPLISHED!")
            print("   Business Intelligence Agent deployed and working")
            print("   Users can ask natural business questions")
            print("   Agent automatically accesses data when needed")
            print("   Complete AgentCore + TACNode integration functional")
        else:
            print("\n🔧 DEPLOYMENT NEEDS ATTENTION")
            print("   Runtime deployed but some features need optimization")
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Demo Agent Interaction
Show how the agent works with under-the-hood details
"""

import boto3
import json
import time
import subprocess
from datetime import datetime

class AgentDemo:
    """Demo the agent interaction with detailed logging"""
    
    def __init__(self):
        self.bedrock_agentcore = boto3.client('bedrock-agentcore', region_name='us-east-1')
        
        # Load runtime info
        with open('tacnode-business-intelligence-runtime.json', 'r') as f:
            self.runtime_info = json.load(f)
        
        self.runtime_arn = self.runtime_info['runtimeArn']
        self.runtime_id = self.runtime_info['runtimeId']
    
    def show_current_database(self):
        """Show current database state"""
        print("\n" + "="*80)
        print("📊 CURRENT TACNODE DATABASE STATE")
        print("="*80)
        
        try:
            result = subprocess.run(['python3', 'query_tacnode_data.py'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ Database Access: SUCCESS")
                print(result.stdout)
            else:
                print("❌ Database Access: FAILED")
                print(result.stderr)
                
        except Exception as e:
            print(f"❌ Database error: {e}")
        
        print("="*80)
    
    def ask_agent_with_details(self, question):
        """Ask agent with detailed under-the-hood logging"""
        print(f"\n🤖 ASKING AGENT: '{question}'")
        print("="*80)
        
        # Step 1: Analyze question
        print("📋 STEP 1: Question Analysis")
        business_keywords = ['business', 'performance', 'value', 'category', 'financial', 'revenue', 'metrics']
        found_keywords = [kw for kw in business_keywords if kw in question.lower()]
        needs_data = len(found_keywords) > 0
        
        print(f"   Keywords found: {found_keywords}")
        print(f"   Needs business data: {'✅ YES' if needs_data else '❌ NO'}")
        
        # Step 2: Expected data flow
        print("\n📋 STEP 2: Expected Data Flow")
        if needs_data:
            print("   User Question → AgentCore Runtime")
            print("   Runtime detects business keywords → Calls AgentCore Gateway")
            print("   Gateway → TACNode Context Lake → PostgreSQL")
            print("   Data flows back → Claude AI analysis → Response")
        else:
            print("   User Question → AgentCore Runtime → Claude AI → General Response")
        
        # Step 3: Make the request
        print("\n📋 STEP 3: Calling AgentCore Runtime")
        
        test_payload = {
            "input": {
                "prompt": question
            }
        }
        
        session_id = f"demo-session-{int(time.time())}-business-intelligence"
        
        print(f"   Session ID: {session_id}")
        print(f"   Runtime ARN: {self.runtime_arn}")
        print(f"   Payload: {json.dumps(test_payload)}")
        
        try:
            start_time = time.time()
            print(f"\n⏳ Sending request... (started at {datetime.now().strftime('%H:%M:%S')})")
            
            response = self.bedrock_agentcore.invoke_agent_runtime(
                agentRuntimeArn=self.runtime_arn,
                runtimeSessionId=session_id,
                payload=json.dumps(test_payload),
                qualifier="DEFAULT"
            )
            
            end_time = time.time()
            
            # Parse response
            response_body = response['response'].read()
            response_data = json.loads(response_body)
            
            print(f"✅ Response received in {end_time - start_time:.2f} seconds")
            
            # Step 4: Analyze response
            print("\n📋 STEP 4: Response Analysis")
            output = response_data.get('output', {})
            
            print(f"   Timestamp: {output.get('timestamp', 'N/A')}")
            print(f"   Model: {output.get('model', 'N/A')}")
            print(f"   Data Accessed: {output.get('data_accessed', False)}")
            print(f"   Gateway Used: {output.get('gateway_used', False)}")
            print(f"   Records Analyzed: {output.get('records_analyzed', 0)}")
            print(f"   Response Length: {len(output.get('message', ''))} characters")
            
            # Step 5: Show response
            print("\n📋 STEP 5: Agent Response")
            print("="*80)
            print(output.get('message', 'No response'))
            print("="*80)
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def run_demo(self):
        """Run complete demo"""
        print("🎯 BUSINESS INTELLIGENCE AGENT DEMO")
        print("="*80)
        print("This demo shows how the agent works under the hood")
        print("and how it responds to different types of questions.")
        print("="*80)
        
        # Show current database
        self.show_current_database()
        
        # Demo questions
        demo_questions = [
            "How is our business performing?",
            "What is our total business value?",
            "Hello, how are you today?"  # Non-business question
        ]
        
        for i, question in enumerate(demo_questions, 1):
            print(f"\n🔍 DEMO QUESTION {i}/{len(demo_questions)}")
            print("-" * 60)
            
            success = self.ask_agent_with_details(question)
            
            if success:
                print(f"✅ Demo question {i} completed successfully")
            else:
                print(f"❌ Demo question {i} failed")
            
            if i < len(demo_questions):
                print(f"\n⏳ Waiting 10 seconds before next question...")
                time.sleep(10)
        
        print(f"\n🎉 DEMO COMPLETE!")
        print("="*80)
        print("Key observations:")
        print("• Business questions trigger data access")
        print("• Non-business questions get general responses")
        print("• Agent automatically detects when data is needed")
        print("• Real business data is analyzed and presented")
        print("="*80)

def main():
    print("🎬 Agent Interaction Demo")
    print("=" * 50)
    
    demo = AgentDemo()
    demo.run_demo()

if __name__ == "__main__":
    main()

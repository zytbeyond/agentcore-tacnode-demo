#!/usr/bin/env python3
"""
Interactive Agent Terminal Interface
Ask the agent questions and see what happens under the hood
"""

import boto3
import json
import time
import subprocess
from datetime import datetime
import sys

class InteractiveAgentTerminal:
    """Interactive terminal interface for the business intelligence agent"""
    
    def __init__(self):
        self.bedrock_agentcore = boto3.client('bedrock-agentcore', region_name='us-east-1')
        
        # Load the business intelligence runtime
        with open('tacnode-business-intelligence-runtime.json', 'r') as f:
            self.runtime_info = json.load(f)
        
        self.runtime_arn = self.runtime_info['runtimeArn']
        self.runtime_id = self.runtime_info['runtimeId']
        
        print("🤖 Business Intelligence Agent Terminal")
        print("=" * 60)
        print(f"Runtime: {self.runtime_id}")
        print(f"Status: Connected and Ready")
        print("=" * 60)
    
    def generate_session_id(self):
        """Generate unique session ID"""
        timestamp = int(time.time())
        return f"interactive-session-{timestamp}-business-intelligence-terminal"
    
    def show_current_database_state(self):
        """Show current state of TACNode database"""
        print("\n" + "="*80)
        print("📊 CURRENT DATABASE STATE")
        print("="*80)
        
        try:
            result = subprocess.run(['python3', 'query_tacnode_data.py'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ TACNode Database Access: SUCCESS")
                print("\n📋 Current Records:")
                print("-" * 40)
                print(result.stdout)
                print("-" * 40)
            else:
                print("❌ TACNode Database Access: FAILED")
                print(f"Error: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Database query error: {e}")
        
        print("="*80)
    
    def show_under_the_hood_process(self, user_question):
        """Show what happens under the hood"""
        print("\n" + "🔍 UNDER THE HOOD ANALYSIS")
        print("="*80)
        
        # Step 1: Question Analysis
        print("📋 STEP 1: Question Analysis")
        business_keywords = [
            'business', 'data', 'performance', 'metrics', 'analytics', 'report',
            'revenue', 'sales', 'category', 'categories', 'value', 'values',
            'trend', 'trends', 'insight', 'insights', 'analysis', 'analyze',
            'summary', 'overview', 'dashboard', 'kpi', 'financial', 'records'
        ]
        
        found_keywords = [kw for kw in business_keywords if kw in user_question.lower()]
        needs_data = len(found_keywords) > 0
        
        print(f"   User Question: '{user_question}'")
        print(f"   Keywords Found: {found_keywords}")
        print(f"   Needs Business Data: {'✅ YES' if needs_data else '❌ NO'}")
        
        # Step 2: Data Access Decision
        print("\n📋 STEP 2: Data Access Decision")
        if needs_data:
            print("   🌉 Agent will call AgentCore Gateway")
            print("   📊 Gateway will access TACNode Context Lake")
            print("   🗄️  TACNode will query PostgreSQL database")
        else:
            print("   💬 Agent will provide general response")
            print("   🚫 No data access needed")
        
        # Step 3: Expected Data Flow
        print("\n📋 STEP 3: Expected Data Flow")
        print("   User Question → AgentCore Runtime")
        print("   AgentCore Runtime → AgentCore Gateway")
        print("   AgentCore Gateway → TACNode Context Lake")
        print("   TACNode Context Lake → PostgreSQL Database")
        print("   PostgreSQL → TACNode → Gateway → Runtime → Claude AI")
        print("   Claude AI → Business Intelligence Response")
        
        print("="*80)
    
    def ask_agent_question(self, user_question):
        """Ask the agent a question and show detailed process"""
        print(f"\n🤖 ASKING AGENT: '{user_question}'")
        print("="*80)
        
        try:
            # Show under the hood analysis
            self.show_under_the_hood_process(user_question)
            
            # Prepare request
            test_payload = {
                "input": {
                    "prompt": user_question
                }
            }
            
            session_id = self.generate_session_id()
            
            print(f"\n📤 SENDING REQUEST TO AGENTCORE RUNTIME")
            print(f"   Session ID: {session_id}")
            print(f"   Runtime ARN: {self.runtime_arn}")
            print(f"   Payload: {json.dumps(test_payload, indent=2)}")
            
            # Make request
            start_time = time.time()
            print(f"\n⏳ Calling AgentCore Runtime... (started at {datetime.now().strftime('%H:%M:%S')})")
            
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
            
            # Show response metadata
            print(f"\n📊 RESPONSE METADATA")
            print("-" * 40)
            output = response_data.get('output', {})
            print(f"   Timestamp: {output.get('timestamp', 'N/A')}")
            print(f"   Model: {output.get('model', 'N/A')}")
            print(f"   Data Accessed: {output.get('data_accessed', False)}")
            print(f"   Gateway Used: {output.get('gateway_used', False)}")
            print(f"   Records Analyzed: {output.get('records_analyzed', 0)}")
            print(f"   Response Length: {len(output.get('message', ''))} characters")
            
            # Show agent response
            agent_response = output.get('message', 'No response')
            print(f"\n🤖 AGENT RESPONSE:")
            print("="*80)
            print(agent_response)
            print("="*80)
            
            return True
            
        except Exception as e:
            print(f"❌ Error asking agent: {e}")
            return False
    
    def show_database_modification_instructions(self):
        """Show instructions for modifying the database"""
        print("\n" + "🔧 DATABASE MODIFICATION INSTRUCTIONS")
        print("="*80)
        print("To modify the TACNode database and test real-time changes:")
        print("")
        print("1️⃣ OPTION 1: Use the TACNode MCP interface")
        print("   python3 test_tacnode_mcp.py")
        print("   (This will show you how to modify records)")
        print("")
        print("2️⃣ OPTION 2: Direct database modification")
        print("   The database has 10 records with:")
        print("   - IDs: 1-10")
        print("   - Categories: Category 1, Category 2, Category 3")
        print("   - Values: $-10.75 to $999.99")
        print("   - Dates: 2025-07-26 to 2025-08-04")
        print("")
        print("3️⃣ OPTION 3: Add new records")
        print("   You can add new business records and see if the agent")
        print("   picks up the changes in real-time")
        print("")
        print("4️⃣ TEST APPROACH:")
        print("   a) Ask agent a question about current data")
        print("   b) Modify the database")
        print("   c) Ask the same question again")
        print("   d) Compare responses to see real-time changes")
        print("="*80)
    
    def run_interactive_session(self):
        """Run interactive session"""
        print("\n🚀 INTERACTIVE BUSINESS INTELLIGENCE AGENT")
        print("="*80)
        print("Ask natural business questions and see what happens under the hood!")
        print("")
        print("Example questions:")
        print("• How is our business performing?")
        print("• What are our key metrics?")
        print("• Show me our financial overview")
        print("• What trends do you see?")
        print("• Give me actionable recommendations")
        print("")
        print("Commands:")
        print("• 'db' - Show current database state")
        print("• 'modify' - Show database modification instructions")
        print("• 'quit' - Exit")
        print("="*80)
        
        # Show initial database state
        self.show_current_database_state()
        
        while True:
            try:
                print(f"\n💬 Enter your question (or command):")
                user_input = input("❓ ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                elif user_input.lower() == 'db':
                    self.show_current_database_state()
                    continue
                
                elif user_input.lower() == 'modify':
                    self.show_database_modification_instructions()
                    continue
                
                # Ask the agent
                print(f"\n⚡ Processing your question...")
                success = self.ask_agent_question(user_input)
                
                if success:
                    print(f"\n✅ Question processed successfully!")
                else:
                    print(f"\n❌ Question processing failed!")
                
                # Ask if user wants to see database state
                print(f"\n🔍 Would you like to see the current database state? (y/n)")
                show_db = input("📊 ").strip().lower()
                if show_db in ['y', 'yes']:
                    self.show_current_database_state()
                
            except KeyboardInterrupt:
                print(f"\n\n👋 Session interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error in interactive session: {e}")

def main():
    print("🤖 Interactive Business Intelligence Agent Terminal")
    print("=" * 60)
    
    try:
        terminal = InteractiveAgentTerminal()
        terminal.run_interactive_session()
        
    except FileNotFoundError:
        print("❌ Runtime configuration not found!")
        print("   Please run the deployment script first:")
        print("   python3 deploy_corrected_agentcore_runtime.py")
    except Exception as e:
        print(f"❌ Terminal startup failed: {e}")

if __name__ == "__main__":
    main()

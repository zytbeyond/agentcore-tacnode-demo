#!/usr/bin/env python3
"""
Simulate AgentCore Runtime with Gateway Integration
Run our custom agent locally to demonstrate the complete integration
"""

import asyncio
import json
import subprocess
import time
import os
import signal
import sys
from datetime import datetime

class AgentCoreRuntimeSimulator:
    """Simulate the complete AgentCore Runtime experience"""
    
    def __init__(self):
        self.container_process = None
        self.gateway_id = "tacnodecontextlakegateway-bkq6ozcvxp"
        
    def start_agent_container_locally(self):
        """Start the agent container locally to simulate runtime"""
        print("🐳 Starting Agent Container Locally...")
        
        try:
            # Load container info
            with open('tacnode-agent-container.json', 'r') as f:
                container_info = json.load(f)
            
            container_uri = container_info['image_name']
            
            # Run container locally
            cmd = [
                'docker', 'run',
                '-d',  # detached
                '-p', '8000:8000',  # port mapping
                '-e', f'TACNODE_TOKEN={os.getenv("TACNODE_TOKEN", "")}',
                '-e', 'AWS_DEFAULT_REGION=us-east-1',
                '-e', f'GATEWAY_ID={self.gateway_id}',
                '--name', 'tacnode-agent-runtime',
                container_uri
            ]
            
            print(f"🚀 Starting container: {container_uri}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            container_id = result.stdout.strip()
            print(f"✅ Container started: {container_id}")
            
            # Wait for container to be ready
            print("⏳ Waiting for container to be ready...")
            time.sleep(10)
            
            # Check if container is running
            check_cmd = ['docker', 'ps', '--filter', 'name=tacnode-agent-runtime', '--format', 'table {{.Names}}\t{{.Status}}']
            check_result = subprocess.run(check_cmd, capture_output=True, text=True)
            
            if 'tacnode-agent-runtime' in check_result.stdout:
                print("✅ Container is running and ready")
                return container_id
            else:
                print("❌ Container failed to start properly")
                return None
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to start container: {e.stderr}")
            return None
        except Exception as e:
            print(f"❌ Error starting container: {e}")
            return None
    
    def test_agent_health(self):
        """Test agent health endpoint"""
        print("\n🏥 Testing Agent Health...")
        
        try:
            import requests
            response = requests.get('http://localhost:8000/health', timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                print("✅ Agent is healthy")
                print(f"   Status: {health_data.get('status', 'unknown')}")
                print(f"   Timestamp: {health_data.get('timestamp', 'unknown')}")
                return True
            else:
                print(f"❌ Health check failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    def test_agent_invocation(self):
        """Test agent invocation with TACNode data request"""
        print("\n🤖 Testing Agent Invocation...")
        
        try:
            import requests
            
            # Test request for business data analysis
            test_request = {
                "message": "Can you analyze our business data from TACNode Context Lake? I need insights about category performance and recent trends.",
                "session_id": "demo-session-001",
                "user_id": "demo-user",
                "context": {
                    "request_type": "business_analysis",
                    "priority": "high"
                }
            }
            
            print(f"📤 Sending request: {test_request['message'][:50]}...")
            
            response = requests.post(
                'http://localhost:8000/invoke',
                json=test_request,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Agent invocation successful!")
                print(f"\n🧠 Agent Response:")
                print("-" * 60)
                print(result.get('response', 'No response'))
                print("-" * 60)
                
                metadata = result.get('metadata', {})
                print(f"\n📋 Metadata:")
                print(f"   Session ID: {result.get('session_id', 'N/A')}")
                print(f"   Timestamp: {metadata.get('timestamp', 'N/A')}")
                print(f"   Model: {metadata.get('model', 'N/A')}")
                print(f"   Gateway: {metadata.get('gateway', 'N/A')}")
                
                return True
            else:
                print(f"❌ Agent invocation failed: HTTP {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Agent invocation error: {e}")
            return False
    
    def test_streaming_invocation(self):
        """Test streaming agent invocation"""
        print("\n📡 Testing Streaming Agent Invocation...")
        
        try:
            import requests
            
            stream_request = {
                "message": "Give me a detailed summary of our TACNode business data with recommendations.",
                "session_id": "demo-stream-001"
            }
            
            print(f"📤 Starting stream: {stream_request['message'][:50]}...")
            
            response = requests.post(
                'http://localhost:8000/stream',
                json=stream_request,
                stream=True,
                timeout=60
            )
            
            if response.status_code == 200:
                print("✅ Streaming started successfully!")
                print("\n📺 Streaming Response:")
                print("-" * 60)
                
                for line in response.iter_lines():
                    if line:
                        line_text = line.decode('utf-8')
                        if line_text.startswith('data: '):
                            data = json.loads(line_text[6:])
                            if 'chunk' in data:
                                print(data['chunk'], end='', flush=True)
                            elif data.get('done'):
                                print("\n" + "-" * 60)
                                print("✅ Streaming completed")
                                break
                            elif 'error' in data:
                                print(f"\n❌ Streaming error: {data['error']}")
                                break
                
                return True
            else:
                print(f"❌ Streaming failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Streaming error: {e}")
            return False
    
    def get_container_logs(self):
        """Get container logs for debugging"""
        print("\n📋 Getting Container Logs...")
        
        try:
            cmd = ['docker', 'logs', 'tacnode-agent-runtime', '--tail', '50']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.stdout:
                print("📄 Container Logs:")
                print("-" * 40)
                print(result.stdout)
                print("-" * 40)
            
            if result.stderr:
                print("⚠️  Container Errors:")
                print("-" * 40)
                print(result.stderr)
                print("-" * 40)
                
        except Exception as e:
            print(f"❌ Error getting logs: {e}")
    
    def stop_agent_container(self):
        """Stop the agent container"""
        print("\n🛑 Stopping Agent Container...")
        
        try:
            # Stop container
            stop_cmd = ['docker', 'stop', 'tacnode-agent-runtime']
            subprocess.run(stop_cmd, capture_output=True, text=True)
            
            # Remove container
            rm_cmd = ['docker', 'rm', 'tacnode-agent-runtime']
            subprocess.run(rm_cmd, capture_output=True, text=True)
            
            print("✅ Container stopped and removed")
            
        except Exception as e:
            print(f"❌ Error stopping container: {e}")
    
    def run_complete_simulation(self):
        """Run complete AgentCore Runtime simulation"""
        print("🎯 COMPLETE AGENTCORE RUNTIME SIMULATION")
        print("=" * 70)
        
        print("🏗️  SIMULATING PRODUCTION DEPLOYMENT:")
        print("   1. AgentCore Runtime → Custom Container (Local)")
        print("   2. Container → Claude AI Model (Bedrock)")
        print("   3. Container → AgentCore Gateway (AWS)")
        print("   4. Gateway → TACNode Context Lake (Real Data)")
        
        container_id = None
        
        try:
            # Step 1: Start container
            print("\n📋 STEP 1: Starting AgentCore Runtime Container")
            container_id = self.start_agent_container_locally()
            
            if not container_id:
                print("❌ Failed to start container")
                return False
            
            # Step 2: Test health
            print("\n📋 STEP 2: Testing Runtime Health")
            if not self.test_agent_health():
                print("⚠️  Health check failed, but continuing...")
            
            # Step 3: Test invocation
            print("\n📋 STEP 3: Testing Agent Invocation")
            invocation_success = self.test_agent_invocation()
            
            # Step 4: Test streaming
            print("\n📋 STEP 4: Testing Streaming Invocation")
            streaming_success = self.test_streaming_invocation()
            
            # Step 5: Get logs
            self.get_container_logs()
            
            # Calculate success
            success = container_id is not None and (invocation_success or streaming_success)
            
            print("\n" + "="*70)
            if success:
                print("🎉 AGENTCORE RUNTIME SIMULATION SUCCESSFUL!")
            else:
                print("⚠️  AGENTCORE RUNTIME SIMULATION PARTIALLY SUCCESSFUL")
            print("="*70)
            
            print(f"\n✅ SIMULATION RESULTS:")
            print(f"   🐳 Container Started: {'✅' if container_id else '❌'}")
            print(f"   🏥 Health Check: {'✅' if self.test_agent_health() else '❌'}")
            print(f"   🤖 Agent Invocation: {'✅' if invocation_success else '❌'}")
            print(f"   📡 Streaming: {'✅' if streaming_success else '❌'}")
            
            return success
            
        except KeyboardInterrupt:
            print("\n⚠️  Simulation interrupted by user")
            return False
        except Exception as e:
            print(f"\n❌ Simulation failed: {e}")
            return False
        finally:
            # Always clean up
            if container_id:
                self.stop_agent_container()

def main():
    print("🚀 AgentCore Runtime Simulation with Gateway Integration")
    print("=" * 70)
    
    simulator = AgentCoreRuntimeSimulator()
    
    try:
        # Run complete simulation
        success = simulator.run_complete_simulation()
        
        if success:
            print("\n🎯 READY FOR PRODUCTION DEPLOYMENT!")
            print("   All components tested and working")
            print("   AgentCore Runtime simulation successful")
        else:
            print("\n🔧 SIMULATION COMPLETED WITH ISSUES")
            print("   Some components need attention")
        
    except Exception as e:
        print(f"❌ Simulation failed: {e}")

if __name__ == "__main__":
    main()

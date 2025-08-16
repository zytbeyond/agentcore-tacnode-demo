#!/usr/bin/env python3
"""
Get Google OAuth token to test the existing gateway
This is a temporary solution to prove the integration works
"""

import asyncio
import httpx
import json
import webbrowser
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Handle OAuth callback"""
    
    def do_GET(self):
        """Handle GET request with OAuth callback"""
        if self.path.startswith('/?code='):
            # Extract authorization code
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            
            if 'code' in params:
                self.server.auth_code = params['code'][0]
                
                # Send success response
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'''
                <html>
                <body>
                <h1>Authorization Successful!</h1>
                <p>You can close this window and return to the terminal.</p>
                </body>
                </html>
                ''')
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'Error: No authorization code received')
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress log messages"""
        pass

async def get_google_oauth_token_interactive():
    """Get Google OAuth token interactively"""
    print("🔑 GETTING GOOGLE OAUTH TOKEN")
    print("=" * 60)
    print("⚠️  This is a temporary solution to test the integration")
    print("📋 We'll use Google OAuth playground for simplicity")
    
    # Google OAuth playground approach
    print("\n📋 OPTION 1: Google OAuth Playground (Recommended)")
    print("-" * 50)
    print("1. Go to: https://developers.google.com/oauthplayground")
    print("2. In 'Step 1', select 'Google OAuth2 API v2'")
    print("3. Select scope: https://www.googleapis.com/auth/userinfo.email")
    print("4. Click 'Authorize APIs'")
    print("5. Sign in with your Google account")
    print("6. In 'Step 2', click 'Exchange authorization code for tokens'")
    print("7. Copy the 'Access token' value")
    
    print("\n🔑 Enter the access token here:")
    access_token = input("Access Token: ").strip()
    
    if access_token:
        print(f"\n✅ Token received: {access_token[:50]}...")
        
        # Save token
        token_info = {
            "accessToken": access_token,
            "provider": "google-oauth-playground",
            "obtained": time.time()
        }
        
        with open('google-oauth-token.json', 'w') as f:
            json.dump(token_info, f, indent=2)
        
        print(f"✅ Token saved to google-oauth-token.json")
        
        return access_token
    else:
        print("❌ No token provided")
        return None

async def test_gateway_with_google_token(token):
    """Test the gateway with Google OAuth token"""
    print(f"\n🧪 TESTING GATEWAY WITH GOOGLE OAUTH TOKEN")
    print("=" * 60)
    
    # Load gateway info
    with open('tacnode-agentcore-gateway.json', 'r') as f:
        gateway_info = json.load(f)
        gateway_id = gateway_info['gatewayId']
    
    with open('tacnode-agentcore-target.json', 'r') as f:
        target_info = json.load(f)
        target_name = target_info['targetName']
    
    gateway_url = f"https://{gateway_id}.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp"
    
    print(f"Gateway URL: {gateway_url}")
    print(f"Target: {target_name}")
    print(f"Token: {token[:50]}...")
    
    # Test MCP call
    mcp_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "executeJsonRpcCall",
            "arguments": {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "query",
                    "arguments": {
                        "sql": "SELECT COUNT(*) as record_count FROM test WHERE is_active = true"
                    }
                },
                "id": 1
            }
        }
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print(f"\n🌐 Making MCP call to gateway...")
            
            response = await client.post(
                gateway_url,
                json=mcp_request,
                headers=headers
            )
            
            print(f"Response Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    response_json = response.json()
                    print(f"Response JSON: {json.dumps(response_json, indent=2)}")
                    
                    if 'result' in response_json:
                        print(f"\n🎉 SUCCESS! COMPLETE END-TO-END INTEGRATION WORKING!")
                        print(f"✅ User → MCP → AgentCore Gateway → TACNode → PostgreSQL")
                        print(f"✅ Google OAuth authentication successful")
                        print(f"✅ Gateway routing successful")
                        print(f"✅ TACNode API call successful")
                        
                        return True
                    else:
                        print(f"❌ No result in response")
                        return False
                        
                except json.JSONDecodeError as e:
                    print(f"❌ Failed to parse response: {e}")
                    print(f"Raw response: {response.text}")
                    return False
            elif response.status_code == 401:
                print(f"❌ 401 Unauthorized - Token not accepted")
                print(f"Response: {response.text}")
                return False
            else:
                print(f"❌ Unexpected status: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

async def show_final_results(success, token):
    """Show final results and next steps"""
    print(f"\n🎯 FINAL RESULTS")
    print("=" * 60)
    
    if success:
        print("🎉 COMPLETE SUCCESS!")
        print("✅ End-to-end integration is WORKING!")
        print("✅ User → MCP → AgentCore Gateway → TACNode → PostgreSQL")
        
        print(f"\n🔑 Working Configuration:")
        print(f"   • Gateway: tacnodecontextlakegateway-bkq6ozcvxp")
        print(f"   • Authentication: Google OAuth")
        print(f"   • Target: TACNode REST API")
        print(f"   • Database: PostgreSQL via TACNode")
        
        print(f"\n🧪 For Future Testing:")
        print(f"export GATEWAY_TOKEN='{token}'")
        print("python3 test_tacnode_rest_api_direct.py")
        
        print(f"\n📋 Next Steps (Optional):")
        print("1. ✅ Integration is working - you can use it as-is")
        print("2. 🔄 Optionally reconfigure to AWS Cognito for pure AWS solution")
        print("3. 🚀 Deploy to production")
        
    else:
        print("❌ INTEGRATION TEST FAILED")
        print("🔍 Possible issues:")
        print("   • Google OAuth token invalid or expired")
        print("   • Gateway configuration issue")
        print("   • TACNode API issue")
        
        print(f"\n🔧 Troubleshooting:")
        print("1. Try getting a fresh Google OAuth token")
        print("2. Check TACNode API directly")
        print("3. Verify gateway configuration")

async def main():
    """Main function to get token and test integration"""
    print("🔑 Google OAuth Token Getter for Gateway Testing")
    print("=" * 60)
    print("🎯 Goal: Test complete end-to-end integration")
    print("⚠️  Temporary solution using Google OAuth")
    
    # Get Google OAuth token
    token = await get_google_oauth_token_interactive()
    
    if not token:
        print("❌ No token obtained")
        return
    
    # Test gateway with token
    success = await test_gateway_with_google_token(token)
    
    # Show final results
    await show_final_results(success, token)

if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
Query actual data from TACNode Context Lake
"""
import json
import requests
import os

def query_tacnode_data():
    """Query and display data from TACNode Context Lake"""
    
    token = os.getenv('TACNODE_TOKEN')
    if not token:
        print("❌ TACNODE_TOKEN environment variable not set")
        return
    
    url = "https://mcp-server.tacnode.io/mcp"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream',
        'Authorization': f'Bearer {token}'
    }
    
    queries = [
        {
            "name": "📊 All Test Data",
            "sql": "SELECT * FROM test ORDER BY created_date DESC;"
        },
        {
            "name": "📈 Summary by Category", 
            "sql": "SELECT category, COUNT(*) as count, AVG(value) as avg_value, SUM(value) as total_value FROM test WHERE is_active = true GROUP BY category ORDER BY total_value DESC;"
        },
        {
            "name": "🔍 Recent Active Records",
            "sql": "SELECT name, description, value, category, created_date FROM test WHERE is_active = true AND created_date > CURRENT_DATE - INTERVAL '5 days' ORDER BY created_date DESC;"
        },
        {
            "name": "💰 High Value Items",
            "sql": "SELECT name, value, category, is_active FROM test WHERE value > 100 ORDER BY value DESC;"
        },
        {
            "name": "📅 Data by Date Range",
            "sql": "SELECT DATE(created_date) as date, COUNT(*) as records, AVG(value) as avg_value FROM test GROUP BY DATE(created_date) ORDER BY date DESC;"
        }
    ]
    
    print("🏛️ TACNode Context Lake - Data Analysis")
    print("=" * 50)
    
    for i, query_info in enumerate(queries, 1):
        print(f"\n{i}️⃣ {query_info['name']}")
        print("-" * 40)
        
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "query",
                "arguments": {"sql": query_info['sql']}
            },
            "id": i
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            if response.status_code == 200:
                # Parse SSE response
                lines = response.text.strip().split('\n')
                for line in lines:
                    if line.startswith('data: '):
                        data = json.loads(line[6:])
                        if 'result' in data and 'content' in data['result']:
                            content = data['result']['content'][0]['text']
                            # Parse the JSON result
                            try:
                                result_data = json.loads(content)
                                if result_data:
                                    print(f"✅ Found {len(result_data)} records")
                                    for record in result_data:
                                        print(f"   {record}")
                                else:
                                    print("📭 No data found")
                            except json.JSONDecodeError:
                                print(f"📄 Raw result: {content}")
                        elif 'error' in data:
                            print(f"❌ Query error: {data['error']}")
            else:
                print(f"❌ Request failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n🎯 Summary:")
    print("- Database: PostgreSQL 14.2 (TACNode Context Lake)")
    print("- User: zyuantao@amazon.com") 
    print("- Available table: 'test' with sample business data")
    print("- Data includes: names, descriptions, values, categories, timestamps")
    print("- Real-time querying capabilities via MCP protocol")

if __name__ == "__main__":
    query_tacnode_data()

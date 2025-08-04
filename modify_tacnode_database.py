#!/usr/bin/env python3
"""
TACNode Database Modification Tool
Easily modify the database to test real-time agent responses
"""

import json
import os
import time
from datetime import datetime, timedelta
import random

class TACNodeDatabaseModifier:
    """Tool to modify TACNode database for testing"""
    
    def __init__(self):
        self.tacnode_token = os.getenv('TACNODE_TOKEN')
        if not self.tacnode_token:
            print("❌ TACNODE_TOKEN environment variable not set")
            return
        
        print("🔧 TACNode Database Modification Tool")
        print("=" * 50)
    
    def show_current_data(self):
        """Show current database state"""
        print("\n📊 CURRENT DATABASE STATE")
        print("-" * 40)
        
        import subprocess
        try:
            result = subprocess.run(['python3', 'query_tacnode_data.py'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(result.stdout)
            else:
                print(f"❌ Error: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Query error: {e}")
        
        print("-" * 40)
    
    def add_new_record(self, name, description, value, category):
        """Add a new record to the database"""
        print(f"\n➕ ADDING NEW RECORD")
        print(f"   Name: {name}")
        print(f"   Description: {description}")
        print(f"   Value: ${value}")
        print(f"   Category: {category}")
        
        # In a real implementation, this would call TACNode MCP to insert data
        # For now, we'll simulate the addition
        print("✅ Record added successfully (simulated)")
        print("   Note: In production, this would call TACNode MCP server")
        print("   to execute: INSERT INTO test (name, description, value, category, created_date, is_active)")
        print(f"   VALUES ('{name}', '{description}', {value}, '{category}', NOW(), true)")
    
    def update_record_value(self, record_id, new_value):
        """Update a record's value"""
        print(f"\n✏️  UPDATING RECORD {record_id}")
        print(f"   New Value: ${new_value}")
        
        # In a real implementation, this would call TACNode MCP
        print("✅ Record updated successfully (simulated)")
        print("   Note: In production, this would call TACNode MCP server")
        print(f"   to execute: UPDATE test SET value = {new_value} WHERE id = {record_id}")
    
    def simulate_business_scenarios(self):
        """Simulate different business scenarios"""
        print("\n🎭 BUSINESS SCENARIO SIMULATION")
        print("=" * 50)
        
        scenarios = [
            {
                "name": "Revenue Boost",
                "description": "Simulate a successful quarter",
                "changes": [
                    {"action": "update", "id": 1, "value": 1500.00},
                    {"action": "update", "id": 4, "value": 1200.00},
                    {"action": "add", "name": "Bonus Revenue", "desc": "Unexpected revenue stream", "value": 800.00, "category": "Category 1"}
                ]
            },
            {
                "name": "Cost Reduction",
                "description": "Simulate operational efficiency improvements",
                "changes": [
                    {"action": "update", "id": 2, "value": 150.00},  # Reduced marketing cost
                    {"action": "update", "id": 5, "value": -5.00},   # Improved efficiency
                    {"action": "add", "name": "Process Optimization", "desc": "Automated workflow savings", "value": 300.00, "category": "Category 2"}
                ]
            },
            {
                "name": "Market Expansion",
                "description": "Simulate new market entry",
                "changes": [
                    {"action": "add", "name": "New Market Revenue", "desc": "International expansion", "value": 2000.00, "category": "Category 3"},
                    {"action": "add", "name": "Market Research", "desc": "Investment in market analysis", "value": 450.00, "category": "Category 2"},
                    {"action": "update", "id": 7, "value": 650.00}  # Increased market expansion
                ]
            }
        ]
        
        print("Available scenarios:")
        for i, scenario in enumerate(scenarios, 1):
            print(f"{i}. {scenario['name']}: {scenario['description']}")
        
        try:
            choice = input(f"\nSelect scenario (1-{len(scenarios)}) or 'skip': ").strip()
            
            if choice.lower() == 'skip':
                return
            
            scenario_idx = int(choice) - 1
            if 0 <= scenario_idx < len(scenarios):
                scenario = scenarios[scenario_idx]
                print(f"\n🎬 Applying scenario: {scenario['name']}")
                
                for change in scenario['changes']:
                    if change['action'] == 'update':
                        self.update_record_value(change['id'], change['value'])
                    elif change['action'] == 'add':
                        self.add_new_record(change['name'], change['desc'], change['value'], change['category'])
                
                print(f"\n✅ Scenario '{scenario['name']}' applied!")
                print("   Ask the agent about business performance to see the changes!")
            else:
                print("❌ Invalid scenario selection")
                
        except ValueError:
            print("❌ Invalid input")
    
    def interactive_modification(self):
        """Interactive database modification"""
        print("\n🔧 INTERACTIVE DATABASE MODIFICATION")
        print("=" * 50)
        
        while True:
            print("\nOptions:")
            print("1. Show current data")
            print("2. Add new record")
            print("3. Update record value")
            print("4. Apply business scenario")
            print("5. Return to main menu")
            
            try:
                choice = input("\nSelect option (1-5): ").strip()
                
                if choice == '1':
                    self.show_current_data()
                
                elif choice == '2':
                    print("\n➕ ADD NEW RECORD")
                    name = input("Name: ").strip()
                    description = input("Description: ").strip()
                    value = float(input("Value ($): ").strip())
                    category = input("Category (Category 1/2/3): ").strip()
                    
                    self.add_new_record(name, description, value, category)
                
                elif choice == '3':
                    print("\n✏️  UPDATE RECORD VALUE")
                    record_id = int(input("Record ID (1-10): ").strip())
                    new_value = float(input("New Value ($): ").strip())
                    
                    self.update_record_value(record_id, new_value)
                
                elif choice == '4':
                    self.simulate_business_scenarios()
                
                elif choice == '5':
                    break
                
                else:
                    print("❌ Invalid option")
                    
            except ValueError:
                print("❌ Invalid input format")
            except KeyboardInterrupt:
                print("\n👋 Returning to main menu")
                break
    
    def run_modification_tool(self):
        """Run the modification tool"""
        print("\n🎯 DATABASE MODIFICATION FOR AGENT TESTING")
        print("=" * 60)
        print("This tool helps you modify the TACNode database to test")
        print("how the agent responds to real-time data changes.")
        print("")
        print("TESTING WORKFLOW:")
        print("1. Ask agent a question about business data")
        print("2. Note the response and specific numbers")
        print("3. Modify the database using this tool")
        print("4. Ask the same question again")
        print("5. Compare responses to see real-time changes")
        print("=" * 60)
        
        # Show current state
        self.show_current_data()
        
        # Interactive modification
        self.interactive_modification()
        
        print("\n✅ Database modification session complete!")
        print("   Now test the agent to see if it reflects your changes!")

def main():
    print("🔧 TACNode Database Modification Tool")
    print("=" * 50)
    
    modifier = TACNodeDatabaseModifier()
    
    try:
        modifier.run_modification_tool()
        
    except Exception as e:
        print(f"❌ Modification tool error: {e}")

if __name__ == "__main__":
    main()

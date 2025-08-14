#!/usr/bin/env python3
"""
Agentic client for interacting with the skill tree server.
Optimized for agentic development workflows.
"""

import requests
import time
import subprocess
import os
from pathlib import Path

class SkillTreeClient:
    def __init__(self, host="127.0.0.1", port=8003):
        self.base_url = f"http://{host}:{port}"
        self.host = host
        self.port = port
    
    def is_server_running(self):
        """Check if server is running"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def start_server_external(self):
        """Start server in external terminal (best for Windows)"""
        try:
            launcher = Path("start_skill_tree_server.bat")
            if launcher.exists():
                # Start in external terminal
                subprocess.Popen([str(launcher)], shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
                print("Server started in external terminal window")
                time.sleep(5)  # Wait for startup
                return self.is_server_running()
            else:
                print("Launcher script not found")
                return False
        except Exception as e:
            print(f"Failed to start server: {e}")
            return False
    
    def get_skill_tree_data(self):
        """Get skill tree data"""
        response = requests.get(f"{self.base_url}/skill-tree/overview", timeout=15)
        response.raise_for_status()
        return response.json()
    
    def get_server_health(self):
        """Get server health status"""
        response = requests.get(f"{self.base_url}/health", timeout=5)
        response.raise_for_status()
        return response.json()

def test_agentic_workflow():
    """Test the complete agentic workflow"""
    print("AGENTIC SKILL TREE WORKFLOW TEST")
    print("=" * 50)
    
    client = SkillTreeClient()
    
    # Test 1: Check server status
    print("\n1. Checking server status...")
    if client.is_server_running():
        print("   ✓ Server is running")
    else:
        print("   - Server not running, starting...")
        if client.start_server_external():
            print("   ✓ Server started successfully")
        else:
            print("   ✗ Failed to start server")
            print("\n   Manual steps:")
            print("   1. Double-click start_skill_tree_server.bat")
            print("   2. Wait for server to start")
            print("   3. Run this script again")
            return
    
    # Test 2: Get health data
    print("\n2. Testing server health...")
    try:
        health = client.get_server_health()
        print(f"   ✓ Server status: {health.get('status', 'unknown')}")
        print(f"   ✓ Service: {health.get('service', 'unknown')}")
    except Exception as e:
        print(f"   ✗ Health check failed: {e}")
    
    # Test 3: Get skill tree data
    print("\n3. Testing skill tree data...")
    try:
        data = client.get_skill_tree_data()
        total_problems = data.get('total_problems', 0)
        skill_areas = data.get('total_skill_areas', 0)
        columns = data.get('skill_tree_columns', [])
        
        print(f"   ✓ Total problems: {total_problems}")
        print(f"   ✓ Skill areas: {skill_areas}")
        print(f"   ✓ Data source: {data.get('data_source', 'unknown')}")
        
        if columns:
            print("   ✓ Skill areas available:")
            for column in columns[:3]:  # Show first 3
                area = column.get('skill_area', 'unknown')
                count = column.get('total_problems', 0)
                print(f"     - {area}: {count} problems")
        
        print("\n✓ AGENTIC WORKFLOW SUCCESSFUL!")
        print("  → Server can be controlled programmatically")
        print("  → Data is accessible via API")
        print("  → Frontend can connect to this server")
        
    except Exception as e:
        print(f"   ✗ Data retrieval failed: {e}")

if __name__ == "__main__":
    test_agentic_workflow()

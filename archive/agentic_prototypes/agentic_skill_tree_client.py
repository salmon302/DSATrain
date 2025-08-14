#!/usr/bin/env python3
"""
Agentic client for DSA Skill Tree integration with the main platform.
Works with the integrated launch system.
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
        """Check if skill tree server is running"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def is_main_platform_running(self):
        """Check if main DSATrain platform is running"""
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def start_integrated_platform(self):
        """Start the complete integrated platform"""
        try:
            launcher = Path("launch_dsatrain.bat")
            if launcher.exists():
                print("Starting integrated DSATrain platform...")
                subprocess.Popen([str(launcher)], shell=True)
                time.sleep(10)  # Wait for both servers to start
                return self.is_main_platform_running() and self.is_server_running()
            else:
                print("Main launcher script not found")
                return False
        except Exception as e:
            print(f"Failed to start platform: {e}")
            return False
    
    def get_skill_tree_data(self):
        """Get skill tree data from the integrated server"""
        response = requests.get(f"{self.base_url}/skill-tree/overview", timeout=15)
        response.raise_for_status()
        return response.json()
    
    def get_server_health(self):
        """Get skill tree server health status"""
        response = requests.get(f"{self.base_url}/health", timeout=5)
        response.raise_for_status()
        return response.json()
    
    def get_platform_status(self):
        """Get complete platform status"""
        status = {
            "main_api": self.is_main_platform_running(),
            "skill_tree_api": self.is_server_running(),
            "frontend_expected": "http://localhost:3000",
            "skill_tree_endpoint": f"{self.base_url}/skill-tree/overview"
        }
        return status

def test_integrated_platform():
    """Test the complete integrated platform"""
    print("INTEGRATED DSA SKILL TREE PLATFORM TEST")
    print("=" * 60)
    
    client = SkillTreeClient()
    
    # Test 1: Check platform status
    print("\n1. Checking platform status...")
    status = client.get_platform_status()
    
    if status["main_api"]:
        print("   ✓ Main API server running (port 8000)")
    else:
        print("   - Main API server not running")
    
    if status["skill_tree_api"]:
        print("   ✓ Skill Tree API running (port 8003)")
    else:
        print("   - Skill Tree API not running")
    
    # If neither is running, start the integrated platform
    if not status["main_api"] and not status["skill_tree_api"]:
        print("\n   → Starting integrated platform...")
        if client.start_integrated_platform():
            print("   ✓ Platform started successfully")
            status = client.get_platform_status()
        else:
            print("   ✗ Failed to start platform")
            print("\n   Manual steps:")
            print("   1. Double-click launch_dsatrain.bat")
            print("   2. Wait for all servers to start")
            print("   3. Run this script again")
            return
    
    # Test 2: Skill Tree API functionality
    if status["skill_tree_api"]:
        print("\n2. Testing Skill Tree API...")
        try:
            health = client.get_server_health()
            print(f"   ✓ Health status: {health.get('status', 'unknown')}")
            
            data = client.get_skill_tree_data()
            total_problems = data.get('total_problems', 0)
            skill_areas = data.get('total_skill_areas', 0)
            
            print(f"   ✓ Total problems: {total_problems}")
            print(f"   ✓ Skill areas: {skill_areas}")
            print(f"   ✓ Data source: {data.get('data_source', 'unknown')}")
            
        except Exception as e:
            print(f"   ✗ Skill Tree API test failed: {e}")
    
    # Test 3: Integration status
    print("\n3. Integration Status...")
    print(f"   Main API (FastAPI): {'✓' if status['main_api'] else '✗'} http://localhost:8000")
    print(f"   Skill Tree API: {'✓' if status['skill_tree_api'] else '✗'} http://localhost:8003")
    print(f"   Frontend: {'→' if status['main_api'] else '✗'} http://localhost:3000")
    print(f"   API Docs: {'→' if status['main_api'] else '✗'} http://localhost:8000/docs")
    
    if status["main_api"] and status["skill_tree_api"]:
        print("\n✓ INTEGRATED PLATFORM FULLY OPERATIONAL!")
        print("  → All APIs accessible for agentic control")
        print("  → Frontend can display skill tree visualization")
        print("  → Complete development environment ready")
    else:
        print("\n⚠ PARTIAL PLATFORM STATUS")
        print("  → Some services may need manual startup")

if __name__ == "__main__":
    test_integrated_platform()

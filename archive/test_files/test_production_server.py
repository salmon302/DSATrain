#!/usr/bin/env python3
"""Test the production Flask server."""

import requests
import time

def test_production_server():
    """Test the production server endpoints"""
    base_url = "http://localhost:8005"
    
    try:
        print("🧪 Testing production Flask server...")
        
        # Test health endpoint
        print("Testing /health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"Health response: {response.status_code} - {response.json()}")
        
        # Test skill tree endpoint
        print("Testing /skill-tree/overview endpoint...")
        response = requests.get(f"{base_url}/skill-tree/overview", timeout=10)
        data = response.json()
        print(f"Skill tree response: {response.status_code}")
        print(f"Total problems: {data.get('total_problems', 'unknown')}")
        print(f"Skill areas: {data.get('total_skill_areas', 'unknown')}")
        
        print("✅ Production server is working correctly!")
        return True
        
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection failed: {e}")
        return False
    except requests.exceptions.Timeout as e:
        print(f"❌ Request timed out: {e}")
        return False
    except Exception as e:
        print(f"❌ Request failed: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    # Give server time to start
    time.sleep(3)
    test_production_server()

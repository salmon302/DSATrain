#!/usr/bin/env python3
"""Test the Flask skill tree server API."""

import requests
import json

def test_health():
    """Test the health endpoint."""
    try:
        response = requests.get("http://localhost:8003/health", timeout=5)
        print(f"Health endpoint: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_skill_tree():
    """Test the skill tree overview endpoint."""
    try:
        response = requests.get("http://localhost:8003/skill-tree/overview", timeout=10)
        print(f"Skill tree endpoint: {response.status_code}")
        data = response.json()
        print(f"Total problems: {data.get('total_problems', 'unknown')}")
        print(f"Categories: {len(data.get('categories', []))}")
        
        # Show first few problems for verification
        problems = data.get('problems', [])
        if problems:
            print(f"First problem: {problems[0].get('title', 'No title')}")
            print(f"Sample problem data: {json.dumps(problems[0], indent=2)[:200]}...")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Skill tree test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Flask Skill Tree Server API...")
    print("=" * 50)
    
    health_ok = test_health()
    print()
    
    if health_ok:
        skill_tree_ok = test_skill_tree()
        print()
        
        if skill_tree_ok:
            print("✅ All API tests passed! Frontend should be able to connect.")
        else:
            print("❌ Skill tree endpoint failed.")
    else:
        print("❌ Server health check failed.")

#!/usr/bin/env python3
"""Test the Python HTTP server."""

import requests
import time

def test_http_server():
    """Test the HTTP server endpoints"""
    base_url = "http://localhost:8006"
    
    try:
        print("🧪 Testing Python HTTP server...")
        
        # Test health endpoint
        print("Testing /health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"Health response: {response.status_code} - {response.json()}")
        
        # Test skill tree endpoint
        print("Testing /skill-tree/overview endpoint...")
        response = requests.get(f"{base_url}/skill-tree/overview", timeout=15)
        data = response.json()
        print(f"Skill tree response: {response.status_code}")
        print(f"Total problems: {data.get('total_problems', 'unknown')}")
        print(f"Skill areas: {data.get('total_skill_areas', 'unknown')}")
        
        # Show detailed data
        columns = data.get('skill_tree_columns', [])
        if columns:
            first_column = columns[0]
            print(f"First skill area: {first_column.get('skill_area', 'unknown')}")
            easy_problems = first_column.get('difficulty_levels', {}).get('Easy', [])
            print(f"Easy problems in first area: {len(easy_problems)}")
            if easy_problems:
                print(f"First problem: {easy_problems[0].get('title', 'No title')}")
        
        print("✅ HTTP server is working correctly!")
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
    time.sleep(2)
    test_http_server()

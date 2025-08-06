#!/usr/bin/env python3
"""Test the minimal Flask server to understand the deployment issue."""

import requests
import time

def test_minimal_server():
    """Test the minimal server endpoints"""
    base_url = "http://localhost:8004"
    
    try:
        print("🧪 Testing minimal Flask server...")
        
        # Test health endpoint
        print("Testing /health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"Health response: {response.status_code} - {response.json()}")
        
        # Test basic endpoint
        print("Testing /test endpoint...")
        response = requests.get(f"{base_url}/test", timeout=5)
        print(f"Test response: {response.status_code} - {response.json()}")
        
        print("✅ Minimal server is working correctly!")
        return True
        
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    # Give server time to start
    time.sleep(2)
    test_minimal_server()

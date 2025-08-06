#!/usr/bin/env python3
"""
Test script for FastAPI Google code analysis endpoint
Tests the actual REST API running on localhost:8000
"""

import requests
import json

# Test endpoint URL
BASE_URL = "http://127.0.0.1:8004"

def test_analyze_code():
    """Test the /google/analyze-code endpoint"""
    print("🧪 Testing FastAPI Google Code Analysis Endpoint")
    print("=" * 60)
    
    # Test code - Two Sum brute force
    test_code = """
def two_sum(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
"""
    
    # Request payload
    payload = {
        "code": test_code,
        "language": "python",
        "problem_id": "two-sum",
        "time_spent_seconds": 15,
        "thinking_out_loud": True,
        "communication_notes": [
            "Starting with brute force approach",
            "Checking each pair of numbers",
            "Returning indices when sum matches target"
        ]
    }
    
    try:
        print(f"📡 Sending POST request to {BASE_URL}/google/analyze")
        response = requests.post(
            f"{BASE_URL}/google/analyze",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📋 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API Response Success!")
            print(json.dumps(result, indent=2))
            
            # Validate response structure
            expected_keys = ["complexity", "code_quality", "google_scores", "suggestions"]
            for key in expected_keys:
                if key in result:
                    print(f"✅ {key}: Present")
                else:
                    print(f"❌ {key}: Missing")
                    
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Error details: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure FastAPI server is running on port 8000")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_get_feedback():
    """Test the /google/feedback endpoint"""
    print("\n🧪 Testing Google Feedback Endpoint")
    print("=" * 60)
    
    # Test parameters
    params = {
        "code_quality": 75,
        "time_spent": 20,
        "communication_count": 3
    }
    
    try:
        print(f"📡 Sending GET request to {BASE_URL}/google/feedback")
        response = requests.get(
            f"{BASE_URL}/google/feedback",
            params=params
        )
        
        print(f"📋 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Feedback API Success!")
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Error details: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure FastAPI server is running on port 8000")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_health_check():
    """Test basic health check"""
    print("\n🧪 Testing API Health")
    print("=" * 60)
    
    try:
        # Test root endpoint
        response = requests.get(f"{BASE_URL}/")
        print(f"📋 Root endpoint status: {response.status_code}")
        
        # Test docs endpoint
        response = requests.get(f"{BASE_URL}/docs")
        print(f"📋 Docs endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ FastAPI is running and healthy!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: FastAPI server not accessible")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    print("🚀 FastAPI Google Analysis Integration Test")
    print("=" * 60)
    
    test_health_check()
    test_analyze_code()
    test_get_feedback()
    
    print("\n🎯 Integration Test Complete!")
    print("📝 To use in frontend, ensure the API service points to http://127.0.0.1:8000")

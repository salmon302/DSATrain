#!/usr/bin/env python3
"""
Simple endpoint test for FastAPI Google analysis
"""

import time
import requests
import json

# Give server time to start
time.sleep(2)

# Test health first
try:
    response = requests.get("http://127.0.0.1:8005/")
    print(f"✅ Health check: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
except Exception as e:
    print(f"❌ Health check failed: {e}")
    
# Test analyze endpoint
test_code = """
def two_sum(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
"""

payload = {
    "code": test_code,
    "language": "python",
    "problem_id": "two-sum",
    "time_spent_seconds": 15,
    "thinking_out_loud": True,
    "communication_notes": [
        "Starting with brute force approach",
        "Checking each pair of numbers"
    ]
}

try:
    response = requests.post(
        "http://127.0.0.1:8005/google/analyze",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    print(f"✅ Analyze endpoint: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print("📊 Analysis result:")
        print(json.dumps(result, indent=2))
    else:
        print(f"❌ Error: {response.text}")
except Exception as e:
    print(f"❌ Analyze test failed: {e}")

print("🎯 Test complete!")

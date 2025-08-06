#!/usr/bin/env python3
"""
Simple API test script
"""

import requests
import json

def test_api():
    try:
        # Test basic endpoint
        print("Testing API root endpoint...")
        response = requests.get('http://127.0.0.1:8001/', timeout=5)
        print(f"Root endpoint status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        
        # Test learning paths templates
        print("\nTesting learning paths templates...")
        response = requests.get('http://127.0.0.1:8001/learning-paths/templates', timeout=10)
        print(f"Templates endpoint status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {data.get('total_count', 0)} templates")
        else:
            print(f"Error: {response.text}")
        
        # Test learning path generation (POST)
        print("\nTesting learning path generation...")
        request_data = {
            'user_id': 'test_user_123',
            'current_skill_levels': {
                'arrays': 0.3,
                'strings': 0.2,
                'hash_tables': 0.1
            },
            'learning_goals': ['google_interview'],
            'available_hours_per_week': 10,
            'preferred_difficulty_curve': 'gradual',
            'target_completion_weeks': 8
        }
        
        response = requests.post(
            'http://127.0.0.1:8001/learning-paths/generate',
            json=request_data,
            timeout=30
        )
        print(f"Generation endpoint status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Learning path generated successfully!")
            print(f"Message: {data.get('message', 'No message')}")
        else:
            print(f"❌ Error: {response.text}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_api()

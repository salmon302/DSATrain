#!/usr/bin/env python3
"""
Test the actual API endpoint
"""

import requests
import json

def test_api_endpoint():
    try:
        print("Testing learning path API endpoint...")
        
        # Test data matching the API format
        request_data = {
            'user_id': 'test_user_api',
            'current_skill_levels': {
                'arrays': 0.3,
                'strings': 0.2,
                'hash_tables': 0.1,
                'trees': 0.1,
                'dynamic_programming': 0.1
            },
            'learning_goals': ['google_interview'],
            'available_hours_per_week': 10,
            'preferred_difficulty_curve': 'gradual',
            'target_completion_weeks': 8,
            'weak_areas': ['dynamic_programming', 'trees'],
            'strong_areas': ['arrays']
        }
        
        print(f"Making POST request to /learning-paths/generate...")
        print(f"Request data: {json.dumps(request_data, indent=2)}")
        
        response = requests.post(
            'http://127.0.0.1:8000/learning-paths/generate',
            json=request_data,
            timeout=30
        )
        
        print(f"\nResponse status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS!")
            print(f"Message: {data.get('message', 'No message')}")
            path = data.get('learning_path', {})
            print(f"Learning Path ID: {path.get('id', 'No ID')}")
            print(f"Learning Path Name: {path.get('name', 'No name')}")
            print(f"Problem Count: {path.get('problem_count', 0)}")
        else:
            print(f"❌ ERROR: {response.text}")
        
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    test_api_endpoint()

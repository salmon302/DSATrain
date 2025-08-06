#!/usr/bin/env python3
"""
Test script for learning path API endpoint
"""

import requests
import json
import time
import sys

def test_learning_path_generation():
    """Test the learning path generation endpoint"""
    try:
        # Wait a moment for server to be ready
        time.sleep(2)
        
        print('Testing learning path generation endpoint...')
        
        # Prepare test data
        request_data = {
            'user_id': 'test_user_123',
            'current_skill_levels': {
                'arrays': 0.3,
                'strings': 0.2,
                'hash_tables': 0.1,
                'trees': 0.1,
                'dynamic_programming': 0.1
            },
            'learning_goals': ['google_interview', 'algorithm_mastery'],
            'available_hours_per_week': 10,
            'preferred_difficulty_curve': 'gradual',
            'target_completion_weeks': 8,
            'weak_areas': ['dynamic_programming', 'trees'],
            'strong_areas': ['arrays']
        }
        
        print(f'Request data: {json.dumps(request_data, indent=2)}')
        
        # Make POST request
        response = requests.post(
            'http://127.0.0.1:8001/learning-paths/generate',
            json=request_data,
            timeout=30
        )
        
        print(f'Response status: {response.status_code}')
        print(f'Response headers: {dict(response.headers)}')
        
        if response.status_code == 200:
            result = response.json()
            print('✅ SUCCESS: Learning path generated successfully!')
            print(f'Learning path ID: {result.get("id")}')
            print(f'Template: {result.get("template_name")}')
            print(f'Total milestones: {len(result.get("milestones", []))}')
            print(f'First few milestones:')
            for i, milestone in enumerate(result.get("milestones", [])[:3]):
                print(f'  {i+1}. {milestone.get("title", "N/A")} - {milestone.get("description", "N/A")}')
            return True
        else:
            print(f'❌ ERROR: Status {response.status_code}')
            print(f'Response text: {response.text}')
            return False
            
    except requests.exceptions.ConnectionError as e:
        print(f'❌ Connection error: Server not running or not accessible')
        print(f'Error details: {str(e)}')
        return False
    except requests.exceptions.Timeout as e:
        print(f'❌ Timeout error: Server took too long to respond')
        print(f'Error details: {str(e)}')
        return False
    except Exception as e:
        print(f'❌ Unexpected error: {str(e)}')
        import traceback
        traceback.print_exc()
        return False

def test_basic_endpoints():
    """Test basic endpoints to verify server is working"""
    try:
        print('Testing basic health check...')
        
        # Test health endpoint
        response = requests.get('http://127.0.0.1:8001/', timeout=10)
        print(f'Health check status: {response.status_code}')
        
        if response.status_code == 200:
            print('✅ Server is responding to basic requests')
            
            # Test learning path templates endpoint
            print('Testing learning path templates endpoint...')
            response = requests.get('http://127.0.0.1:8001/learning-paths/templates', timeout=10)
            print(f'Templates endpoint status: {response.status_code}')
            
            if response.status_code == 200:
                templates = response.json()
                print(f'✅ Found {len(templates)} learning path templates')
                for template in templates[:3]:
                    print(f'  - {template.get("name", "N/A")}: {template.get("description", "N/A")[:50]}...')
                return True
            else:
                print(f'❌ Templates endpoint failed: {response.text}')
                return False
        else:
            print(f'❌ Health check failed: {response.text}')
            return False
            
    except Exception as e:
        print(f'❌ Basic endpoint test failed: {str(e)}')
        return False

if __name__ == "__main__":
    print("=== Learning Path API Test ===")
    
    # Test basic endpoints first
    if test_basic_endpoints():
        print()
        # Then test learning path generation
        test_learning_path_generation()
    else:
        print("Basic endpoint tests failed, skipping learning path test")
        sys.exit(1)

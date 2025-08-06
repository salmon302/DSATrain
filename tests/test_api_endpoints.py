"""
Test Learning Paths API Endpoints
Quick verification that all API endpoints are working correctly
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8001"


def test_learning_paths_api():
    """Test all learning paths API endpoints"""
    
    print("🧪 Testing Learning Paths API Endpoints...\n")
    
    # Test 1: Get templates
    print("📋 Test 1: Get Learning Path Templates")
    response = requests.get(f"{BASE_URL}/learning-paths/templates")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success: Found {data['total_count']} templates")
        templates = data['templates']
        for template in templates[:3]:
            print(f"   - {template['name']} ({template['category']}, {template['estimated_duration_weeks']} weeks)")
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
        return False
    
    # Test 2: Get template recommendations
    print("\n🎯 Test 2: Get Template Recommendations")
    params = {
        "user_goals": ["google", "interview"],
        "available_weeks": 10,
        "current_skill_level": "intermediate"
    }
    response = requests.get(f"{BASE_URL}/learning-paths/templates/recommendations", params=params)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success: Found {len(data['recommendations'])} recommendations")
        for i, rec in enumerate(data['recommendations'][:2]):
            template = rec['template']
            print(f"   {i+1}. {template['name']} (fit score: {rec['fit_score']:.2f})")
            print(f"      Reasons: {', '.join(rec['reasons'])}")
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
        return False
    
    # Test 3: Assess user skills
    print("\n🎯 Test 3: Assess User Skills")
    skills_payload = {
        "user_id": "api_test_user",
        "assessment_type": "quick"
    }
    response = requests.post(f"{BASE_URL}/learning-paths/assess-skills", json=skills_payload)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success: Assessed skills for {data['user_id']}")
        skills = data['skill_assessment']
        for skill, level in list(skills.items())[:5]:
            print(f"   - {skill}: {level:.2f}")
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
        return False
    
    # Test 4: Generate personalized path
    print("\n🛤️ Test 4: Generate Personalized Learning Path")
    path_payload = {
        "user_id": "api_test_user",
        "current_skill_levels": {
            "arrays": 0.4,
            "strings": 0.3,
            "hash_tables": 0.5,
            "trees": 0.2,
            "graphs": 0.1,
            "dynamic_programming": 0.1
        },
        "learning_goals": ["google", "interview_prep"],
        "available_hours_per_week": 12,
        "preferred_difficulty_curve": "gradual",
        "target_completion_weeks": 8,
        "weak_areas": ["dynamic_programming", "graphs"],
        "strong_areas": ["arrays"]
    }
    
    response = requests.post(f"{BASE_URL}/learning-paths/generate", json=path_payload)
    if response.status_code == 200:
        data = response.json()
        path = data['learning_path']
        print(f"✅ Success: Generated learning path")
        print(f"   - Path ID: {path['id']}")
        print(f"   - Name: {path['name']}")
        print(f"   - Total Problems: {path['problem_count']}")
        print(f"   - Completion: {path['completion_percentage']}%")
        path_id = path['id']
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
        return False
    
    # Test 5: Get next problems
    print("\n📚 Test 5: Get Next Problems")
    response = requests.get(f"{BASE_URL}/learning-paths/{path_id}/next-problems?count=3")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success: Retrieved {data['returned_count']} next problems")
        for i, problem in enumerate(data['problems']):
            print(f"   {i+1}. {problem['title']} ({problem['difficulty']})")
            if 'learning_context' in problem:
                context = problem['learning_context']
                print(f"      Position: {context['position_in_path']}/{context['total_problems']}")
                print(f"      Focus: {', '.join(context.get('focus_areas', []))}")
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
        return False
    
    # Test 6: Get learning path details
    print("\n📝 Test 6: Get Learning Path Details")
    response = requests.get(f"{BASE_URL}/learning-paths/{path_id}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success: Retrieved learning path details")
        print(f"   - Status: {data['status']}")
        print(f"   - Current Position: {data['current_position']}")
        print(f"   - Milestones: {data.get('milestone_count', 0)}")
        if 'milestones' in data:
            completed_milestones = len([m for m in data['milestones'] if m['is_completed']])
            print(f"   - Completed Milestones: {completed_milestones}/{len(data['milestones'])}")
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
        return False
    
    # Test 7: Get analytics
    print("\n📊 Test 7: Get Learning Paths Analytics")
    response = requests.get(f"{BASE_URL}/learning-paths/analytics/overview")
    if response.status_code == 200:
        data = response.json()
        overview = data['overview']
        print(f"✅ Success: Retrieved analytics overview")
        print(f"   - Total Templates: {overview['total_templates']}")
        print(f"   - Total User Paths: {overview['total_user_paths']}")
        print(f"   - Active Paths: {overview['active_paths']}")
        print(f"   - Completion Rate: {overview['completion_rate']}%")
        print(f"   - Total Milestones: {overview['total_milestones']}")
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
        return False
    
    print("\n🎉 All API tests completed successfully!")
    print("Learning Paths API is fully functional!")
    return True


if __name__ == "__main__":
    # Wait a moment for server to be ready
    time.sleep(2)
    
    try:
        test_learning_paths_api()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")

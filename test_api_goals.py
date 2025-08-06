import requests
import json

# Test the fixed learning path generation
def test_api_with_different_goals():
    base_url = "http://127.0.0.1:8001"
    
    # Test array-focused path
    print("Testing array-focused learning path via API:")
    array_profile = {
        "user_id": 1,
        "current_skill_levels": {"array": "beginner", "overall": "beginner"},
        "learning_goals": ["array"],
        "available_hours_per_week": 10,
        "preferred_difficulty_curve": "gradual",
        "target_completion_weeks": 4,
        "weak_areas": ["array"],
        "strong_areas": []
    }
    
    response = requests.post(f"{base_url}/api/learning-paths/generate", json=array_profile)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Generated path with {len(data['weekly_plan'])} weeks")
        week1 = data['weekly_plan'][0]
        print(f"Week 1 has {len(week1['problems'])} problems:")
        for p in week1['problems'][:3]:
            print(f"  - {p['title']} [{p['difficulty']}] - {p['algorithm_tags']}")
    else:
        print(f"Error: {response.text}")
    
    print("\n" + "="*50 + "\n")
    
    # Test greedy-focused path
    print("Testing greedy-focused learning path via API:")
    greedy_profile = {
        "user_id": 2,
        "current_skill_levels": {"greedy": "beginner", "overall": "beginner"},
        "learning_goals": ["greedy"],
        "available_hours_per_week": 10,
        "preferred_difficulty_curve": "gradual",
        "target_completion_weeks": 4,
        "weak_areas": ["greedy"],
        "strong_areas": []
    }
    
    response = requests.post(f"{base_url}/api/learning-paths/generate", json=greedy_profile)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Generated path with {len(data['weekly_plan'])} weeks")
        week1 = data['weekly_plan'][0]
        print(f"Week 1 has {len(week1['problems'])} problems:")
        for p in week1['problems'][:3]:
            print(f"  - {p['title']} [{p['difficulty']}] - {p['algorithm_tags']}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_api_with_different_goals()

import requests
import json

def test_frontend_integration():
    """Test what the frontend would send after our fixes"""
    
    # This is the exact request the frontend will now send
    frontend_request = {
        'user_id': 'frontend_integration_test',
        'current_skill_levels': {
            'array': 0.3,           # matches database algorithm_tags
            'hash_table': 0.2,      # matches database algorithm_tags
            'binary_search': 0.1,   # matches database algorithm_tags
            'two_pointers': 0.2,    # matches database algorithm_tags
            'sliding_window': 0.1,  # matches database algorithm_tags
            'greedy': 0.2,          # matches database algorithm_tags
            'sorting': 0.2,         # matches database algorithm_tags
            'string': 0.2           # matches database algorithm_tags
        },
        'learning_goals': ['google_interview'],
        'available_hours_per_week': 10,
        'preferred_difficulty_curve': 'gradual',
        'target_completion_weeks': 8,
        'weak_areas': ['binary_search', 'sliding_window'],
        'strong_areas': ['array', 'hash_table']
    }
    
    try:
        print("🧪 Testing Frontend Integration...")
        response = requests.post(
            'http://127.0.0.1:8000/learning-paths/generate',
            json=frontend_request,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            learning_path = result['learning_path']
            
            print("✅ API Response Structure Check:")
            print(f"   - ID: {learning_path['id']}")
            print(f"   - Target Goal: {learning_path['target_goal']}")
            print(f"   - Duration: {learning_path['duration_weeks']} weeks")
            print(f"   - Total Problems: {learning_path['total_problems']}")
            
            # Check weekly plan structure
            weekly_plan = learning_path['weekly_plan']
            print(f"\n📅 Weekly Plan Structure:")
            print(f"   - Number of weeks: {len(weekly_plan)}")
            
            # Test first week in detail
            if weekly_plan:
                first_week = weekly_plan[0]
                problems = first_week['problems']
                
                print(f"\n📋 Week 1 Details:")
                print(f"   - Problems count: {len(problems)}")
                print(f"   - Focus areas: {first_week['focus_areas']}")
                print(f"   - Estimated hours: {first_week['estimated_hours']}")
                
                # Check problem structure that frontend expects
                if problems and isinstance(problems[0], dict):
                    problem = problems[0]
                    required_fields = ['id', 'title', 'difficulty', 'platform', 'algorithm_tags']
                    missing_fields = [field for field in required_fields if field not in problem]
                    
                    if not missing_fields:
                        print("✅ Problem object structure is correct!")
                        print(f"   - Sample problem: {problem['title']} [{problem['difficulty']}]")
                        print(f"   - Platform: {problem['platform']}")
                        print(f"   - Tags: {problem['algorithm_tags'][:3]}")
                    else:
                        print(f"❌ Missing fields in problem object: {missing_fields}")
                else:
                    print("❌ Problems are not properly structured objects")
            
            # Check estimated completion time structure
            completion_time = learning_path['estimated_completion_time']
            print(f"\n⏱️ Time Estimates:")
            print(f"   - Total hours: {completion_time['total_hours']}")
            print(f"   - Hours per week: {completion_time['hours_per_week']}")
            print(f"   - Easy problems: {completion_time['easy_problems']}")
            print(f"   - Medium problems: {completion_time['medium_problems']}")
            print(f"   - Hard problems: {completion_time['hard_problems']}")
            
            print(f"\n🎉 Frontend integration should now work perfectly!")
            return True
            
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    test_frontend_integration()

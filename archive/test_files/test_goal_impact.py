import requests
import json

# Test with different goals and levels to see if they actually affect the output
test_cases = [
    {
        'name': 'Beginner + Data Structures',
        'user_id': 'test_beginner_ds',
        'current_skill_levels': {'array': 0.1, 'hash_table': 0.1},
        'learning_goals': ['data_structures'],
        'available_hours_per_week': 10,
        'preferred_difficulty_curve': 'gradual',
        'target_completion_weeks': 4,
        'weak_areas': ['array'],
        'strong_areas': []
    },
    {
        'name': 'Advanced + Interview Prep',
        'user_id': 'test_advanced_interview',
        'current_skill_levels': {'array': 0.8, 'hash_table': 0.8, 'graphs': 0.7},
        'learning_goals': ['google_interview'],
        'available_hours_per_week': 10,
        'preferred_difficulty_curve': 'steep',
        'target_completion_weeks': 4,
        'weak_areas': [],
        'strong_areas': ['array', 'hash_table']
    }
]

for i, test_case in enumerate(test_cases):
    print(f'\n=== Test {i+1}: {test_case["name"]} ===')
    try:
        response = requests.post('http://127.0.0.1:8000/learning-paths/generate', json=test_case)
        if response.status_code == 200:
            result = response.json()
            learning_path = result['learning_path']
            
            print(f'Goal: {learning_path.get("target_goal", "N/A")}')
            print(f'Level indicators: Current={learning_path.get("current_level", "N/A")}')
            
            # Check first few problems
            problems = learning_path.get('personalized_sequence', [])[:3]
            print(f'First 3 problems: {problems}')
            
            # Check problem difficulties
            weekly_plan = learning_path.get('weekly_plan', [])
            if weekly_plan:
                week1_problems = weekly_plan[0].get('problems', [])
                difficulties = [p.get('difficulty', 'Unknown') for p in week1_problems]
                tags = [p.get('algorithm_tags', [])[:2] for p in week1_problems]
                print(f'Week 1 difficulties: {difficulties}')
                print(f'Week 1 algorithm tags: {tags}')
        else:
            print(f'API Error: {response.status_code} - {response.text}')
    except Exception as e:
        print(f'Request failed: {e}')

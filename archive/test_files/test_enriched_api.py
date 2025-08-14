import requests
import json

# Test the updated API with enriched problem data
frontend_request = {
    'user_id': 'frontend_test_user_v2',
    'current_skill_levels': {
        'arrays': 0.3,
        'strings': 0.2,
        'hash_tables': 0.2,
        'trees': 0.1,
        'dynamic_programming': 0.1,
        'graphs': 0.1,
        'sorting': 0.2,
        'searching': 0.2
    },
    'learning_goals': ['google_interview'],
    'available_hours_per_week': 10,
    'preferred_difficulty_curve': 'gradual',
    'target_completion_weeks': 8,
    'weak_areas': ['dynamic_programming', 'graphs'],
    'strong_areas': ['arrays', 'strings']
}

try:
    response = requests.post(
        'http://127.0.0.1:8000/learning-paths/generate',
        json=frontend_request,
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        learning_path = result.get('learning_path', {})
        weekly_plan = learning_path.get('weekly_plan', [])
        
        print(f'✅ SUCCESS: Generated {len(learning_path.get("personalized_sequence", []))} problems')
        print(f'Weekly plan has {len(weekly_plan)} weeks')
        
        if weekly_plan:
            first_week = weekly_plan[0]
            problems = first_week.get('problems', [])
            print(f'\nFirst week has {len(problems)} problems:')
            for i, problem in enumerate(problems):
                if isinstance(problem, dict):
                    title = problem.get('title', 'Unknown')
                    difficulty = problem.get('difficulty', 'Unknown')
                    platform = problem.get('platform', 'Unknown')
                    tags = problem.get('algorithm_tags', [])
                    print(f'  {i+1}. {title} [{difficulty}] from {platform}')
                    print(f'      Tags: {tags[:3]}')
                else:
                    print(f'  {i+1}. Problem ID: {problem}')
                    
            focus_areas = first_week.get('focus_areas', [])
            print(f'\nFocus areas: {focus_areas}')
        else:
            print('❌ No weekly plan found')
    else:
        print(f'❌ ERROR: {response.status_code} - {response.text}')
        
except Exception as e:
    print(f'❌ Request failed: {e}')

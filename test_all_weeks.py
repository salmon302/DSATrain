import requests
import json

frontend_request = {
    'user_id': 'test_all_weeks',
    'current_skill_levels': {
        'arrays': 0.3, 'hash_tables': 0.2, 'trees': 0.1,
        'dynamic_programming': 0.1, 'graphs': 0.1, 'sorting': 0.2
    },
    'learning_goals': ['google_interview'],
    'available_hours_per_week': 10,
    'preferred_difficulty_curve': 'gradual',
    'target_completion_weeks': 4,  # Shorter for testing
    'weak_areas': ['dynamic_programming', 'graphs'],
    'strong_areas': ['arrays']
}

try:
    response = requests.post('http://127.0.0.1:8000/learning-paths/generate', json=frontend_request)
    
    if response.status_code == 200:
        result = response.json()
        weekly_plan = result['learning_path']['weekly_plan']
        
        print(f'Testing {len(weekly_plan)} weeks:')
        for week in weekly_plan:
            problems = week['problems']
            focus_areas = week['focus_areas']
            print(f'\nWeek {week["week"]}: {len(problems)} problems, Focus: {focus_areas}')
            for problem in problems:
                title = problem['title']
                difficulty = problem['difficulty']
                tags = problem['algorithm_tags'][:2]
                print(f'  - {title} [{difficulty}] - {tags}')
    else:
        print(f'Error: {response.status_code}')
        
except Exception as e:
    print(f'Failed: {e}')

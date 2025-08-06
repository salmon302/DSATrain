import requests
import json

try:
    print('Testing learning path generation...')
    
    # Prepare test data with correct schema and realistic skill names that match database
    request_data = {
        'user_id': 'test_user_123',
        'current_skill_levels': {
            'array': 0.3,           # matches algorithm_tags in database
            'hash_table': 0.2,      # matches algorithm_tags in database
            'binary_search': 0.1,   # matches algorithm_tags in database
            'sliding_window': 0.1,  # matches algorithm_tags in database
            'two_pointers': 0.2     # matches algorithm_tags in database
        },
        'learning_goals': [
            'master_basic_algorithms',
            'prepare_for_interviews', 
            'improve_problem_solving'
        ],
        'available_hours_per_week': 10,
        'preferred_difficulty_curve': 'gradual',
        'target_completion_weeks': 12,
        'weak_areas': ['binary_search', 'sliding_window'],
        'strong_areas': ['array']
    }
    
    print('Request data prepared')
    
    # Make POST request
    response = requests.post(
        'http://127.0.0.1:8000/learning-paths/generate',
        json=request_data,
        timeout=30
    )
    
    print(f'Response status: {response.status_code}')
    
    if response.status_code == 200:
        result = response.json()
        print('✅ SUCCESS: Learning path generated!')
        print('Full response:')
        print(json.dumps(result, indent=2))
        
        # Check the actual structure
        learning_path = result.get("learning_path", {})
        print(f'Learning path ID: {learning_path.get("id")}')
        print(f'Template ID: {learning_path.get("template_id")}')
        print(f'Problems count: {len(learning_path.get("personalized_sequence", []))}')
        print(f'Message: {result.get("message")}')
        
        # Check if personalized_sequence exists and show sample problems
        sequence = learning_path.get("personalized_sequence", [])
        if sequence:
            print(f'\\nFirst few problems in sequence:')
            for i, problem_id in enumerate(sequence[:3]):
                print(f'  {i+1}. Problem ID: {problem_id}')
        else:
            print('\\n❌ No problems found in personalized_sequence!')
            print('Available fields in learning_path:')
            for key in learning_path.keys():
                value = learning_path[key]
                if isinstance(value, list):
                    print(f'  {key}: list with {len(value)} items')
                elif isinstance(value, dict):
                    print(f'  {key}: dict with keys {list(value.keys())}')
                else:
                    print(f'  {key}: {type(value).__name__}')
    else:
        print(f'❌ ERROR: Status {response.status_code}')
        print(f'Response: {response.text}')
        
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()

import requests
import json

# Test the Google Code Analysis API
data = {
    'code': '''def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []''',
    'language': 'python',
    'thinking_out_loud': True,
    'communication_notes': ['Explained approach', 'Discussed complexity']
}

try:
    response = requests.post('http://localhost:8000/google/analyze', json=data)
    result = response.json()
    
    print('✅ Google Analysis API working!')
    print(f'Overall Score: {result["google_criteria"]["overall_score"]}/100')
    print(f'Time Complexity: {result["complexity"]["time_complexity"]}')
    print(f'GCA Score: {result["google_criteria"]["gca_score"]}/100')
    print(f'Communication Score: {result["google_criteria"]["communication_score"]}/100')
    print('\n💡 Suggestions:')
    for suggestion in result.get('suggestions', [])[:3]:
        print(f'  • {suggestion}')
        
except Exception as e:
    print(f'❌ Error: {e}')

"""
Phase 4 API Demo Script
Demonstrates the capabilities of the DSA Training Platform API
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_json(data, title="Response"):
    """Pretty print JSON data"""
    print(f"\n{title}:")
    print(json.dumps(data, indent=2))

def demo_api():
    """Demonstrate API capabilities"""
    
    print_header("🚀 DSA Training Platform API Demo")
    
    try:
        # 1. Health Check
        print_header("1. Health Check")
        response = requests.get(f"{BASE_URL}/")
        print_json(response.json(), "API Status")
        
        # 2. Platform Statistics
        print_header("2. Platform Statistics")
        response = requests.get(f"{BASE_URL}/stats")
        print_json(response.json(), "Platform Stats")
        
        # 3. All Problems
        print_header("3. All Problems")
        response = requests.get(f"{BASE_URL}/problems")
        data = response.json()
        print(f"Total Problems: {data['count']}")
        print(f"Sample Problem: {data['problems'][0]['title']}")
        print_json(data['problems'][0], "First Problem Details")
        
        # 4. Filter by Platform
        print_header("4. LeetCode Problems Only")
        response = requests.get(f"{BASE_URL}/problems?platform=leetcode")
        data = response.json()
        print(f"LeetCode Problems: {data['count']}")
        print("Titles:", [p['title'] for p in data['problems']])
        
        # 5. Filter by Difficulty
        print_header("5. Medium Difficulty Problems")
        response = requests.get(f"{BASE_URL}/problems?difficulty=Medium")
        data = response.json()
        print(f"Medium Problems: {data['count']}")
        print("Titles:", [p['title'] for p in data['problems']])
        
        # 6. High Quality Problems
        print_header("6. High Quality Problems (>80 score)")
        response = requests.get(f"{BASE_URL}/problems?min_quality=80")
        data = response.json()
        print(f"High Quality Problems: {data['count']}")
        for problem in data['problems']:
            print(f"  - {problem['title']}: Quality {problem['quality_score']}, Relevance {problem['google_interview_relevance']}")
        
        # 7. Recommendations
        print_header("7. Problem Recommendations")
        response = requests.get(f"{BASE_URL}/recommendations?difficulty_level=Medium&focus_area=hash_table")
        data = response.json()
        print(f"Recommendations: {data['count']}")
        for rec in data['recommendations']:
            print(f"  - {rec['title']}: {rec['recommendation_reason']}")
        
        # 8. Platform Analytics
        print_header("8. Platform Analytics")
        response = requests.get(f"{BASE_URL}/analytics/platforms")
        print_json(response.json(), "Platform Breakdown")
        
        # 9. Difficulty Analytics
        print_header("9. Difficulty Analytics")
        response = requests.get(f"{BASE_URL}/analytics/difficulty")
        print_json(response.json(), "Difficulty Breakdown")
        
        # 10. Search
        print_header("10. Search Functionality")
        response = requests.get(f"{BASE_URL}/search?query=sum")
        data = response.json()
        print(f"Search Results for 'sum': {data['count']}")
        print("Found:", [p['title'] for p in data['results']])
        
        print_header("✅ Demo Complete - API Fully Functional!")
        print(f"API Documentation: {BASE_URL}/docs")
        print(f"Alternative Docs: {BASE_URL}/redoc")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: API server not running!")
        print("Please start the server first:")
        print("python src/api/main.py")
    except Exception as e:
        print(f"❌ Error during demo: {e}")

if __name__ == "__main__":
    demo_api()

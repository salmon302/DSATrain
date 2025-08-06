"""Simple test for enhanced stats"""
import requests
import time

# Wait a moment for server to be ready
time.sleep(2)

try:
    response = requests.get("http://127.0.0.1:8003/enhanced-stats/overview", timeout=10)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        overview = data.get('overview', {})
        print(f"✅ SUCCESS!")
        print(f"Total Problems: {overview.get('total_problems', 0):,}")
        print(f"High Relevance Problems: {overview.get('high_relevance_problems', 0):,}")
        print(f"Interview Ready Problems: {overview.get('interview_ready_problems', 0):,}")
        print(f"Coverage Score: {overview.get('coverage_score', 0)}%")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Connection error: {e}")

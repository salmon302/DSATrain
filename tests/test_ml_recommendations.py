"""
Test script for the enhanced ML recommendation system
Phase 4 Week 2 - Testing ML recommendations and user tracking

Note: This file exercises a live external server (localhost:8000).
It is skipped by default in automated test runs. To enable, set
environment variable RUN_EXTERNAL_API_TESTS=1.
"""

import requests
import json
import time
from datetime import datetime
import os
import pytest

# Skip entire module unless explicitly enabled
pytestmark = pytest.mark.skipif(
    not os.getenv("RUN_EXTERNAL_API_TESTS"),
    reason="Requires external API server on localhost:8000; set RUN_EXTERNAL_API_TESTS=1 to run.",
)

# API base URL
BASE_URL = "http://localhost:8000"

def test_basic_recommendations():
    """Test basic recommendations without user ID"""
    print("🔍 Testing basic recommendations...")
    
    response = requests.get(f"{BASE_URL}/recommendations?limit=3")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Basic recommendations: {data['count']} problems returned")
        print(f"   Type: {data['type']}")
        print(f"   ML Powered: {data['ml_powered']}")
        return True
    else:
        print(f"❌ Basic recommendations failed: {response.status_code}")
        return False

def test_personalized_recommendations():
    """Test personalized ML recommendations"""
    print("\n🤖 Testing personalized ML recommendations...")
    
    test_user_id = "test_user_123"
    response = requests.get(
        f"{BASE_URL}/recommendations",
        params={
            "user_id": test_user_id,
            "difficulty_level": "Medium",
            "limit": 5
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Personalized recommendations: {data['count']} problems returned")
        print(f"   Type: {data['type']}")
        print(f"   ML Powered: {data['ml_powered']}")
        print(f"   User ID: {data['user_id']}")
        
        # Print first recommendation details
        if data['recommendations']:
            rec = data['recommendations'][0]
            print(f"   Sample recommendation: {rec['title']}")
            print(f"   Score: {rec.get('recommendation_score', 'N/A')}")
            print(f"   Reasoning: {rec.get('recommendation_reasoning', 'N/A')}")
        
        return True
    else:
        print(f"❌ Personalized recommendations failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

def test_similar_problems():
    """Test content-based similar problems"""
    print("\n🔗 Testing similar problems...")
    
    # First get a problem ID
    problems_response = requests.get(f"{BASE_URL}/problems?limit=1")
    if problems_response.status_code != 200:
        print("❌ Could not get problems for similarity test")
        return False
    
    problems_data = problems_response.json()
    if not problems_data['problems']:
        print("❌ No problems available for similarity test")
        return False
    
    problem_id = problems_data['problems'][0]['id']
    
    # Test similar problems
    response = requests.get(f"{BASE_URL}/recommendations/similar/{problem_id}?limit=3")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Similar problems: {data['count']} problems returned")
        print(f"   Reference problem: {data['reference_problem_id']}")
        print(f"   Algorithm: {data['algorithm']}")
        
        # Print similarity scores
        for similar in data['similar_problems']:
            print(f"   - {similar['title']}: similarity {similar.get('similarity_score', 'N/A')}")
        
        return True
    else:
        print(f"❌ Similar problems failed: {response.status_code}")
        return False

def test_user_interaction_tracking():
    """Test user interaction tracking"""
    print("\n📊 Testing user interaction tracking...")
    
    test_user_id = "test_user_123"
    
    # Get a problem ID for testing
    problems_response = requests.get(f"{BASE_URL}/problems?limit=1")
    if problems_response.status_code != 200:
        print("❌ Could not get problems for interaction test")
        return False
    
    problem_id = problems_response.json()['problems'][0]['id']
    
    # Test tracking a problem view
    response = requests.post(
        f"{BASE_URL}/interactions/track",
        params={
            "user_id": test_user_id,
            "problem_id": problem_id,
            "action": "viewed",
            "time_spent": 120,
            "session_id": "test_session_123"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Interaction tracking: {data['status']}")
        print(f"   Message: {data['message']}")
        return True
    else:
        print(f"❌ Interaction tracking failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

def test_learning_path_generation():
    """Test learning path generation"""
    print("\n🛤️ Testing learning path generation...")
    
    test_user_id = "test_user_123"
    response = requests.get(
        f"{BASE_URL}/learning-paths/generate",
        params={
            "user_id": test_user_id,
            "goal": "google_interview",
            "level": "intermediate",
            "duration_weeks": 4
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        learning_path = data['learning_path']
        print(f"✅ Learning path generated: {learning_path['total_problems']} problems")
        print(f"   Duration: {learning_path['duration_weeks']} weeks")
        print(f"   Goal: {learning_path['target_goal']}")
        print(f"   Level: {learning_path['current_level']}")
        
        # Print weekly plan summary
        for week in learning_path['weekly_plan'][:2]:  # Show first 2 weeks
            print(f"   Week {week['week']}: {len(week['problems'])} problems, {week['estimated_hours']} hours")
            print(f"      Focus areas: {', '.join(week['focus_areas'][:3])}")
        
        return True
    else:
        print(f"❌ Learning path generation failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

def test_ml_training():
    """Test ML model training"""
    print("\n🎓 Testing ML model training...")
    
    response = requests.post(f"{BASE_URL}/ml/train")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ ML training: {data['status']}")
        print(f"   Message: {data['message']}")
        return True
    else:
        print(f"❌ ML training failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

def test_user_analytics():
    """Test user analytics"""
    print("\n📈 Testing user analytics...")
    
    test_user_id = "test_user_123"
    response = requests.get(f"{BASE_URL}/analytics/user/{test_user_id}?days_back=30")
    
    if response.status_code == 200:
        data = response.json()
        analytics = data['user_analytics']
        print(f"✅ User analytics: {analytics['total_interactions']} interactions")
        print(f"   Period: {data['period_days']} days")
        if analytics['total_interactions'] > 0:
            print(f"   Activity summary: {analytics.get('activity_summary', {})}")
        return True
    else:
        print(f"❌ User analytics failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

def main():
    """Run all ML recommendation system tests"""
    print("🚀 DSA Training Platform - ML Recommendation System Test Suite")
    print("=" * 70)
    
    tests = [
        test_basic_recommendations,
        test_personalized_recommendations,
        test_similar_problems,
        test_user_interaction_tracking,
        test_learning_path_generation,
        test_ml_training,
        test_user_analytics
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            time.sleep(0.5)  # Small delay between tests
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
    
    print("\n" + "=" * 70)
    print(f"🏆 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All ML recommendation features are working correctly!")
        print("✅ Phase 4 Week 2 ML Enhancement: SUCCESSFUL")
    else:
        print(f"⚠️ {total - passed} tests failed - need to investigate")
    
    print(f"\n📅 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()

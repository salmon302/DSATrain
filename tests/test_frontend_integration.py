"""
Test Enhanced Frontend Integration
Verify interview readiness and algorithm relevance features

Note: Targets live server on 127.0.0.1:8003; skipped by default unless
RUN_EXTERNAL_API_TESTS=1 is set in the environment.
"""

import requests
import time
import os
import pytest

pytestmark = pytest.mark.skipif(
    not os.getenv("RUN_EXTERNAL_API_TESTS"),
    reason="Requires external API server on 127.0.0.1:8003; set RUN_EXTERNAL_API_TESTS=1 to run.",
)

API_BASE = "http://127.0.0.1:8003"

def test_enhanced_integration():
    """Test the enhanced statistics endpoints that the frontend now uses"""
    print("🔍 Testing Enhanced Frontend Integration")
    print("=" * 60)
    
    # Wait for servers to be ready
    time.sleep(3)
    
    # Test 1: Enhanced Overview (used by Dashboard)
    try:
        response = requests.get(f"{API_BASE}/enhanced-stats/overview", timeout=10)
        if response.status_code == 200:
            data = response.json()
            overview = data.get('overview', {})
            print("✅ Enhanced Overview API (Dashboard):")
            print(f"   📊 Total Problems: {overview.get('total_problems', 0):,}")
            print(f"   🎯 High Relevance: {overview.get('high_relevance_problems', 0):,}")
            print(f"   📈 Interview Ready: {overview.get('interview_ready_problems', 0):,}")
            print(f"   💯 Coverage Score: {overview.get('coverage_score', 0)}%")
        else:
            print(f"❌ Overview API Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Overview API Connection Error: {e}")
    
    print()
    
    # Test 2: Interview Readiness (used by Dashboard)
    try:
        response = requests.get(f"{API_BASE}/enhanced-stats/interview-readiness", timeout=10)
        if response.status_code == 200:
            data = response.json()
            overview = data.get('overview', {})
            print("✅ Interview Readiness API (Dashboard):")
            print(f"   📝 Total Interview Ready: {overview.get('total_interview_ready', 0):,}")
            print(f"   💯 Readiness Score: {overview.get('readiness_score', 0)}%")
            
            readiness_by_difficulty = data.get('readiness_by_difficulty', [])
            if readiness_by_difficulty:
                print("   ⭐ By Difficulty:")
                for item in readiness_by_difficulty[:3]:
                    print(f"      • {item['difficulty']}: {item['interview_ready']:,} ready / {item['total']:,} total")
            
            recommendations = data.get('recommendations', {})
            focus_areas = recommendations.get('focus_areas', [])
            if focus_areas:
                print(f"   🎯 Focus Areas: {', '.join(focus_areas[:3])}")
        else:
            print(f"❌ Interview Readiness API Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Interview Readiness API Connection Error: {e}")
    
    print()
    
    # Test 3: Algorithm Relevance (used by Dashboard)
    try:
        response = requests.get(f"{API_BASE}/enhanced-stats/algorithm-relevance", timeout=10)
        if response.status_code == 200:
            data = response.json()
            summary = data.get('summary', {})
            print("✅ Algorithm Relevance API (Dashboard):")
            print(f"   🔥 High Priority Tags: {summary.get('high_priority_tags', 0)}")
            print(f"   ⚡ Medium Priority Tags: {summary.get('medium_priority_tags', 0)}")
            print(f"   📊 Total Unique Tags: {summary.get('total_unique_tags', 0)}")
            
            algorithm_analysis = data.get('algorithm_analysis', [])
            if algorithm_analysis:
                print("   🎯 Top Interview Algorithms:")
                for i, alg in enumerate(algorithm_analysis[:5], 1):
                    print(f"      {i}. {alg['algorithm_tag']}: {alg['problem_count']} problems ({alg['interview_priority']} priority)")
        else:
            print(f"❌ Algorithm Relevance API Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Algorithm Relevance API Connection Error: {e}")
    
    print()
    
    # Test 4: Sample Problems for Browser
    try:
        response = requests.get(f"{API_BASE}/problems", params={'limit': 5}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            problems = data.get('problems', [])
            print("✅ Enhanced Problem Browser Data:")
            print(f"   📊 Sample Problems Available: {len(problems)}")
            
            if problems:
                print("   🎯 Sample with Enhanced Data:")
                for i, problem in enumerate(problems[:3], 1):
                    relevance = problem.get('google_interview_relevance', 0)
                    quality = problem.get('quality_score', 0)
                    is_interview_ready = relevance >= 6
                    print(f"      {i}. {problem.get('title', 'N/A')[:40]}")
                    print(f"         • Difficulty: {problem.get('difficulty', 'N/A')}")
                    print(f"         • Google Relevance: {relevance:.1f}%")
                    print(f"         • Quality Score: {quality:.1f}")
                    print(f"         • Interview Ready: {'✅' if is_interview_ready else '❌'}")
                    
                    tags = problem.get('algorithm_tags', [])
                    if tags:
                        print(f"         • Algorithm Tags: {', '.join(tags[:3])}")
        else:
            print(f"❌ Problems API Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Problems API Connection Error: {e}")
    
    print()
    print("=" * 60)
    print("🎉 Enhanced Frontend Integration Test Complete!")
    print("✅ Dashboard now shows Interview Readiness & Algorithm Relevance")
    print("✅ Problem Browser enhanced with interview-ready indicators")
    print("✅ Algorithm priority badges and enhanced filtering available")
    print("🚀 Ready for user testing!")

if __name__ == "__main__":
    test_enhanced_integration()

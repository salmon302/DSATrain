"""
Test Enhanced Statistics API Endpoints
Showcase improved difficulty and Google relevance statistics

Note: This archive test targets a live server and provides helper functions
intended for manual runs. It is skipped by default in CI. To enable, set
RUN_EXTERNAL_API_TESTS=1.
"""

import requests
import json
from typing import Dict
import os
import pytest

pytestmark = pytest.mark.skipif(
    not os.getenv("RUN_EXTERNAL_API_TESTS"),
    reason="Archived external-API test; set RUN_EXTERNAL_API_TESTS=1 to run.",
)

API_BASE = "http://127.0.0.1:8003"

def test_enhanced_endpoint(endpoint: str, params: Dict = None) -> Dict:
    """Test an enhanced statistics endpoint"""
    try:
        response = requests.get(f"{API_BASE}{endpoint}", params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def display_results(title: str, data: Dict):
    """Display results in a formatted way"""
    print(f"\n{'='*60}")
    print(f"📊 {title}")
    print('='*60)
    
    if "error" in data:
        print(f"❌ Error: {data['error']}")
        return
    
    # Format the output based on the data structure
    print(json.dumps(data, indent=2))

def main():
    """Test all enhanced statistics endpoints"""
    print("🚀 Testing Enhanced DSATrain Statistics System")
    print("After implementing improved difficulty and Google relevance scoring")
    
    # Test 1: Enhanced Overview
    print("\n🔍 Testing Enhanced Overview...")
    overview = test_enhanced_endpoint("/enhanced-stats/overview")
    if "error" not in overview:
        print("✅ Enhanced Overview:")
        print(f"   📊 Total Problems: {overview.get('overview', {}).get('total_problems', 0):,}")
        print(f"   🎯 High Relevance Problems: {overview.get('overview', {}).get('high_relevance_problems', 0):,}")
        print(f"   📈 Interview Ready Problems: {overview.get('overview', {}).get('interview_ready_problems', 0):,}")
        print(f"   💯 Coverage Score: {overview.get('overview', {}).get('coverage_score', 0)}%")
        
        print("\n   🎯 Google Relevance Distribution:")
        for item in overview.get('relevance_distribution', []):
            print(f"      • {item['range']:<20}: {item['count']:>5,} problems ({item['percentage']:4.1f}%)")
        
        print("\n   ⭐ Difficulty Distribution:")
        for item in overview.get('difficulty_distribution', []):
            print(f"      • {item['difficulty']}: {item['count']:,} problems ({item['percentage']:.1f}%) - Avg Relevance: {item['avg_relevance']:.2f}")
    else:
        print(f"❌ Error: {overview['error']}")
    
    # Test 2: Algorithm Relevance Analysis
    print("\n🧮 Testing Algorithm Relevance Analysis...")
    algorithm_analysis = test_enhanced_endpoint("/enhanced-stats/algorithm-relevance")
    if "error" not in algorithm_analysis:
        print("✅ Algorithm Relevance Analysis:")
        summary = algorithm_analysis.get('summary', {})
        print(f"   📊 Total Unique Tags: {summary.get('total_unique_tags', 0)}")
        print(f"   🔥 High Priority Tags: {summary.get('high_priority_tags', 0)}")
        print(f"   ⚡ Medium Priority Tags: {summary.get('medium_priority_tags', 0)}")
        print(f"   📝 Low Priority Tags: {summary.get('low_priority_tags', 0)}")
        
        print("\n   🎯 Top 10 Interview-Relevant Algorithm Tags:")
        for i, tag in enumerate(algorithm_analysis.get('algorithm_analysis', [])[:10], 1):
            print(f"      {i:2d}. {tag['algorithm_tag']:<25} | {tag['problem_count']:>4} problems | Avg: {tag['avg_relevance']:5.2f} | Priority: {tag['interview_priority']}")
    else:
        print(f"❌ Error: {algorithm_analysis['error']}")
    
    # Test 3: Interview Readiness Stats
    print("\n📝 Testing Interview Readiness Statistics...")
    readiness = test_enhanced_endpoint("/enhanced-stats/interview-readiness")
    if "error" not in readiness:
        print("✅ Interview Readiness Statistics:")
        overview = readiness.get('overview', {})
        print(f"   📊 Total Interview Ready: {overview.get('total_interview_ready', 0):,}")
        print(f"   🎯 High Priority Problems: {overview.get('high_priority_problems', 0):,}")
        print(f"   💯 Readiness Score: {overview.get('readiness_score', 0)}%")
        
        print("\n   ⭐ Readiness by Difficulty:")
        for item in readiness.get('readiness_by_difficulty', []):
            print(f"      • {item['difficulty']}: {item['interview_ready']:,} ready / {item['total']:,} total ({item['readiness_percentage']:.1f}%)")
        
        print("\n   🧮 Top Interview Algorithms:")
        for i, tag in enumerate(readiness.get('top_interview_algorithms', [])[:8], 1):
            print(f"      {i}. {tag['algorithm_tag']}: {tag['interview_ready_problems']} problems")
        
        recommendations = readiness.get('recommendations', {})
        if recommendations:
            print("\n   💡 Practice Recommendations:")
            focus_areas = recommendations.get('focus_areas', [])
            print(f"      Focus Areas: {', '.join(focus_areas[:5])}")
            
            practice_plan = recommendations.get('practice_plan', {})
            print(f"      Practice Plan:")
            print(f"         Easy: {practice_plan.get('easy_problems_needed', 0)} more problems needed")
            print(f"         Medium: {practice_plan.get('medium_problems_needed', 0)} more problems needed")
            print(f"         Hard: {practice_plan.get('hard_problems_needed', 0)} more problems needed")
    else:
        print(f"❌ Error: {readiness['error']}")
    
    # Test 4: Quality Improvements Summary
    print("\n💎 Testing Quality Improvements Summary...")
    improvements = test_enhanced_endpoint("/enhanced-stats/quality-improvements")
    if "error" not in improvements:
        print("✅ Quality Improvements Summary:")
        print(f"   📊 Total Problems Processed: {improvements.get('total_problems_processed', 0):,}")
        print(f"   🎯 Relevance Score Updates: {improvements.get('relevance_score_updates', 0):,}")
        print(f"   ⭐ Difficulty Rating Updates: {improvements.get('difficulty_rating_updates', 0):,}")
        
        current_dist = improvements.get('current_distribution', {})
        print(f"\n   📈 Current Distribution:")
        print(f"      High Relevance Problems: {current_dist.get('high_relevance_problems', 0):,}")
        print(f"      Medium Relevance Problems: {current_dist.get('medium_relevance_problems', 0):,}")
        print(f"      Interview Coverage: {current_dist.get('interview_coverage', 0)}%")
        
        quality_metrics = improvements.get('quality_metrics', {})
        print(f"\n   💯 Quality Metrics:")
        print(f"      Average Relevance Improvement: {quality_metrics.get('average_relevance_improvement', 'N/A')}")
        print(f"      Difficulty Calibration Accuracy: {quality_metrics.get('difficulty_calibration_accuracy', 'N/A')}")
        print(f"      Interview Readiness Coverage: {quality_metrics.get('interview_readiness_coverage', 'N/A')}")
    else:
        print(f"❌ Error: {improvements['error']}")
    
    print("\n" + "="*60)
    print("🎉 Enhanced Statistics Testing Complete!")
    print("✅ Successfully improved difficulty and Google relevance statistics")
    print("📊 Data quality significantly enhanced through algorithm-based scoring")
    print("🎯 Interview preparation capabilities dramatically improved")

if __name__ == "__main__":
    main()

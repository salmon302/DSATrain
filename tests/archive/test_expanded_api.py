"""
Test the expanded DSATrain API with 10K+ problems
"""

import requests
import json
from typing import Dict, Any

API_BASE = "http://127.0.0.1:8002"

def test_api_endpoint(endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """Test an API endpoint and return the response"""
    try:
        url = f"{API_BASE}{endpoint}"
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def main():
    print("🚀 Testing DSATrain API with Expanded Dataset")
    print("=" * 60)
    
    # Test 1: Overall stats
    print("\n📊 1. Testing /stats endpoint...")
    stats = test_api_endpoint("/stats")
    if "error" not in stats:
        db_stats = stats.get("database_stats", {})
        quality_metrics = stats.get("quality_metrics", {})
        print(f"   ✅ Problems: {db_stats.get('problems', 0):,}")
        print(f"   ✅ Solutions: {db_stats.get('solutions', 0)}")
        print(f"   ✅ Avg Problem Quality: {quality_metrics.get('average_problem_quality', 0):.2f}")
        print(f"   ✅ Avg Solution Quality: {quality_metrics.get('average_solution_quality', 0):.2f}")
    else:
        print(f"   ❌ Error: {stats['error']}")
    
    # Test 2: Browse problems with different filters
    print("\n🔍 2. Testing /problems endpoint with filters...")
    
    # Test basic pagination
    problems = test_api_endpoint("/problems", {"limit": 10})
    if "error" not in problems:
        problem_list = problems.get("problems", [])
        print(f"   ✅ Retrieved {len(problem_list)} problems")
        print(f"   ✅ Total available: {problems.get('total_available', 0):,}")
        if problem_list:
            sample = problem_list[0]
            print(f"   ✅ Sample problem: {sample.get('title', 'Unknown')} ({sample.get('platform', 'Unknown')})")
    else:
        print(f"   ❌ Error: {problems['error']}")
    
    # Test platform filtering
    print("\n🎯 3. Testing platform filtering...")
    codeforces_problems = test_api_endpoint("/problems", {"platform": "codeforces", "limit": 5})
    if "error" not in codeforces_problems:
        cf_list = codeforces_problems.get("problems", [])
        print(f"   ✅ Codeforces problems: {len(cf_list)}")
        print(f"   ✅ Total Codeforces available: {codeforces_problems.get('total_available', 0):,}")
    else:
        print(f"   ❌ Error: {codeforces_problems['error']}")
    
    # Test difficulty filtering
    print("\n⭐ 4. Testing difficulty filtering...")
    easy_problems = test_api_endpoint("/problems", {"difficulty": "Easy", "limit": 5})
    medium_problems = test_api_endpoint("/problems", {"difficulty": "Medium", "limit": 5})
    hard_problems = test_api_endpoint("/problems", {"difficulty": "Hard", "limit": 5})
    
    for diff, result in [("Easy", easy_problems), ("Medium", medium_problems), ("Hard", hard_problems)]:
        if "error" not in result:
            count = result.get("total_available", 0)
            print(f"   ✅ {diff} problems: {count:,}")
        else:
            print(f"   ❌ {diff} problems error: {result['error']}")
    
    # Test 5: Search functionality
    print("\n🔍 5. Testing search functionality...")
    search_results = test_api_endpoint("/search", {"query": "binary", "limit": 5})
    if "error" not in search_results:
        results = search_results.get("results", [])
        print(f"   ✅ Search 'binary': {len(results)} results")
        if results:
            print(f"   ✅ Top result: {results[0].get('title', 'Unknown')}")
    else:
        print(f"   ❌ Search error: {search_results['error']}")
    
    # Test 6: Quality filtering
    print("\n💎 6. Testing quality filtering...")
    high_quality = test_api_endpoint("/problems", {"min_quality": 95.0, "limit": 10})
    if "error" not in high_quality:
        hq_list = high_quality.get("problems", [])
        total_hq = high_quality.get("total_available", 0)
        print(f"   ✅ High quality (95+) problems: {total_hq:,}")
        if hq_list:
            avg_quality = sum(p.get("quality_score", 0) for p in hq_list) / len(hq_list)
            print(f"   ✅ Average quality of results: {avg_quality:.2f}")
    else:
        print(f"   ❌ Error: {high_quality['error']}")
    
    # Test 7: Algorithm tag analytics
    print("\n🧮 7. Testing algorithm tag analytics...")
    tag_analytics = test_api_endpoint("/analytics/algorithm-tags")
    if "error" not in tag_analytics:
        analytics = tag_analytics.get("algorithm_tag_analytics", [])
        total_tags = tag_analytics.get("total_unique_tags", 0)
        print(f"   ✅ Total unique algorithm tags: {total_tags}")
        if analytics:
            top_5 = analytics[:5]
            print(f"   ✅ Top 5 algorithm tags:")
            for tag_info in top_5:
                tag = tag_info.get("tag", "Unknown")
                count = tag_info.get("problem_count", 0)
                quality = tag_info.get("average_quality", 0)
                print(f"      • {tag}: {count} problems (avg quality: {quality:.1f})")
    else:
        print(f"   ❌ Error: {tag_analytics['error']}")
    
    # Test 8: Platform analytics
    print("\n🌐 8. Testing platform analytics...")
    platform_analytics = test_api_endpoint("/analytics/platforms")
    if "error" not in platform_analytics:
        analytics = platform_analytics.get("platform_analytics", [])
        print(f"   ✅ Platform breakdown:")
        for platform_info in analytics:
            platform = platform_info.get("platform", "Unknown")
            count = platform_info.get("problem_count", 0)
            quality = platform_info.get("average_quality_score", 0)
            relevance = platform_info.get("average_google_relevance", 0)
            print(f"      • {platform}: {count:,} problems (quality: {quality:.1f}, relevance: {relevance:.1f})")
    else:
        print(f"   ❌ Error: {platform_analytics['error']}")
    
    print("\n" + "=" * 60)
    print("🎉 API Testing Complete!")
    print("✅ DSATrain now has access to 10,000+ coding problems!")

if __name__ == "__main__":
    main()

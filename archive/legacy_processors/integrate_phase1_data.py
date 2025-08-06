"""
Data Integration Script - Phase 1 Completion
Combines Codeforces and LeetCode datasets into unified collections

This script creates the final unified datasets for:
1. All problems (Codeforces + LeetCode)
2. Google-relevant problems (cross-platform)
3. Training sets by difficulty
4. Comprehensive analytics
"""

import json
from pathlib import Path
from datetime import datetime
from collections import Counter
from typing import List, Dict, Any

def load_codeforces_data():
    """Load processed Codeforces data"""
    cf_file = Path("data/processed/problems_unified.json")
    if not cf_file.exists():
        print("❌ Codeforces data not found. Run process_full_data.py first.")
        return []
    
    with open(cf_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✅ Loaded {len(data)} Codeforces problems")
    return data

def load_leetcode_data():
    """Load processed LeetCode data"""
    lc_file = Path("data/processed/leetcode_problems_unified.json")
    if not lc_file.exists():
        print("❌ LeetCode data not found. Run collect_leetcode.py first.")
        return []
    
    with open(lc_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✅ Loaded {len(data)} LeetCode problems")
    return data

def standardize_difficulty_ratings(problems):
    """Standardize difficulty ratings across platforms"""
    print("🔧 Standardizing difficulty ratings...")
    
    for problem in problems:
        source = problem['source']
        rating = problem['difficulty'].get('rating')
        level = problem['difficulty']['level']
        
        # Standardize rating system (0-4000 scale)
        if source == 'leetcode':
            # Convert LeetCode estimated ratings to standardized scale
            if level == 'easy':
                std_rating = rating if rating else 1200
            elif level == 'medium':
                std_rating = rating if rating else 1600  
            else:  # hard
                std_rating = rating if rating else 2400
        else:  # codeforces
            std_rating = rating if rating else 1500
        
        problem['difficulty']['standardized_rating'] = std_rating
        
        # Add standardized level based on standardized rating
        if std_rating <= 1200:
            std_level = 'easy'
        elif std_rating <= 2000:
            std_level = 'medium'  
        else:
            std_level = 'hard'
        
        problem['difficulty']['standardized_level'] = std_level
    
    print("✅ Difficulty ratings standardized")
    return problems

def create_google_relevance_scores(problems):
    """Calculate Google relevance scores for all problems"""
    print("🎯 Calculating Google relevance scores...")
    
    # Google-relevant keywords
    google_keywords = {
        'algorithms', 'data_structures', 'dynamic_programming', 'dp', 
        'graphs', 'trees', 'arrays', 'strings', 'binary_search', 
        'sorting', 'hashing', 'hash_table', 'greedy', 'divide_and_conquer',
        'backtracking', 'recursion', 'two_pointers', 'sliding_window',
        'linked_list', 'stack', 'queue', 'heap', 'trie'
    }
    
    for problem in problems:
        score = 0
        
        # Tag-based scoring
        problem_tags = set(problem['tags'])
        tag_matches = len(problem_tags.intersection(google_keywords))
        score += tag_matches * 2
        
        # Company tag bonus
        company_tags = problem.get('company_tags', [])
        if any('google' in tag.lower() for tag in company_tags):
            score += 10
        
        # Difficulty preference (Google likes medium-hard problems)
        std_rating = problem['difficulty']['standardized_rating']
        if 1400 <= std_rating <= 2200:
            score += 3
        elif 1200 <= std_rating <= 1400 or 2200 <= std_rating <= 2800:
            score += 1
        
        # Source bonus (LeetCode problems often more interview-focused)
        if problem['source'] == 'leetcode':
            score += 2
        
        # Popularity bonus (for Codeforces)
        if problem['source'] == 'codeforces':
            solved_count = problem['metadata'].get('solved_count', 0)
            if solved_count > 5000:
                score += 2
            elif solved_count > 1000:
                score += 1
        
        problem['google_relevance_score'] = score
    
    print("✅ Google relevance scores calculated")
    return problems

def create_unified_collections(cf_problems, lc_problems):
    """Create unified problem collections"""
    print("🔗 Creating unified collections...")
    
    # Combine all problems
    all_problems = cf_problems + lc_problems
    
    # Standardize ratings and calculate relevance
    all_problems = standardize_difficulty_ratings(all_problems)
    all_problems = create_google_relevance_scores(all_problems)
    
    # Create Google-relevant subset (score >= 5)
    google_problems = [p for p in all_problems if p['google_relevance_score'] >= 5]
    google_problems.sort(key=lambda x: x['google_relevance_score'], reverse=True)
    
    # Create difficulty-based collections
    easy_problems = [p for p in all_problems if p['difficulty']['standardized_level'] == 'easy']
    medium_problems = [p for p in all_problems if p['difficulty']['standardized_level'] == 'medium']
    hard_problems = [p for p in all_problems if p['difficulty']['standardized_level'] == 'hard']
    
    # Create platform-specific Google collections
    google_cf = [p for p in google_problems if p['source'] == 'codeforces']
    google_lc = [p for p in google_problems if p['source'] == 'leetcode']
    
    collections = {
        'all_problems': all_problems,
        'google_problems': google_problems,
        'easy_problems': easy_problems[:1000],  # Limit to top 1000
        'medium_problems': medium_problems[:1000],
        'hard_problems': hard_problems[:1000],
        'google_codeforces': google_cf[:500],
        'google_leetcode': google_lc,
        'top_google_100': google_problems[:100],
        'interview_practice_set': google_problems[:200]  # Top 200 for interview practice
    }
    
    print(f"✅ Created {len(collections)} unified collections")
    return collections

def create_comprehensive_analytics(collections):
    """Create comprehensive analytics across all data"""
    print("📊 Creating comprehensive analytics...")
    
    all_problems = collections['all_problems']
    google_problems = collections['google_problems']
    
    # Basic statistics
    total_problems = len(all_problems)
    cf_problems = len([p for p in all_problems if p['source'] == 'codeforces'])
    lc_problems = len([p for p in all_problems if p['source'] == 'leetcode'])
    
    # Difficulty analysis
    difficulty_dist = Counter(p['difficulty']['standardized_level'] for p in all_problems)
    
    # Rating analysis
    ratings = [p['difficulty']['standardized_rating'] for p in all_problems if p['difficulty']['standardized_rating']]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0
    
    # Google relevance analysis
    relevance_scores = [p['google_relevance_score'] for p in all_problems]
    avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0
    
    # Tag analysis
    all_tags = []
    for p in all_problems:
        all_tags.extend(p['tags'])
    tag_freq = Counter(all_tags)
    
    # Company analysis
    all_companies = []
    for p in all_problems:
        all_companies.extend(p.get('company_tags', []))
    company_freq = Counter(all_companies)
    
    # Source comparison
    source_comparison = {
        'codeforces': {
            'count': cf_problems,
            'avg_rating': sum(p['difficulty']['standardized_rating'] for p in all_problems 
                            if p['source'] == 'codeforces' and p['difficulty']['standardized_rating']) / cf_problems,
            'google_relevant': len([p for p in google_problems if p['source'] == 'codeforces'])
        },
        'leetcode': {
            'count': lc_problems,
            'avg_rating': sum(p['difficulty']['standardized_rating'] for p in all_problems 
                            if p['source'] == 'leetcode' and p['difficulty']['standardized_rating']) / lc_problems if lc_problems else 0,
            'google_relevant': len([p for p in google_problems if p['source'] == 'leetcode'])
        }
    }
    
    analytics = {
        "phase_1_summary": {
            "total_problems_collected": total_problems,
            "codeforces_problems": cf_problems,
            "leetcode_problems": lc_problems,
            "google_relevant_problems": len(google_problems),
            "collection_date": datetime.now().isoformat(),
            "data_coverage": f"{total_problems:,} problems across 2 platforms"
        },
        "difficulty_analysis": {
            "distribution": dict(difficulty_dist),
            "average_rating": round(avg_rating, 1),
            "rating_range": {
                "min": min(ratings) if ratings else None,
                "max": max(ratings) if ratings else None
            }
        },
        "google_relevance_analysis": {
            "average_relevance_score": round(avg_relevance, 2),
            "high_relevance_problems": len([p for p in all_problems if p['google_relevance_score'] >= 8]),
            "medium_relevance_problems": len([p for p in all_problems if 5 <= p['google_relevance_score'] < 8]),
            "low_relevance_problems": len([p for p in all_problems if p['google_relevance_score'] < 5])
        },
        "tag_analysis": {
            "total_unique_tags": len(tag_freq),
            "most_common_tags": dict(tag_freq.most_common(25)),
            "google_interview_tags": {
                tag: count for tag, count in tag_freq.most_common(50)
                if any(keyword in tag for keyword in ['dp', 'graph', 'tree', 'array', 'string', 'search', 'sort'])
            }
        },
        "company_analysis": {
            "total_companies": len(company_freq),
            "most_frequent_companies": dict(company_freq.most_common(15)),
            "google_tagged_problems": company_freq.get('google', 0)
        },
        "source_comparison": source_comparison,
        "collection_quality": {
            "data_completeness": {
                "problems_with_descriptions": len([p for p in all_problems if len(p['description']) > 20]),
                "problems_with_tags": len([p for p in all_problems if p['tags']]),
                "problems_with_ratings": len([p for p in all_problems if p['difficulty']['standardized_rating']]),
                "problems_with_source_urls": len([p for p in all_problems if p['metadata'].get('source_url')])
            },
            "google_readiness": {
                "interview_ready_problems": len(collections['interview_practice_set']),
                "difficulty_coverage": {
                    "easy": len([p for p in google_problems if p['difficulty']['standardized_level'] == 'easy']),
                    "medium": len([p for p in google_problems if p['difficulty']['standardized_level'] == 'medium']),
                    "hard": len([p for p in google_problems if p['difficulty']['standardized_level'] == 'hard'])
                }
            }
        }
    }
    
    print("✅ Comprehensive analytics created")
    return analytics

def save_unified_data(collections, analytics):
    """Save all unified data and collections"""
    print("💾 Saving unified data...")
    
    # Ensure directories exist
    unified_dir = Path("data/unified")
    final_exports_dir = Path("data/exports/final")
    
    for directory in [unified_dir, final_exports_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    
    saved_files = {}
    
    # Save main unified collection
    all_problems_file = unified_dir / "all_problems_unified.json"
    with open(all_problems_file, 'w', encoding='utf-8') as f:
        json.dump(collections['all_problems'], f, indent=2, ensure_ascii=False)
    saved_files['all_problems'] = str(all_problems_file)
    print(f"📄 Saved all problems: {all_problems_file}")
    
    # Save Google-relevant collections
    google_all_file = final_exports_dir / "google_problems_all_platforms.json"
    with open(google_all_file, 'w', encoding='utf-8') as f:
        json.dump(collections['google_problems'], f, indent=2, ensure_ascii=False)
    saved_files['google_all'] = str(google_all_file)
    print(f"🎯 Saved Google problems (all platforms): {google_all_file}")
    
    # Save interview practice set
    interview_file = final_exports_dir / "interview_practice_set.json"
    with open(interview_file, 'w', encoding='utf-8') as f:
        json.dump(collections['interview_practice_set'], f, indent=2, ensure_ascii=False)
    saved_files['interview_practice'] = str(interview_file)
    print(f"🎓 Saved interview practice set: {interview_file}")
    
    # Save top 100 Google problems
    top100_file = final_exports_dir / "top_100_google_interview_problems.json"
    with open(top100_file, 'w', encoding='utf-8') as f:
        json.dump(collections['top_google_100'], f, indent=2, ensure_ascii=False)
    saved_files['top_100'] = str(top100_file)
    print(f"🏆 Saved top 100 Google problems: {top100_file}")
    
    # Save by difficulty
    for difficulty in ['easy', 'medium', 'hard']:
        if difficulty + '_problems' in collections:
            diff_file = final_exports_dir / f"unified_{difficulty}_problems.json"
            with open(diff_file, 'w', encoding='utf-8') as f:
                json.dump(collections[f'{difficulty}_problems'], f, indent=2, ensure_ascii=False)
            saved_files[f'{difficulty}_problems'] = str(diff_file)
            print(f"📚 Saved {difficulty} problems: {diff_file}")
    
    # Save comprehensive analytics
    analytics_file = unified_dir / "phase1_comprehensive_analytics.json"
    with open(analytics_file, 'w', encoding='utf-8') as f:
        json.dump(analytics, f, indent=2, ensure_ascii=False)
    saved_files['analytics'] = str(analytics_file)
    print(f"📊 Saved comprehensive analytics: {analytics_file}")
    
    return saved_files

def print_phase1_completion_summary(collections, analytics):
    """Print Phase 1 completion summary"""
    print("\n" + "="*80)
    print("🎉 PHASE 1 DATA COLLECTION COMPLETED!")
    print("="*80)
    
    phase_summary = analytics['phase_1_summary']
    print(f"📊 COLLECTION SUMMARY:")
    print(f"   Total Problems: {phase_summary['total_problems_collected']:,}")
    print(f"   Codeforces: {phase_summary['codeforces_problems']:,}")
    print(f"   LeetCode: {phase_summary['leetcode_problems']:,}")
    print(f"   Google-Relevant: {phase_summary['google_relevant_problems']:,}")
    
    print(f"\n🎯 GOOGLE INTERVIEW READINESS:")
    google_analysis = analytics['google_relevance_analysis']
    quality_info = analytics['collection_quality']['google_readiness']
    print(f"   High-Relevance Problems: {google_analysis['high_relevance_problems']:,}")
    print(f"   Interview Practice Set: {quality_info['interview_ready_problems']:,}")
    print(f"   Difficulty Coverage:")
    for diff, count in quality_info['difficulty_coverage'].items():
        print(f"     {diff.title()}: {count:,}")
    
    print(f"\n📋 DATA QUALITY:")
    completeness = analytics['collection_quality']['data_completeness']
    total = phase_summary['total_problems_collected']
    print(f"   Problems with Descriptions: {(completeness['problems_with_descriptions']/total)*100:.1f}%")
    print(f"   Problems with Tags: {(completeness['problems_with_tags']/total)*100:.1f}%")
    print(f"   Problems with Ratings: {(completeness['problems_with_ratings']/total)*100:.1f}%")
    print(f"   Problems with Source URLs: {(completeness['problems_with_source_urls']/total)*100:.1f}%")
    
    print(f"\n🏷️  TOP INTERVIEW TAGS:")
    interview_tags = analytics['tag_analysis']['google_interview_tags']
    for tag, count in list(interview_tags.items())[:8]:
        print(f"   {tag}: {count:,}")
    
    print(f"\n📁 KEY EXPORT FILES:")
    print(f"   🎯 Google Problems (All): data/exports/final/google_problems_all_platforms.json")
    print(f"   🎓 Interview Practice Set: data/exports/final/interview_practice_set.json")
    print(f"   🏆 Top 100 Google Problems: data/exports/final/top_100_google_interview_problems.json")
    print(f"   📊 Comprehensive Analytics: data/unified/phase1_comprehensive_analytics.json")
    print(f"   📚 Problems by Difficulty: data/exports/final/unified_[easy|medium|hard]_problems.json")
    
    print(f"\n✅ ACHIEVEMENTS:")
    print(f"   ✓ Successfully collected {phase_summary['total_problems_collected']:,} coding problems")
    print(f"   ✓ Identified {phase_summary['google_relevant_problems']:,} Google-relevant problems")
    print(f"   ✓ Created standardized data format across platforms")
    print(f"   ✓ Implemented Google relevance scoring system")
    print(f"   ✓ Generated interview-ready problem sets")
    print(f"   ✓ Created comprehensive analytics and reporting")
    
    print(f"\n🚀 READY FOR PHASE 2:")
    print(f"   • HackerRank Interview Kit collection")
    print(f"   • Academic dataset integration")
    print(f"   • Advanced data quality assessment")
    print(f"   • Machine learning model training")
    print(f"   • API development for data access")
    
    print("="*80)
    print("🎊 PHASE 1 SUCCESSFULLY COMPLETED! 🎊")
    print("="*80)

def main():
    """Main integration function"""
    print("Data Integration - Phase 1 Completion")
    print("="*60)
    
    # Load data from both sources
    cf_problems = load_codeforces_data()
    lc_problems = load_leetcode_data()
    
    if not cf_problems and not lc_problems:
        print("❌ No data available. Please run collection scripts first.")
        return
    
    # Create unified collections
    collections = create_unified_collections(cf_problems, lc_problems)
    
    # Create comprehensive analytics
    analytics = create_comprehensive_analytics(collections)
    
    # Save unified data
    saved_files = save_unified_data(collections, analytics)
    
    # Print completion summary
    print_phase1_completion_summary(collections, analytics)

if __name__ == "__main__":
    main()

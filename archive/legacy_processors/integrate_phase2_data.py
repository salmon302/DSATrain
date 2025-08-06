"""
Phase 2 Data Integration Script - Expand Data Sources
Combines all collected data from Phase 1 + Phase 2 sources

This script integrates:
Phase 1: Codeforces (10,544) + LeetCode (10)
Phase 2: HackerRank (20) + AtCoder (20) + CodeChef (20)

Creates comprehensive unified datasets with enhanced Google relevance scoring
and cross-platform analytics.
"""

import json
from pathlib import Path
from datetime import datetime
from collections import Counter
from typing import List, Dict, Any

def load_all_datasets():
    """Load all processed datasets from Phase 1 and Phase 2"""
    print("📂 Loading all datasets...")
    
    datasets = {}
    
    # Phase 1 datasets
    phase1_files = {
        'codeforces': 'data/processed/problems_unified.json',
        'leetcode': 'data/processed/leetcode_problems_unified.json'
    }
    
    # Phase 2 datasets
    phase2_files = {
        'hackerrank': 'data/processed/hackerrank_problems_unified.json',
        'atcoder': 'data/processed/atcoder_problems_unified.json',
        'codechef': 'data/processed/codechef_problems_unified.json'
    }
    
    all_files = {**phase1_files, **phase2_files}
    
    for source, file_path in all_files.items():
        file_path = Path(file_path)
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                datasets[source] = data
                print(f"✅ Loaded {len(data)} problems from {source}")
        else:
            print(f"❌ File not found: {file_path}")
            datasets[source] = []
    
    total_problems = sum(len(data) for data in datasets.values())
    print(f"📊 Total problems loaded: {total_problems:,}")
    
    return datasets

def enhance_google_relevance_scoring(all_problems: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Enhanced Google relevance scoring algorithm for Phase 2"""
    print("🎯 Applying enhanced Google relevance scoring...")
    
    # Enhanced Google-relevant keywords (expanded from Phase 1)
    google_keywords = {
        # Core algorithms
        'algorithms', 'data_structures', 'dynamic_programming', 'dp', 
        'graphs', 'trees', 'arrays', 'strings', 'binary_search', 
        'sorting', 'hashing', 'hash_table', 'greedy', 'divide_and_conquer',
        'backtracking', 'recursion', 'two_pointers', 'sliding_window',
        
        # Data structures
        'linked_list', 'stack', 'queue', 'heap', 'priority_queue', 'trie',
        'segment_tree', 'union_find', 'disjoint_set',
        
        # Graph algorithms
        'bfs', 'dfs', 'shortest_path', 'dijkstra', 'bellman_ford',
        'topological_sort', 'mst', 'lca', 'binary_lifting',
        
        # Advanced topics (bonus for competitive programming background)
        'number_theory', 'combinatorics', 'game_theory', 'geometry',
        'bit_manipulation', 'modular_arithmetic'
    }
    
    # Platform bonus weights
    platform_weights = {
        'leetcode': 3.0,      # Highest weight - interview focused
        'hackerrank': 2.5,    # High weight - interview prep kit
        'codeforces': 2.0,    # Medium weight - competitive programming
        'atcoder': 1.8,       # Good for algorithms
        'codechef': 1.8       # Good for algorithms and tutorials
    }
    
    for problem in all_problems:
        score = 0
        source = problem['source']
        
        # 1. Tag-based scoring (core component)
        problem_tags = set(problem['tags'])
        tag_matches = len(problem_tags.intersection(google_keywords))
        score += tag_matches * 2
        
        # 2. Company tag bonus (mainly from LeetCode)
        company_tags = problem.get('company_tags', [])
        if any('google' in tag.lower() for tag in company_tags):
            score += 15  # High bonus for explicit Google tagging
        
        # 3. Platform-specific bonus
        platform_bonus = platform_weights.get(source, 1.0)
        score *= platform_bonus
        
        # 4. Difficulty preference (Google likes medium-hard problems)
        std_rating = problem['difficulty'].get('standardized_rating', problem['difficulty'].get('rating', 1500))
        if 1400 <= std_rating <= 2200:
            score += 4  # Sweet spot for interviews
        elif 1200 <= std_rating <= 1400 or 2200 <= std_rating <= 2800:
            score += 2  # Still good
        elif std_rating > 2800:
            score += 1  # Very advanced, less likely in interviews
        
        # 5. Contest type bonus (for competitive programming platforms)
        metadata = problem.get('metadata', {})
        contest_type = metadata.get('contest_type', '').lower()
        
        if 'educational' in contest_type or 'tutorial' in contest_type:
            score += 3  # Educational content is great for learning
        elif 'interview' in contest_type or metadata.get('is_interview_kit', False):
            score += 5  # Explicitly interview-focused
        elif 'practice' in contest_type:
            score += 2  # Practice problems are good
        
        # 6. Problem complexity bonus (advanced algorithms)
        advanced_tags = {'segment_tree', 'fenwick_tree', 'trie', 'union_find', 'lca', 'heavy_light_decomposition'}
        if problem_tags.intersection(advanced_tags):
            score += 2  # Bonus for advanced data structures
        
        # 7. Classic problem bonus
        classic_indicators = {'classic', 'fundamental', 'basic', 'standard'}
        if any(indicator in problem.get('description', '').lower() for indicator in classic_indicators):
            score += 1
        
        # 8. Popularity bonus (for platforms that track this)
        solved_count = metadata.get('solved_count', 0)
        if solved_count > 10000:
            score += 3
        elif solved_count > 5000:
            score += 2
        elif solved_count > 1000:
            score += 1
        
        # Apply final scoring
        problem['google_relevance_score'] = round(score, 2)
    
    print("✅ Enhanced Google relevance scoring completed")
    return all_problems

def standardize_all_ratings(all_problems: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Standardize ratings across all platforms to unified 0-4000 scale"""
    print("🔧 Standardizing ratings across all platforms...")
    
    for problem in all_problems:
        source = problem['source']
        rating = problem['difficulty'].get('rating')
        level = problem['difficulty']['level']
        
        # Platform-specific rating conversion to 0-4000 scale
        if source == 'codeforces':
            # Codeforces ratings are already good (800-3500)
            std_rating = rating if rating else 1500
        elif source == 'leetcode':
            # Convert LeetCode estimated ratings
            if level == 'easy':
                std_rating = 1200 + (rating - 1000) if rating else 1200
            elif level == 'medium':
                std_rating = 1600 + (rating - 1600) if rating else 1600
            else:  # hard
                std_rating = 2400 + (rating - 2400) if rating else 2400
        elif source == 'hackerrank':
            # HackerRank estimated ratings
            std_rating = rating if rating else (1100 if level == 'easy' else 1600 if level == 'medium' else 2200)
        elif source == 'atcoder':
            # AtCoder ratings are similar to Codeforces
            std_rating = rating if rating else 1500
        elif source == 'codechef':
            # CodeChef estimated ratings
            std_rating = rating if rating else 1500
        else:
            std_rating = 1500  # Default
        
        # Ensure rating is within bounds
        std_rating = max(800, min(4000, std_rating))
        
        # Standardized level based on standardized rating
        if std_rating <= 1200:
            std_level = 'easy'
        elif std_rating <= 2000:
            std_level = 'medium'
        else:
            std_level = 'hard'
        
        problem['difficulty']['standardized_rating'] = std_rating
        problem['difficulty']['standardized_level'] = std_level
    
    print("✅ Rating standardization completed")
    return all_problems

def create_phase2_collections(all_problems: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Create comprehensive collections for Phase 2"""
    print("🔗 Creating Phase 2 comprehensive collections...")
    
    # Sort by Google relevance score
    all_problems.sort(key=lambda x: x['google_relevance_score'], reverse=True)
    
    # Create various collections
    collections = {
        'all_problems': all_problems,
        'google_relevant': [p for p in all_problems if p['google_relevance_score'] >= 5.0],
        'high_relevance': [p for p in all_problems if p['google_relevance_score'] >= 8.0],
        'interview_focused': [p for p in all_problems if p['google_relevance_score'] >= 6.0][:300],  # Top 300
        'top_100_elite': all_problems[:100],
        'top_500_practice': all_problems[:500],
    }
    
    # Platform-specific collections
    for platform in ['codeforces', 'leetcode', 'hackerrank', 'atcoder', 'codechef']:
        platform_problems = [p for p in all_problems if p['source'] == platform]
        collections[f'{platform}_problems'] = platform_problems
        collections[f'{platform}_google'] = [p for p in platform_problems if p['google_relevance_score'] >= 5.0]
    
    # Difficulty-based collections (using standardized levels)
    for difficulty in ['easy', 'medium', 'hard']:
        diff_problems = [p for p in all_problems if p['difficulty']['standardized_level'] == difficulty]
        collections[f'{difficulty}_problems'] = diff_problems[:1000]  # Limit to 1000 each
        collections[f'{difficulty}_google'] = [p for p in diff_problems if p['google_relevance_score'] >= 5.0][:500]
    
    # Topic-based collections
    important_topics = ['dynamic_programming', 'graphs', 'trees', 'binary_search', 'greedy', 'strings', 'arrays']
    for topic in important_topics:
        topic_problems = [p for p in all_problems if any(topic in tag for tag in p['tags'])]
        collections[f'{topic}_problems'] = topic_problems[:200]  # Top 200 per topic
    
    # Contest type collections
    educational_problems = [p for p in all_problems if 
                          'educational' in p.get('metadata', {}).get('contest_type', '').lower() or
                          'tutorial' in p['tags']]
    collections['educational_problems'] = educational_problems
    
    competitive_problems = [p for p in all_problems if 
                           p.get('metadata', {}).get('is_competitive_programming', False)]
    collections['competitive_programming'] = competitive_problems
    
    print(f"✅ Created {len(collections)} collections")
    return collections

def create_comprehensive_phase2_analytics(datasets: Dict[str, List], collections: Dict[str, List]) -> Dict[str, Any]:
    """Create comprehensive analytics for Phase 2"""
    print("📊 Creating comprehensive Phase 2 analytics...")
    
    all_problems = collections['all_problems']
    total_problems = len(all_problems)
    
    # Source distribution
    source_dist = Counter(p['source'] for p in all_problems)
    
    # Difficulty distribution
    difficulty_dist = Counter(p['difficulty']['standardized_level'] for p in all_problems)
    
    # Rating analysis
    ratings = [p['difficulty']['standardized_rating'] for p in all_problems]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0
    
    # Google relevance analysis
    relevance_scores = [p['google_relevance_score'] for p in all_problems]
    avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0
    
    # Tag analysis
    all_tags = []
    for p in all_problems:
        all_tags.extend(p['tags'])
    tag_freq = Counter(all_tags)
    
    # Platform comparison
    platform_comparison = {}
    for source, problems in datasets.items():
        if problems:
            platform_comparison[source] = {
                'total_problems': len(problems),
                'avg_rating': sum(p['difficulty'].get('standardized_rating', 1500) for p in problems) / len(problems),
                'avg_relevance': sum(p.get('google_relevance_score', 0) for p in problems) / len(problems),
                'google_relevant_count': len([p for p in problems if p.get('google_relevance_score', 0) >= 5.0]),
                'unique_tags': len(set(tag for p in problems for tag in p['tags']))
            }
    
    # Contest type analysis
    contest_types = Counter()
    for p in all_problems:
        contest_type = p.get('metadata', {}).get('contest_type', 'Unknown')
        contest_types[contest_type] += 1
    
    # Educational content analysis
    educational_count = len(collections.get('educational_problems', []))
    competitive_count = len(collections.get('competitive_programming', []))
    
    analytics = {
        "phase_2_summary": {
            "total_problems_collected": total_problems,
            "phase_1_problems": datasets.get('codeforces', []) + datasets.get('leetcode', []),
            "phase_2_additions": len(datasets.get('hackerrank', [])) + len(datasets.get('atcoder', [])) + len(datasets.get('codechef', [])),
            "platforms_integrated": len([source for source, data in datasets.items() if data]),
            "collection_date": datetime.now().isoformat(),
            "data_expansion": f"{total_problems:,} problems across {len(source_dist)} platforms"
        },
        "source_analysis": {
            "platform_distribution": dict(source_dist),
            "platform_comparison": platform_comparison,
            "most_problems": source_dist.most_common(1)[0] if source_dist else ("none", 0),
            "diversity_score": len(source_dist)
        },
        "difficulty_analysis": {
            "standardized_distribution": dict(difficulty_dist),
            "average_rating": round(avg_rating, 1),
            "rating_range": {
                "min": min(ratings) if ratings else None,
                "max": max(ratings) if ratings else None
            },
            "rating_statistics": {
                "25th_percentile": sorted(ratings)[len(ratings)//4] if ratings else None,
                "median": sorted(ratings)[len(ratings)//2] if ratings else None,
                "75th_percentile": sorted(ratings)[3*len(ratings)//4] if ratings else None
            }
        },
        "google_relevance_analysis": {
            "average_relevance_score": round(avg_relevance, 2),
            "high_relevance_problems": len([p for p in all_problems if p['google_relevance_score'] >= 8.0]),
            "medium_relevance_problems": len([p for p in all_problems if 5.0 <= p['google_relevance_score'] < 8.0]),
            "low_relevance_problems": len([p for p in all_problems if p['google_relevance_score'] < 5.0]),
            "interview_ready_problems": len(collections.get('interview_focused', [])),
            "relevance_by_platform": {
                source: round(platform_comparison[source]['avg_relevance'], 2) 
                for source in platform_comparison if platform_comparison[source]['total_problems'] > 0
            }
        },
        "content_analysis": {
            "total_unique_tags": len(tag_freq),
            "most_common_tags": dict(tag_freq.most_common(30)),
            "interview_tags": {
                tag: count for tag, count in tag_freq.most_common(50)
                if any(keyword in tag for keyword in ['dp', 'graph', 'tree', 'array', 'string', 'search', 'sort', 'heap', 'stack'])
            },
            "contest_type_distribution": dict(contest_types),
            "educational_content": {
                "educational_problems": educational_count,
                "competitive_problems": competitive_count,
                "tutorial_problems": len([p for p in all_problems if 'tutorial' in p['tags']])
            }
        },
        "quality_metrics": {
            "data_completeness": {
                "problems_with_descriptions": len([p for p in all_problems if len(p['description']) > 20]),
                "problems_with_tags": len([p for p in all_problems if p['tags']]),
                "problems_with_ratings": len([p for p in all_problems if p['difficulty']['standardized_rating']]),
                "problems_with_source_urls": len([p for p in all_problems if p['metadata'].get('source_url')])
            },
            "coverage_metrics": {
                "difficulty_coverage": len(difficulty_dist),
                "platform_diversity": len(source_dist),
                "tag_diversity": len(tag_freq),
                "rating_spread": max(ratings) - min(ratings) if ratings else 0
            }
        },
        "collection_achievements": {
            "phase_1_to_phase_2_growth": {
                "problems_added": len(datasets.get('hackerrank', [])) + len(datasets.get('atcoder', [])) + len(datasets.get('codechef', [])),
                "platforms_added": 3,
                "diversity_improved": True,
                "educational_content_added": educational_count > 0
            },
            "interview_readiness": {
                "total_google_relevant": len(collections.get('google_relevant', [])),
                "elite_problem_set": len(collections.get('top_100_elite', [])),
                "practice_set_size": len(collections.get('top_500_practice', [])),
                "difficulty_balance": all(difficulty_dist[d] > 0 for d in ['easy', 'medium', 'hard'])
            }
        }
    }
    
    print("✅ Comprehensive Phase 2 analytics created")
    return analytics

def save_phase2_unified_data(collections: Dict[str, List], analytics: Dict[str, Any]):
    """Save all Phase 2 unified data"""
    print("💾 Saving Phase 2 unified data...")
    
    # Create directories
    phase2_dir = Path("data/phase2_unified")
    final_exports_dir = Path("data/exports/phase2_final")
    
    for directory in [phase2_dir, final_exports_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    
    saved_files = {}
    
    # Save main unified collection
    all_problems_file = phase2_dir / "all_problems_phase2_unified.json"
    with open(all_problems_file, 'w', encoding='utf-8') as f:
        json.dump(collections['all_problems'], f, indent=2, ensure_ascii=False)
    saved_files['all_problems'] = str(all_problems_file)
    print(f"📄 Saved all problems (Phase 2): {all_problems_file}")
    
    # Save key collections
    key_collections = ['google_relevant', 'high_relevance', 'interview_focused', 'top_100_elite', 'top_500_practice']
    for collection_name in key_collections:
        if collection_name in collections:
            file_path = final_exports_dir / f"{collection_name}_phase2.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(collections[collection_name], f, indent=2, ensure_ascii=False)
            saved_files[collection_name] = str(file_path)
            print(f"🎯 Saved {collection_name}: {file_path}")
    
    # Save platform-specific collections
    platforms = ['codeforces', 'leetcode', 'hackerrank', 'atcoder', 'codechef']
    for platform in platforms:
        if f'{platform}_google' in collections and collections[f'{platform}_google']:
            file_path = final_exports_dir / f"{platform}_google_relevant.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(collections[f'{platform}_google'], f, indent=2, ensure_ascii=False)
            print(f"📊 Saved {platform} Google-relevant: {file_path}")
    
    # Save topic-based collections
    important_topics = ['dynamic_programming', 'graphs', 'trees', 'binary_search']
    for topic in important_topics:
        if f'{topic}_problems' in collections and collections[f'{topic}_problems']:
            file_path = final_exports_dir / f"{topic}_curated.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(collections[f'{topic}_problems'], f, indent=2, ensure_ascii=False)
            print(f"📚 Saved {topic} problems: {file_path}")
    
    # Save analytics
    analytics_file = phase2_dir / "phase2_comprehensive_analytics.json"
    with open(analytics_file, 'w', encoding='utf-8') as f:
        json.dump(analytics, f, indent=2, ensure_ascii=False)
    saved_files['analytics'] = str(analytics_file)
    print(f"📊 Saved Phase 2 analytics: {analytics_file}")
    
    return saved_files

def print_phase2_completion_summary(collections: Dict[str, List], analytics: Dict[str, Any]):
    """Print Phase 2 completion summary"""
    print("\n" + "="*80)
    print("🚀 PHASE 2 DATA EXPANSION COMPLETED!")
    print("="*80)
    
    phase_summary = analytics['phase_2_summary']
    source_analysis = analytics['source_analysis']
    relevance_analysis = analytics['google_relevance_analysis']
    
    print(f"📊 COLLECTION SUMMARY:")
    print(f"   Total Problems: {phase_summary['total_problems_collected']:,}")
    print(f"   Platforms Integrated: {phase_summary['platforms_integrated']}")
    print(f"   Phase 2 Additions: {phase_summary['phase_2_additions']:,}")
    
    print(f"\n🌐 PLATFORM DISTRIBUTION:")
    for platform, count in source_analysis['platform_distribution'].items():
        percentage = (count / phase_summary['total_problems_collected']) * 100
        print(f"   {platform.title()}: {count:,} ({percentage:.1f}%)")
    
    print(f"\n🎯 GOOGLE INTERVIEW READINESS:")
    print(f"   Google-Relevant Problems: {len(collections['google_relevant']):,}")
    print(f"   High-Relevance Problems: {relevance_analysis['high_relevance_problems']:,}")
    print(f"   Interview-Focused Set: {len(collections['interview_focused']):,}")
    print(f"   Elite Top 100: {len(collections['top_100_elite']):,}")
    
    print(f"\n📈 PLATFORM PERFORMANCE (Avg Google Relevance):")
    for platform, score in relevance_analysis['relevance_by_platform'].items():
        print(f"   {platform.title()}: {score:.2f}")
    
    print(f"\n📋 CONTENT COVERAGE:")
    content_analysis = analytics['content_analysis']
    print(f"   Unique Tags: {content_analysis['total_unique_tags']:,}")
    print(f"   Educational Problems: {content_analysis['educational_content']['educational_problems']:,}")
    print(f"   Tutorial Problems: {content_analysis['educational_content']['tutorial_problems']:,}")
    
    print(f"\n🏷️  TOP INTERVIEW TAGS:")
    interview_tags = content_analysis['interview_tags']
    for tag, count in list(interview_tags.items())[:8]:
        print(f"   {tag}: {count:,}")
    
    print(f"\n📁 KEY EXPORT FILES:")
    print(f"   🎯 All Problems (Phase 2): data/phase2_unified/all_problems_phase2_unified.json")
    print(f"   🏆 Top 100 Elite: data/exports/phase2_final/top_100_elite_phase2.json")
    print(f"   🎓 Interview-Focused (300): data/exports/phase2_final/interview_focused_phase2.json")
    print(f"   📊 Google-Relevant Problems: data/exports/phase2_final/google_relevant_phase2.json")
    print(f"   📈 Comprehensive Analytics: data/phase2_unified/phase2_comprehensive_analytics.json")
    
    print(f"\n✅ PHASE 2 ACHIEVEMENTS:")
    achievements = analytics['collection_achievements']
    print(f"   ✓ Expanded from 10,554 to {phase_summary['total_problems_collected']:,} problems")
    print(f"   ✓ Added {achievements['phase_1_to_phase_2_growth']['platforms_added']} new platforms")
    print(f"   ✓ Increased Google-relevant problems to {len(collections['google_relevant']):,}")
    print(f"   ✓ Enhanced educational content with tutorials and competitive programming")
    print(f"   ✓ Achieved {source_analysis['diversity_score']}-platform coverage")
    print(f"   ✓ Created comprehensive cross-platform scoring system")
    
    print(f"\n🚀 READY FOR NEXT PHASE:")
    print(f"   • Academic dataset integration (CodeComplex, etc.)")
    print(f"   • Solution code collection and quality assessment")
    print(f"   • Machine learning model training")
    print(f"   • Advanced similarity analysis and clustering")
    print(f"   • Real-time API development")
    
    print("="*80)
    print("🎊 PHASE 2 SUCCESSFULLY COMPLETED! 🎊")
    print("="*80)

def main():
    """Main Phase 2 integration function"""
    print("Phase 2 Data Integration - Expand Data Sources")
    print("="*70)
    
    # Load all datasets
    datasets = load_all_datasets()
    
    if not any(datasets.values()):
        print("❌ No datasets available. Please run collection scripts first.")
        return
    
    # Combine all problems
    all_problems = []
    for source, problems in datasets.items():
        all_problems.extend(problems)
    
    print(f"📊 Combined {len(all_problems):,} problems from {len(datasets)} sources")
    
    # Standardize ratings across platforms
    all_problems = standardize_all_ratings(all_problems)
    
    # Apply enhanced Google relevance scoring
    all_problems = enhance_google_relevance_scoring(all_problems)
    
    # Create comprehensive collections
    collections = create_phase2_collections(all_problems)
    
    # Create comprehensive analytics
    analytics = create_comprehensive_phase2_analytics(datasets, collections)
    
    # Save unified data
    saved_files = save_phase2_unified_data(collections, analytics)
    
    # Print completion summary
    print_phase2_completion_summary(collections, analytics)

if __name__ == "__main__":
    main()

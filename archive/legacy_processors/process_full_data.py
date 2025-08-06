"""
Process the full Codeforces dataset and create standardized format
Convert to our Problem schema and create enriched datasets
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict, Counter

def load_codeforces_data():
    """Load the full Codeforces dataset"""
    data_file = Path("data/raw/codeforces/problems/problems_full.json")
    
    if not data_file.exists():
        print(f"❌ Data file not found: {data_file}")
        return None
    
    print(f"📂 Loading data from: {data_file}")
    with open(data_file, 'r', encoding='utf-8') as f:
        full_data = json.load(f)
    
    # Extract just the problems array from the full dataset
    if isinstance(full_data, dict) and 'problems' in full_data:
        data = full_data['problems']
        print(f"✅ Loaded {len(data)} problems from full dataset")
        print(f"📊 Dataset info: {full_data.get('total_problems', 'unknown')} total problems collected on {full_data.get('collection_date', 'unknown date')}")
    else:
        data = full_data
        print(f"✅ Loaded {len(data)} problems")
    
    return data

def convert_to_difficulty_level(rating):
    """Convert Codeforces rating to standard difficulty level"""
    if rating is None:
        return "unrated"
    elif rating <= 1200:
        return "easy"
    elif rating <= 2000:
        return "medium"
    else:
        return "hard"

def create_standardized_problems(codeforces_data):
    """Convert Codeforces data to standardized format"""
    print("🔄 Converting to standardized format...")
    
    standardized_problems = []
    
    for problem in codeforces_data:
        # Extract basic info
        contest_id = problem.get("contestId")
        index = problem.get("index", "")
        name = problem.get("name", "")
        rating = problem.get("rating")
        tags = problem.get("tags", [])
        
        # Create unique ID
        problem_id = f"cf_{contest_id}_{index}" if contest_id else f"cf_{name.replace(' ', '_').lower()}"
        
        # Create standardized problem
        std_problem = {
            "id": problem_id,
            "source": "codeforces",
            "title": name,
            "description": name,  # Limited description from API
            "difficulty": {
                "level": convert_to_difficulty_level(rating),
                "rating": rating,
                "source_scale": "codeforces_rating"
            },
            "tags": [tag.lower().replace(" ", "_") for tag in tags],
            "company_tags": [],  # Codeforces doesn't provide company tags
            "constraints": {
                "time_limit": f"{problem.get('timeLimit', 1000)}ms" if problem.get('timeLimit') else None,
                "memory_limit": f"{problem.get('memoryLimit', 262144)}KB" if problem.get('memoryLimit') else None
            },
            "test_cases": [],  # Would need separate scraping
            "editorial": None,  # Would need separate scraping
            "metadata": {
                "created_date": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "source_url": f"https://codeforces.com/contest/{contest_id}/problem/{index}" if contest_id and index else None,
                "acquisition_method": "api",
                "contest_id": contest_id,
                "problem_index": index,
                "solved_count": problem.get("solvedCount", 0)
            }
        }
        
        standardized_problems.append(std_problem)
    
    print(f"✅ Converted {len(standardized_problems)} problems to standardized format")
    return standardized_problems

def create_google_relevant_subset(problems):
    """Create subset of problems relevant for Google interviews"""
    print("🎯 Creating Google-relevant problem subset...")
    
    # Google-relevant tags based on common interview topics
    google_tags = {
        'dynamic_programming', 'dp', 'graphs', 'trees', 'data_structures',
        'binary_search', 'greedy', 'two_pointers', 'sliding_window',
        'divide_and_conquer', 'backtracking', 'recursion', 'arrays',
        'strings', 'hash_tables', 'sorting', 'heap', 'trie',
        'implementation', 'math', 'geometry', 'dfs', 'bfs'
    }
    
    google_relevant = []
    
    for problem in problems:
        problem_tags = set(problem['tags'])
        
        # Check if problem has Google-relevant tags
        relevance_score = len(problem_tags.intersection(google_tags))
        
        # Additional scoring based on difficulty and popularity
        rating = problem['difficulty']['rating']
        solved_count = problem['metadata'].get('solved_count', 0)
        
        # Prefer medium difficulty problems (typical for interviews)
        difficulty_bonus = 0
        if rating and 1200 <= rating <= 2200:
            difficulty_bonus = 2
        elif rating and 800 <= rating <= 1200:
            difficulty_bonus = 1
        
        # Prefer well-tested problems (higher solved count)
        popularity_bonus = 1 if solved_count > 1000 else 0
        
        total_score = relevance_score + difficulty_bonus + popularity_bonus
        
        if total_score >= 2:  # Minimum threshold for Google relevance
            problem['google_relevance_score'] = total_score
            google_relevant.append(problem)
    
    # Sort by relevance score
    google_relevant.sort(key=lambda x: x['google_relevance_score'], reverse=True)
    
    print(f"✅ Found {len(google_relevant)} Google-relevant problems")
    return google_relevant

def create_analytics_report(problems):
    """Create comprehensive analytics report"""
    print("📊 Creating analytics report...")
    
    # Basic statistics
    total_problems = len(problems)
    rated_problems = [p for p in problems if p['difficulty']['rating'] is not None]
    
    # Difficulty distribution
    difficulty_dist = Counter(p['difficulty']['level'] for p in problems)
    
    # Rating distribution
    ratings = [p['difficulty']['rating'] for p in rated_problems]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0
    
    # Tag analysis
    all_tags = []
    for p in problems:
        all_tags.extend(p['tags'])
    tag_frequency = Counter(all_tags)
    
    # Contest distribution
    contests = Counter(p['metadata'].get('contest_id') for p in problems if p['metadata'].get('contest_id'))
    
    # Time/Memory constraints analysis
    time_limits = [int(p['constraints']['time_limit'].replace('ms', '')) 
                  for p in problems if p['constraints'].get('time_limit')]
    memory_limits = [int(p['constraints']['memory_limit'].replace('KB', '')) 
                    for p in problems if p['constraints'].get('memory_limit')]
    
    report = {
        "collection_info": {
            "total_problems": total_problems,
            "rated_problems": len(rated_problems),
            "unrated_problems": total_problems - len(rated_problems),
            "collection_date": datetime.now().isoformat(),
            "source": "codeforces_api"
        },
        "difficulty_analysis": {
            "distribution": dict(difficulty_dist),
            "average_rating": round(avg_rating, 1) if avg_rating else None,
            "rating_range": {
                "min": min(ratings) if ratings else None,
                "max": max(ratings) if ratings else None
            }
        },
        "tag_analysis": {
            "total_unique_tags": len(tag_frequency),
            "most_common_tags": dict(tag_frequency.most_common(20)),
            "google_relevant_tags": {
                tag: count for tag, count in tag_frequency.most_common(50)
                if any(keyword in tag for keyword in ['dp', 'graph', 'tree', 'array', 'string', 'search', 'sort'])
            }
        },
        "contest_analysis": {
            "total_contests": len(contests),
            "most_active_contests": dict(contests.most_common(10))
        },
        "constraints_analysis": {
            "time_limits": {
                "average_ms": round(sum(time_limits) / len(time_limits)) if time_limits else None,
                "most_common_ms": Counter(time_limits).most_common(5) if time_limits else []
            },
            "memory_limits": {
                "average_kb": round(sum(memory_limits) / len(memory_limits)) if memory_limits else None,
                "most_common_kb": Counter(memory_limits).most_common(5) if memory_limits else []
            }
        }
    }
    
    print("✅ Analytics report created")
    return report

def save_processed_data(problems, google_subset, analytics):
    """Save all processed data to appropriate directories"""
    print("💾 Saving processed data...")
    
    # Ensure directories exist
    processed_dir = Path("data/processed")
    enriched_dir = Path("data/enriched")
    exports_dir = Path("data/exports")
    
    for directory in [processed_dir, enriched_dir, exports_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    
    # Save standardized problems
    problems_file = processed_dir / "problems_unified.json"
    with open(problems_file, 'w', encoding='utf-8') as f:
        json.dump(problems, f, indent=2, ensure_ascii=False)
    print(f"📄 Saved standardized problems: {problems_file}")
    
    # Save Google-relevant subset
    google_file = exports_dir / "google_relevant_problems.json"
    with open(google_file, 'w', encoding='utf-8') as f:
        json.dump(google_subset, f, indent=2, ensure_ascii=False)
    print(f"🎯 Saved Google-relevant problems: {google_file}")
    
    # Save analytics report
    analytics_file = enriched_dir / "codeforces_analytics.json"
    with open(analytics_file, 'w', encoding='utf-8') as f:
        json.dump(analytics, f, indent=2, ensure_ascii=False)
    print(f"📊 Saved analytics report: {analytics_file}")
    
    # Create quick reference files
    
    # Top Google problems (first 100)
    top_google_file = exports_dir / "top_100_google_problems.json"
    with open(top_google_file, 'w', encoding='utf-8') as f:
        json.dump(google_subset[:100], f, indent=2, ensure_ascii=False)
    print(f"🏆 Saved top 100 Google problems: {top_google_file}")
    
    # Problems by difficulty
    for difficulty in ['easy', 'medium', 'hard']:
        diff_problems = [p for p in problems if p['difficulty']['level'] == difficulty]
        if diff_problems:
            diff_file = exports_dir / f"{difficulty}_problems.json"
            with open(diff_file, 'w', encoding='utf-8') as f:
                json.dump(diff_problems[:500], f, indent=2, ensure_ascii=False)  # Limit to 500 per difficulty
            print(f"📚 Saved {difficulty} problems: {diff_file}")
    
    return {
        "problems_file": str(problems_file),
        "google_file": str(google_file),
        "analytics_file": str(analytics_file),
        "top_google_file": str(top_google_file)
    }

def print_summary(problems, google_subset, analytics):
    """Print processing summary"""
    print("\n" + "="*60)
    print("🎉 DATA PROCESSING COMPLETED!")
    print("="*60)
    
    print(f"📊 Total Problems Processed: {len(problems):,}")
    print(f"🎯 Google-Relevant Problems: {len(google_subset):,}")
    print(f"📈 Success Rate: {(len(problems)/10544)*100:.1f}%")
    
    print(f"\n📋 Difficulty Distribution:")
    for difficulty, count in analytics['difficulty_analysis']['distribution'].items():
        percentage = (count / len(problems)) * 100
        print(f"   {difficulty.title()}: {count:,} ({percentage:.1f}%)")
    
    print(f"\n🏷️  Top Google-Relevant Tags:")
    google_tags = analytics['tag_analysis']['google_relevant_tags']
    for tag, count in list(google_tags.items())[:10]:
        print(f"   {tag}: {count:,}")
    
    print(f"\n⭐ Top Google Problems (by relevance score):")
    for i, problem in enumerate(google_subset[:5], 1):
        title = problem['title']
        score = problem['google_relevance_score']
        rating = problem['difficulty']['rating'] or 'Unrated'
        print(f"   {i}. {title} (Score: {score}, Rating: {rating})")
    
    print(f"\n📁 Files Created:")
    print(f"   • Standardized problems: data/processed/problems_unified.json")
    print(f"   • Google-relevant problems: data/exports/google_relevant_problems.json")
    print(f"   • Analytics report: data/enriched/codeforces_analytics.json")
    print(f"   • Top 100 Google problems: data/exports/top_100_google_problems.json")
    print(f"   • Problems by difficulty: data/exports/[easy|medium|hard]_problems.json")
    
    print(f"\n✅ Ready for Phase 2: Additional Data Sources!")
    print("="*60)

def main():
    """Main processing function"""
    print("Codeforces Data Processing Pipeline")
    print("="*50)
    
    # Load raw data
    codeforces_data = load_codeforces_data()
    if not codeforces_data:
        return
    
    # Convert to standardized format
    standardized_problems = create_standardized_problems(codeforces_data)
    
    # Create Google-relevant subset
    google_subset = create_google_relevant_subset(standardized_problems)
    
    # Create analytics report
    analytics = create_analytics_report(standardized_problems)
    
    # Save all processed data
    file_paths = save_processed_data(standardized_problems, google_subset, analytics)
    
    # Print summary
    print_summary(standardized_problems, google_subset, analytics)

if __name__ == "__main__":
    main()

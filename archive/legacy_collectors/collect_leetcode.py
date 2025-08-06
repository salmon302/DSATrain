"""
Phase 1.2: Kaggle LeetCode Dataset Collection
Implementation of automated LeetCode dataset processing

This script searches for and processes LeetCode datasets that are available
as CSV files (either manually downloaded from Kaggle or found in the project).
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

def check_for_existing_datasets():
    """Check for any existing LeetCode datasets in the project"""
    print("🔍 Checking for existing LeetCode datasets...")
    
    leetcode_dir = Path("data/raw/kaggle_leetcode")
    leetcode_dir.mkdir(parents=True, exist_ok=True)
    
    # Look for common LeetCode dataset files
    common_files = [
        "problems.csv", "leetcode_problems.csv", "problems.json",
        "solutions.csv", "leetcode_solutions.csv", "solutions.json",
        "problem_list.csv", "leetcode_data.csv"
    ]
    
    found_files = []
    for file_name in common_files:
        file_path = leetcode_dir / file_name
        if file_path.exists():
            found_files.append(file_path)
    
    if found_files:
        print(f"✅ Found {len(found_files)} existing LeetCode files:")
        for file_path in found_files:
            size = file_path.stat().st_size
            print(f"   📄 {file_path.name} ({size:,} bytes)")
    else:
        print("❌ No existing LeetCode datasets found")
    
    return found_files

def create_sample_leetcode_dataset():
    """Create a sample LeetCode dataset with common interview problems"""
    print("🏗️  Creating sample LeetCode dataset with common interview problems...")
    
    # Sample LeetCode problems that are commonly asked in interviews
    sample_problems = [
        {
            "id": "lc_1",
            "title": "Two Sum",
            "difficulty": "Easy",
            "description": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
            "tags": ["Array", "Hash Table"],
            "companies": ["Google", "Amazon", "Facebook", "Microsoft"],
            "acceptance_rate": 49.1,
            "leetcode_url": "https://leetcode.com/problems/two-sum/"
        },
        {
            "id": "lc_2",
            "title": "Add Two Numbers",
            "difficulty": "Medium", 
            "description": "You are given two non-empty linked lists representing two non-negative integers.",
            "tags": ["Linked List", "Math", "Recursion"],
            "companies": ["Google", "Amazon", "Microsoft"],
            "acceptance_rate": 38.5,
            "leetcode_url": "https://leetcode.com/problems/add-two-numbers/"
        },
        {
            "id": "lc_3",
            "title": "Longest Substring Without Repeating Characters",
            "difficulty": "Medium",
            "description": "Given a string s, find the length of the longest substring without repeating characters.",
            "tags": ["Hash Table", "String", "Sliding Window"],
            "companies": ["Google", "Amazon", "Facebook", "Apple"],
            "acceptance_rate": 33.8,
            "leetcode_url": "https://leetcode.com/problems/longest-substring-without-repeating-characters/"
        },
        {
            "id": "lc_4",
            "title": "Median of Two Sorted Arrays",
            "difficulty": "Hard",
            "description": "Given two sorted arrays nums1 and nums2 of size m and n respectively, return the median of the two sorted arrays.",
            "tags": ["Array", "Binary Search", "Divide and Conquer"],
            "companies": ["Google", "Amazon", "Microsoft", "Apple"],
            "acceptance_rate": 37.1,
            "leetcode_url": "https://leetcode.com/problems/median-of-two-sorted-arrays/"
        },
        {
            "id": "lc_20",
            "title": "Valid Parentheses",
            "difficulty": "Easy",
            "description": "Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.",
            "tags": ["String", "Stack"],
            "companies": ["Google", "Amazon", "Facebook", "Microsoft"],
            "acceptance_rate": 40.7,
            "leetcode_url": "https://leetcode.com/problems/valid-parentheses/"
        },
        {
            "id": "lc_21",
            "title": "Merge Two Sorted Lists",
            "difficulty": "Easy",
            "description": "You are given the heads of two sorted linked lists list1 and list2.",
            "tags": ["Linked List", "Recursion"],
            "companies": ["Google", "Amazon", "Microsoft", "Apple"],
            "acceptance_rate": 62.1,
            "leetcode_url": "https://leetcode.com/problems/merge-two-sorted-lists/"
        },
        {
            "id": "lc_53",
            "title": "Maximum Subarray",
            "difficulty": "Medium",
            "description": "Given an integer array nums, find the subarray with the largest sum, and return its sum.",
            "tags": ["Array", "Divide and Conquer", "Dynamic Programming"],
            "companies": ["Google", "Amazon", "Microsoft", "Bloomberg"],
            "acceptance_rate": 50.1,
            "leetcode_url": "https://leetcode.com/problems/maximum-subarray/"
        },
        {
            "id": "lc_121",
            "title": "Best Time to Buy and Sell Stock",
            "difficulty": "Easy",
            "description": "You are given an array prices where prices[i] is the price of a given stock on the ith day.",
            "tags": ["Array", "Dynamic Programming"],
            "companies": ["Google", "Amazon", "Facebook", "Microsoft"],
            "acceptance_rate": 54.2,
            "leetcode_url": "https://leetcode.com/problems/best-time-to-buy-and-sell-stock/"
        },
        {
            "id": "lc_200",
            "title": "Number of Islands",
            "difficulty": "Medium",
            "description": "Given an m x n 2D binary grid grid which represents a map of '1's (land) and '0's (water), return the number of islands.",
            "tags": ["Array", "Depth-First Search", "Breadth-First Search", "Union Find", "Matrix"],
            "companies": ["Google", "Amazon", "Facebook", "Microsoft"],
            "acceptance_rate": 57.7,
            "leetcode_url": "https://leetcode.com/problems/number-of-islands/"
        },
        {
            "id": "lc_238",
            "title": "Product of Array Except Self",
            "difficulty": "Medium",
            "description": "Given an integer array nums, return an array answer such that answer[i] is equal to the product of all the elements of nums except nums[i].",
            "tags": ["Array", "Prefix Sum"],
            "companies": ["Google", "Amazon", "Facebook", "Microsoft"],
            "acceptance_rate": 65.0,
            "leetcode_url": "https://leetcode.com/problems/product-of-array-except-self/"
        }
    ]
    
    return sample_problems

def convert_leetcode_to_standard_format(leetcode_problems):
    """Convert LeetCode problems to our standardized format"""
    print("🔄 Converting LeetCode problems to standardized format...")
    
    standardized_problems = []
    
    for problem in leetcode_problems:
        # Convert difficulty to standard format
        difficulty_level = problem.get('difficulty', 'Medium').lower()
        
        # Estimate rating based on difficulty and acceptance rate
        acceptance_rate = problem.get('acceptance_rate', 50.0)
        if difficulty_level == 'easy':
            rating = 1000 + int((100 - acceptance_rate) * 5)  # 1000-1500 range
        elif difficulty_level == 'medium':
            rating = 1500 + int((100 - acceptance_rate) * 10)  # 1500-2500 range
        else:  # hard
            rating = 2500 + int((100 - acceptance_rate) * 15)  # 2500-4000 range
        
        # Normalize tags
        tags = [tag.lower().replace(' ', '_').replace('-', '_') for tag in problem.get('tags', [])]
        
        # Extract Google company tags
        companies = problem.get('companies', [])
        google_companies = [c.lower() for c in companies if 'google' in c.lower() or 'alphabet' in c.lower()]
        
        std_problem = {
            "id": problem.get('id', f"lc_{problem.get('title', 'unknown').replace(' ', '_').lower()}"),
            "source": "leetcode",
            "title": problem.get('title', ''),
            "description": problem.get('description', ''),
            "difficulty": {
                "level": difficulty_level,
                "rating": rating,
                "source_scale": "leetcode_estimated"
            },
            "tags": tags,
            "company_tags": google_companies + [c.lower() for c in companies],
            "constraints": {
                "acceptance_rate": f"{acceptance_rate}%"
            },
            "test_cases": [],  # Would need separate collection
            "editorial": None,  # Would need separate collection
            "metadata": {
                "created_date": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "source_url": problem.get('leetcode_url'),
                "acquisition_method": "static_dataset",
                "acceptance_rate": acceptance_rate,
                "companies": companies,
                "is_google_tagged": any('google' in c.lower() for c in companies)
            }
        }
        
        standardized_problems.append(std_problem)
    
    print(f"✅ Converted {len(standardized_problems)} LeetCode problems")
    return standardized_problems

def create_leetcode_analytics(problems):
    """Create analytics for LeetCode data"""
    print("📊 Creating LeetCode analytics...")
    
    total_problems = len(problems)
    google_problems = [p for p in problems if p['metadata'].get('is_google_tagged', False)]
    
    # Difficulty distribution
    difficulty_dist = {}
    for p in problems:
        diff = p['difficulty']['level']
        difficulty_dist[diff] = difficulty_dist.get(diff, 0) + 1
    
    # Company analysis
    all_companies = []
    for p in problems:
        all_companies.extend(p['metadata'].get('companies', []))
    
    from collections import Counter
    company_freq = Counter(all_companies)
    
    # Tag analysis
    all_tags = []
    for p in problems:
        all_tags.extend(p['tags'])
    tag_freq = Counter(all_tags)
    
    analytics = {
        "collection_info": {
            "total_problems": total_problems,
            "google_tagged_problems": len(google_problems),
            "collection_date": datetime.now().isoformat(),
            "source": "leetcode_sample_dataset"
        },
        "difficulty_analysis": {
            "distribution": difficulty_dist,
        },
        "company_analysis": {
            "total_companies": len(company_freq),
            "most_frequent_companies": dict(company_freq.most_common(10)),
            "google_presence": company_freq.get('Google', 0)
        },
        "tag_analysis": {
            "total_unique_tags": len(tag_freq),
            "most_common_tags": dict(tag_freq.most_common(15))
        }
    }
    
    return analytics

def save_leetcode_data(problems, analytics):
    """Save LeetCode data in various formats"""
    print("💾 Saving LeetCode data...")
    
    # Ensure directories exist
    processed_dir = Path("data/processed")
    enriched_dir = Path("data/enriched")
    exports_dir = Path("data/exports")
    
    for directory in [processed_dir, enriched_dir, exports_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    
    # Save standardized problems
    leetcode_problems_file = processed_dir / "leetcode_problems_unified.json"
    with open(leetcode_problems_file, 'w', encoding='utf-8') as f:
        json.dump(problems, f, indent=2, ensure_ascii=False)
    print(f"📄 Saved LeetCode problems: {leetcode_problems_file}")
    
    # Save Google-specific problems
    google_problems = [p for p in problems if p['metadata'].get('is_google_tagged', False)]
    if google_problems:
        google_leetcode_file = exports_dir / "google_leetcode_problems.json"
        with open(google_leetcode_file, 'w', encoding='utf-8') as f:
            json.dump(google_problems, f, indent=2, ensure_ascii=False)
        print(f"🎯 Saved Google LeetCode problems: {google_leetcode_file}")
    
    # Save analytics
    analytics_file = enriched_dir / "leetcode_analytics.json"
    with open(analytics_file, 'w', encoding='utf-8') as f:
        json.dump(analytics, f, indent=2, ensure_ascii=False)
    print(f"📊 Saved LeetCode analytics: {analytics_file}")
    
    return {
        "problems_file": str(leetcode_problems_file),
        "google_file": str(google_leetcode_file) if google_problems else None,
        "analytics_file": str(analytics_file)
    }

def print_leetcode_summary(problems, analytics):
    """Print LeetCode collection summary"""
    print("\n" + "="*60)
    print("📋 LEETCODE DATA COLLECTION SUMMARY")
    print("="*60)
    
    print(f"📊 Total Problems: {len(problems)}")
    print(f"🎯 Google-Tagged Problems: {analytics['collection_info']['google_tagged_problems']}")
    
    print(f"\n📋 Difficulty Distribution:")
    for difficulty, count in analytics['difficulty_analysis']['distribution'].items():
        percentage = (count / len(problems)) * 100
        print(f"   {difficulty.title()}: {count} ({percentage:.1f}%)")
    
    print(f"\n🏢 Top Companies:")
    for company, count in list(analytics['company_analysis']['most_frequent_companies'].items())[:5]:
        print(f"   {company}: {count}")
    
    print(f"\n🏷️  Top Tags:")
    for tag, count in list(analytics['tag_analysis']['most_common_tags'].items())[:8]:
        print(f"   {tag}: {count}")
    
    print(f"\n📁 Files Created:")
    print(f"   • LeetCode problems: data/processed/leetcode_problems_unified.json")
    if analytics['collection_info']['google_tagged_problems'] > 0:
        print(f"   • Google LeetCode problems: data/exports/google_leetcode_problems.json")
    print(f"   • LeetCode analytics: data/enriched/leetcode_analytics.json")
    
    print("="*60)

def main():
    """Main LeetCode collection function"""
    print("LeetCode Dataset Collection - Phase 1.2")
    print("="*50)
    
    # Check for existing datasets
    existing_files = check_for_existing_datasets()
    
    if existing_files:
        print("🎯 Processing existing datasets...")
        # TODO: Implement processing of existing CSV files
        print("⚠️  CSV processing not yet implemented. Using sample dataset instead.")
    
    # Create sample dataset for now
    print("🎯 Creating sample LeetCode dataset...")
    sample_problems = create_sample_leetcode_dataset()
    
    # Convert to standard format
    standardized_problems = convert_leetcode_to_standard_format(sample_problems)
    
    # Create analytics
    analytics = create_leetcode_analytics(standardized_problems)
    
    # Save data
    file_paths = save_leetcode_data(standardized_problems, analytics)
    
    # Print summary
    print_leetcode_summary(standardized_problems, analytics)
    
    print("\n✅ LeetCode data collection completed!")
    print("🔗 Ready to integrate with Codeforces data!")

if __name__ == "__main__":
    main()

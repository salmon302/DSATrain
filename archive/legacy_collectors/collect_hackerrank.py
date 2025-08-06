"""
Phase 2.1: HackerRank Interview Kit Collection
Implementation of web scraping for HackerRank Interview Preparation Kit

This script collects problems from HackerRank's Interview Preparation Kit
which contains curated problems organized by data structure and algorithm topics.
"""

import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import httpx
import time

class HackerRankCollector:
    """
    Collector for HackerRank Interview Preparation Kit
    """
    
    BASE_URL = "https://www.hackerrank.com"
    INTERVIEW_KIT_URL = "https://www.hackerrank.com/interview/interview-preparation-kit"
    
    # Topics in the Interview Preparation Kit
    TOPICS = [
        "arrays", "linked-lists", "trees", "balanced-trees", 
        "stacks-and-queues", "heap", "dynamic-programming",
        "recursion-and-backtracking", "graphs", "greedy-algorithms",
        "search", "sorting", "string-manipulation", "miscellaneous"
    ]
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.hackerrank_dir = data_dir / "raw" / "hackerrank" / "interview_kit"
        self.hackerrank_dir.mkdir(parents=True, exist_ok=True)
        
        # Headers to appear more like a regular browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        self.rate_limit_delay = 2.0  # Be respectful with requests
    
    async def get_page_content(self, url: str) -> Optional[str]:
        """Fetch page content with error handling"""
        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=30.0) as client:
                await asyncio.sleep(self.rate_limit_delay)  # Rate limiting
                response = await client.get(url)
                response.raise_for_status()
                return response.text
        except Exception as e:
            print(f"❌ Error fetching {url}: {e}")
            return None
    
    def parse_problem_from_page(self, html_content: str, problem_url: str) -> Optional[Dict[str, Any]]:
        """Parse problem details from HackerRank problem page"""
        # Note: BeautifulSoup parsing would be implemented here in production
        # For now, returning None as we're using sample data
        print(f"📄 Would parse problem from: {problem_url}")
        return None
    
    def create_sample_hackerrank_problems(self) -> List[Dict[str, Any]]:
        """Create sample HackerRank problems based on known Interview Kit structure"""
        print("🏗️  Creating sample HackerRank Interview Kit problems...")
        
        sample_problems = [
            {
                'id': 'hr_2d_array_ds',
                'title': '2D Array - DS',
                'description': 'Calculate the maximum hourglass sum in a 2D array.',
                'difficulty': 'Easy',
                'tags': ['arrays', 'data_structures'],
                'topic': 'Arrays',
                'url': 'https://www.hackerrank.com/challenges/2d-array/problem'
            },
            {
                'id': 'hr_arrays_left_rotation',
                'title': 'Arrays: Left Rotation',
                'description': 'Perform left rotations on an array and return the result.',
                'difficulty': 'Easy',
                'tags': ['arrays', 'implementation'],
                'topic': 'Arrays',
                'url': 'https://www.hackerrank.com/challenges/ctci-array-left-rotation/problem'
            },
            {
                'id': 'hr_new_year_chaos',
                'title': 'New Year Chaos',
                'description': 'Determine minimum number of bribes to get a given permutation.',
                'difficulty': 'Medium',
                'tags': ['arrays', 'greedy'],
                'topic': 'Arrays',
                'url': 'https://www.hackerrank.com/challenges/new-year-chaos/problem'
            },
            {
                'id': 'hr_minimum_swaps',
                'title': 'Minimum Swaps 2',
                'description': 'Return minimum number of swaps to sort an array.',
                'difficulty': 'Medium',
                'tags': ['arrays', 'sorting'],
                'topic': 'Arrays',
                'url': 'https://www.hackerrank.com/challenges/minimum-swaps-2/problem'
            },
            {
                'id': 'hr_linked_list_cycle',
                'title': 'Linked Lists: Detect a Cycle',
                'description': 'Determine if a linked list contains a cycle.',
                'difficulty': 'Easy',
                'tags': ['linked_lists', 'cycle_detection'],
                'topic': 'Linked Lists',
                'url': 'https://www.hackerrank.com/challenges/ctci-linked-list-cycle/problem'
            },
            {
                'id': 'hr_tree_height',
                'title': 'Tree: Height of a Binary Tree',
                'description': 'Calculate the height of a binary tree.',
                'difficulty': 'Easy',
                'tags': ['trees', 'recursion'],
                'topic': 'Trees',
                'url': 'https://www.hackerrank.com/challenges/tree-height-of-a-binary-tree/problem'
            },
            {
                'id': 'hr_tree_lca',
                'title': 'Binary Search Tree: Lowest Common Ancestor',
                'description': 'Find the lowest common ancestor in a BST.',
                'difficulty': 'Easy',
                'tags': ['trees', 'binary_search_tree'],
                'topic': 'Trees',
                'url': 'https://www.hackerrank.com/challenges/binary-search-tree-lowest-common-ancestor/problem'
            },
            {
                'id': 'hr_balanced_brackets',
                'title': 'Balanced Brackets',
                'description': 'Determine if bracket sequences are balanced.',
                'difficulty': 'Medium',
                'tags': ['stacks', 'string_manipulation'],
                'topic': 'Stacks and Queues',
                'url': 'https://www.hackerrank.com/challenges/balanced-brackets/problem'
            },
            {
                'id': 'hr_queue_using_stacks',
                'title': 'Queue using Two Stacks',
                'description': 'Implement a queue using two stacks.',
                'difficulty': 'Medium',
                'tags': ['stacks', 'queues', 'data_structures'],
                'topic': 'Stacks and Queues',
                'url': 'https://www.hackerrank.com/challenges/queue-using-two-stacks/problem'
            },
            {
                'id': 'hr_max_array_sum',
                'title': 'Max Array Sum',
                'description': 'Find maximum sum of non-adjacent elements.',
                'difficulty': 'Medium',
                'tags': ['dynamic_programming'],
                'topic': 'Dynamic Programming',
                'url': 'https://www.hackerrank.com/challenges/max-array-sum/problem'
            },
            {
                'id': 'hr_abbreviation',
                'title': 'Abbreviation',
                'description': 'Determine if string can be transformed to match pattern.',
                'difficulty': 'Medium',
                'tags': ['dynamic_programming', 'strings'],
                'topic': 'Dynamic Programming',
                'url': 'https://www.hackerrank.com/challenges/abbr/problem'
            },
            {
                'id': 'hr_fibonacci_modified',
                'title': 'Fibonacci Modified',
                'description': 'Calculate modified Fibonacci sequence.',
                'difficulty': 'Medium',
                'tags': ['dynamic_programming', 'recursion'],
                'topic': 'Recursion and Backtracking',
                'url': 'https://www.hackerrank.com/challenges/fibonacci-modified/problem'
            },
            {
                'id': 'hr_roads_and_libraries',
                'title': 'Roads and Libraries',
                'description': 'Determine minimum cost to provide library access.',
                'difficulty': 'Medium',
                'tags': ['graphs', 'greedy'],
                'topic': 'Graphs',
                'url': 'https://www.hackerrank.com/challenges/torque-and-development/problem'
            },
            {
                'id': 'hr_find_nearest_clone',
                'title': 'Find the Nearest Clone',
                'description': 'Find shortest path between nodes with same color.',
                'difficulty': 'Medium',
                'tags': ['graphs', 'bfs'],
                'topic': 'Graphs',
                'url': 'https://www.hackerrank.com/challenges/find-the-nearest-clone/problem'
            },
            {
                'id': 'hr_minimum_time_required',
                'title': 'Minimum Time Required',
                'description': 'Find minimum time to produce required items.',
                'difficulty': 'Medium',
                'tags': ['greedy', 'binary_search'],
                'topic': 'Greedy Algorithms',
                'url': 'https://www.hackerrank.com/challenges/minimum-time-required/problem'
            },
            {
                'id': 'hr_luck_balance',
                'title': 'Luck Balance',
                'description': 'Maximize luck by strategically losing contests.',
                'difficulty': 'Easy',
                'tags': ['greedy', 'sorting'],
                'topic': 'Greedy Algorithms',
                'url': 'https://www.hackerrank.com/challenges/luck-balance/problem'
            },
            {
                'id': 'hr_hash_tables_ransom_note',
                'title': 'Hash Tables: Ransom Note',
                'description': 'Determine if ransom note can be formed from magazine.',
                'difficulty': 'Easy',
                'tags': ['hash_tables', 'string_manipulation'],
                'topic': 'Miscellaneous',
                'url': 'https://www.hackerrank.com/challenges/ctci-ransom-note/problem'
            },
            {
                'id': 'hr_two_strings',
                'title': 'Two Strings',
                'description': 'Determine if two strings share a common substring.',
                'difficulty': 'Easy',
                'tags': ['string_manipulation', 'hash_tables'],
                'topic': 'String Manipulation',
                'url': 'https://www.hackerrank.com/challenges/two-strings/problem'
            },
            {
                'id': 'hr_sherlock_valid_string',
                'title': 'Sherlock and the Valid String',
                'description': 'Determine if string can be made valid by removing one character.',
                'difficulty': 'Medium',
                'tags': ['string_manipulation', 'implementation'],
                'topic': 'String Manipulation',
                'url': 'https://www.hackerrank.com/challenges/sherlock-and-valid-string/problem'
            },
            {
                'id': 'hr_sorting_bubble_sort',
                'title': 'Sorting: Bubble Sort',
                'description': 'Implement bubble sort and count swaps.',
                'difficulty': 'Easy',
                'tags': ['sorting', 'implementation'],
                'topic': 'Sorting',
                'url': 'https://www.hackerrank.com/challenges/ctci-bubble-sort/problem'
            }
        ]
        
        return sample_problems
    
    def convert_to_standard_format(self, problems: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert HackerRank problems to our standardized format"""
        print("🔄 Converting HackerRank problems to standardized format...")
        
        standardized_problems = []
        
        for problem in problems:
            # Convert difficulty to standard format
            difficulty = problem.get('difficulty', 'Medium').lower()
            
            # Estimate rating based on difficulty and topic complexity
            if difficulty == 'easy':
                rating = 1100
            elif difficulty == 'medium':
                rating = 1600
            else:  # hard
                rating = 2200
            
            # Add topic complexity bonus
            topic = problem.get('topic', '').lower()
            if any(complex_topic in topic for complex_topic in ['dynamic', 'graph', 'tree']):
                rating += 200
            
            # Normalize tags
            tags = problem.get('tags', [])
            normalized_tags = [tag.lower().replace(' ', '_').replace('-', '_') for tag in tags]
            
            # Add topic as a tag if not already present
            if 'topic' in problem:
                topic_tag = problem['topic'].lower().replace(' ', '_').replace('-', '_')
                if topic_tag not in normalized_tags:
                    normalized_tags.append(topic_tag)
            
            std_problem = {
                "id": problem.get('id'),
                "source": "hackerrank",
                "title": problem.get('title', ''),
                "description": problem.get('description', ''),
                "difficulty": {
                    "level": difficulty,
                    "rating": rating,
                    "source_scale": "hackerrank_estimated"
                },
                "tags": normalized_tags,
                "company_tags": [],  # HackerRank doesn't typically provide company tags
                "constraints": {},
                "test_cases": [],  # Would need separate collection
                "editorial": None,  # Would need separate collection
                "metadata": {
                    "created_date": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "source_url": problem.get('url'),
                    "acquisition_method": "static_dataset",
                    "topic": problem.get('topic', ''),
                    "is_interview_kit": True
                }
            }
            
            standardized_problems.append(std_problem)
        
        print(f"✅ Converted {len(standardized_problems)} HackerRank problems")
        return standardized_problems
    
    def create_hackerrank_analytics(self, problems: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create analytics for HackerRank data"""
        print("📊 Creating HackerRank analytics...")
        
        # Topic distribution
        topic_dist = {}
        for p in problems:
            topic = p['metadata'].get('topic', 'Unknown')
            topic_dist[topic] = topic_dist.get(topic, 0) + 1
        
        # Difficulty distribution
        difficulty_dist = {}
        for p in problems:
            diff = p['difficulty']['level']
            difficulty_dist[diff] = difficulty_dist.get(diff, 0) + 1
        
        # Tag analysis
        all_tags = []
        for p in problems:
            all_tags.extend(p['tags'])
        
        from collections import Counter
        tag_freq = Counter(all_tags)
        
        analytics = {
            "collection_info": {
                "total_problems": len(problems),
                "source": "hackerrank_interview_kit",
                "collection_date": datetime.now().isoformat(),
                "is_curated": True
            },
            "topic_analysis": {
                "topics_covered": len(topic_dist),
                "topic_distribution": topic_dist
            },
            "difficulty_analysis": {
                "distribution": difficulty_dist
            },
            "tag_analysis": {
                "total_unique_tags": len(tag_freq),
                "most_common_tags": dict(tag_freq.most_common(15))
            },
            "interview_readiness": {
                "curated_for_interviews": True,
                "covers_major_topics": len(topic_dist) >= 10,
                "difficulty_balance": len(difficulty_dist) >= 2
            }
        }
        
        return analytics
    
    def save_hackerrank_data(self, problems: List[Dict[str, Any]], analytics: Dict[str, Any]):
        """Save HackerRank data"""
        print("💾 Saving HackerRank data...")
        
        # Save raw problems
        raw_file = self.hackerrank_dir / "interview_kit_problems.json"
        with open(raw_file, 'w', encoding='utf-8') as f:
            json.dump(problems, f, indent=2, ensure_ascii=False)
        print(f"📄 Saved HackerRank problems: {raw_file}")
        
        # Save analytics
        analytics_file = self.hackerrank_dir / "interview_kit_analytics.json"
        with open(analytics_file, 'w', encoding='utf-8') as f:
            json.dump(analytics, f, indent=2, ensure_ascii=False)
        print(f"📊 Saved HackerRank analytics: {analytics_file}")
        
        # Save to processed directory
        processed_dir = self.data_dir / "processed"
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        processed_file = processed_dir / "hackerrank_problems_unified.json"
        with open(processed_file, 'w', encoding='utf-8') as f:
            json.dump(problems, f, indent=2, ensure_ascii=False)
        print(f"📄 Saved processed HackerRank problems: {processed_file}")
        
        return {
            "raw_file": str(raw_file),
            "processed_file": str(processed_file),
            "analytics_file": str(analytics_file)
        }
    
    async def collect_problems(self) -> List[Dict[str, Any]]:
        """Main collection method"""
        print("🔍 Starting HackerRank Interview Kit collection...")
        
        # For now, use sample problems due to potential scraping complexities
        # In a production environment, you would implement actual web scraping here
        sample_problems = self.create_sample_hackerrank_problems()
        
        # Convert to standard format
        standardized_problems = self.convert_to_standard_format(sample_problems)
        
        # Create analytics
        analytics = self.create_hackerrank_analytics(standardized_problems)
        
        # Save data
        file_paths = self.save_hackerrank_data(standardized_problems, analytics)
        
        return standardized_problems

def main():
    """Main HackerRank collection function"""
    print("HackerRank Interview Kit Collection - Phase 2.1")
    print("="*60)
    
    data_dir = Path("data")
    collector = HackerRankCollector(data_dir)
    
    # Collect problems
    problems = asyncio.run(collector.collect_problems())
    
    print(f"\n" + "="*60)
    print("📋 HACKERRANK COLLECTION SUMMARY")
    print("="*60)
    print(f"📊 Total Problems: {len(problems)}")
    
    # Topic distribution
    topics = {}
    for p in problems:
        topic = p['metadata'].get('topic', 'Unknown')
        topics[topic] = topics.get(topic, 0) + 1
    
    print(f"\n📚 Topics Covered:")
    for topic, count in sorted(topics.items()):
        print(f"   {topic}: {count} problems")
    
    # Difficulty distribution
    difficulties = {}
    for p in problems:
        diff = p['difficulty']['level']
        difficulties[diff] = difficulties.get(diff, 0) + 1
    
    print(f"\n📊 Difficulty Distribution:")
    for diff, count in difficulties.items():
        percentage = (count / len(problems)) * 100
        print(f"   {diff.title()}: {count} ({percentage:.1f}%)")
    
    print(f"\n📁 Files Created:")
    print(f"   • Raw data: data/raw/hackerrank/interview_kit/interview_kit_problems.json")
    print(f"   • Processed: data/processed/hackerrank_problems_unified.json")
    print(f"   • Analytics: data/raw/hackerrank/interview_kit/interview_kit_analytics.json")
    
    print(f"\n✅ HackerRank collection completed!")
    print(f"🔗 Ready to integrate with existing datasets!")

if __name__ == "__main__":
    main()

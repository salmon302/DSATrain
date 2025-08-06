"""
Phase 2.3: CodeChef Problem Collection
Implementation of CodeChef problem collection with sample competitive programming problems

CodeChef is known for its monthly contests and educational content,
making it valuable for both competitive programming and interview preparation.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

class CodeChefCollector:
    """
    Collector for CodeChef competitive programming problems
    """
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.codechef_dir = data_dir / "raw" / "codechef"
        self.codechef_dir.mkdir(parents=True, exist_ok=True)
    
    def create_sample_codechef_problems(self) -> List[Dict[str, Any]]:
        """Create sample CodeChef problems representing various contests and difficulty levels"""
        print("🏗️  Creating sample CodeChef problems...")
        
        sample_problems = [
            # Long Challenge problems
            {
                'id': 'cc_chef_and_recipe',
                'title': 'Chef and Recipe',
                'description': 'Chef wants to cook a recipe by selecting ingredients optimally.',
                'difficulty': 'Easy',
                'rating': 1200,
                'tags': ['implementation', 'greedy'],
                'contest': 'Long Challenge',
                'contest_type': 'Long Challenge'
            },
            {
                'id': 'cc_optimal_partition',
                'title': 'Optimal Partition',
                'description': 'Partition array to maximize sum of minimum elements.',
                'difficulty': 'Medium',
                'rating': 1600,
                'tags': ['dynamic_programming', 'optimization'],
                'contest': 'Long Challenge',
                'contest_type': 'Long Challenge'
            },
            {
                'id': 'cc_tree_operations',
                'title': 'Tree Operations',
                'description': 'Perform operations on tree to achieve target configuration.',
                'difficulty': 'Hard',
                'rating': 2300,
                'tags': ['trees', 'graph_theory', 'constructive'],
                'contest': 'Long Challenge',
                'contest_type': 'Long Challenge'
            },
            
            # Cook-Off problems (shorter contest)
            {
                'id': 'cc_palindrome_pairs',
                'title': 'Palindrome Pairs',
                'description': 'Count pairs of strings that form palindromes when concatenated.',
                'difficulty': 'Medium',
                'rating': 1700,
                'tags': ['strings', 'palindromes', 'hashing'],
                'contest': 'Cook-Off',
                'contest_type': 'Cook-Off'
            },
            {
                'id': 'cc_maximum_xor',
                'title': 'Maximum XOR Subset',
                'description': 'Find subset with maximum XOR value.',
                'difficulty': 'Hard',
                'rating': 2100,
                'tags': ['bit_manipulation', 'linear_algebra', 'basis'],
                'contest': 'Cook-Off',
                'contest_type': 'Cook-Off'
            },
            
            # Lunchtime problems
            {
                'id': 'cc_shortest_route',
                'title': 'Shortest Route',
                'description': 'Find shortest path with special movement rules.',
                'difficulty': 'Medium',
                'rating': 1500,
                'tags': ['graphs', 'shortest_path', 'dijkstra'],
                'contest': 'Lunchtime',
                'contest_type': 'Lunchtime'
            },
            {
                'id': 'cc_matrix_queries',
                'title': 'Matrix Queries',
                'description': 'Answer range queries on 2D matrix efficiently.',
                'difficulty': 'Hard',
                'rating': 2000,
                'tags': ['data_structures', '2d_segment_tree', 'queries'],
                'contest': 'Lunchtime',
                'contest_type': 'Lunchtime'
            },
            
            # Practice problems (from practice section)
            {
                'id': 'cc_beginner_problem1',
                'title': 'Add Two Numbers',
                'description': 'Read two numbers and output their sum.',
                'difficulty': 'Easy',
                'rating': 800,
                'tags': ['implementation', 'basic'],
                'contest': 'Practice',
                'contest_type': 'Practice'
            },
            {
                'id': 'cc_factorial',
                'title': 'Factorial',
                'description': 'Calculate factorial of a number.',
                'difficulty': 'Easy',
                'rating': 900,
                'tags': ['implementation', 'math'],
                'contest': 'Practice',
                'contest_type': 'Practice'
            },
            {
                'id': 'cc_prime_generator',
                'title': 'Prime Generator',
                'description': 'Generate all prime numbers in given range.',
                'difficulty': 'Easy',
                'rating': 1000,
                'tags': ['math', 'sieve', 'number_theory'],
                'contest': 'Practice',
                'contest_type': 'Practice'
            },
            {
                'id': 'cc_coin_change',
                'title': 'Coin Change',
                'description': 'Find minimum coins needed to make target amount.',
                'difficulty': 'Medium',
                'rating': 1400,
                'tags': ['dynamic_programming', 'classic'],
                'contest': 'Practice',
                'contest_type': 'Practice'
            },
            {
                'id': 'cc_knapsack',
                'title': 'Knapsack Problem',
                'description': 'Classical 0/1 knapsack optimization problem.',
                'difficulty': 'Medium',
                'rating': 1500,
                'tags': ['dynamic_programming', 'classic', 'optimization'],
                'contest': 'Practice',
                'contest_type': 'Practice'
            },
            
            # Educational/Tutorial problems
            {
                'id': 'cc_binary_search_tutorial',
                'title': 'Binary Search Tutorial',
                'description': 'Learn binary search through practical examples.',
                'difficulty': 'Easy',
                'rating': 1100,
                'tags': ['binary_search', 'tutorial'],
                'contest': 'Educational',
                'contest_type': 'Educational'
            },
            {
                'id': 'cc_dfs_tutorial',
                'title': 'DFS Tutorial',
                'description': 'Understand depth-first search with examples.',
                'difficulty': 'Medium',
                'rating': 1300,
                'tags': ['graphs', 'dfs', 'tutorial'],
                'contest': 'Educational',
                'contest_type': 'Educational'
            },
            {
                'id': 'cc_dp_tutorial',
                'title': 'DP Tutorial',
                'description': 'Master dynamic programming concepts.',
                'difficulty': 'Medium',
                'rating': 1600,
                'tags': ['dynamic_programming', 'tutorial'],
                'contest': 'Educational',
                'contest_type': 'Educational'
            },
            
            # Special contests (like ICPC practice)
            {
                'id': 'cc_icpc_team_selection',
                'title': 'Team Selection',
                'description': 'Optimize team selection for maximum performance.',
                'difficulty': 'Hard',
                'rating': 2200,
                'tags': ['optimization', 'greedy', 'sorting'],
                'contest': 'ICPC Practice',
                'contest_type': 'ICPC Practice'
            },
            {
                'id': 'cc_network_flow',
                'title': 'Maximum Flow',
                'description': 'Find maximum flow in network.',
                'difficulty': 'Hard',
                'rating': 2400,
                'tags': ['graphs', 'max_flow', 'network_flow'],
                'contest': 'ICPC Practice',
                'contest_type': 'ICPC Practice'
            },
            
            # Math-heavy problems
            {
                'id': 'cc_gcd_queries',
                'title': 'GCD Queries',
                'description': 'Answer GCD queries on array efficiently.',
                'difficulty': 'Medium',
                'rating': 1800,
                'tags': ['math', 'gcd', 'segment_tree'],
                'contest': 'Math Contest',
                'contest_type': 'Mathematical'
            },
            {
                'id': 'cc_modular_exponentiation',
                'title': 'Modular Exponentiation',
                'description': 'Calculate large powers modulo prime efficiently.',
                'difficulty': 'Medium',
                'rating': 1400,
                'tags': ['math', 'modular_arithmetic', 'fast_exponentiation'],
                'contest': 'Math Contest',
                'contest_type': 'Mathematical'
            },
            {
                'id': 'cc_combinatorics',
                'title': 'Combinatorial Game',
                'description': 'Solve game using combinatorial principles.',
                'difficulty': 'Hard',
                'rating': 2100,
                'tags': ['math', 'combinatorics', 'game_theory'],
                'contest': 'Math Contest',
                'contest_type': 'Mathematical'
            }
        ]
        
        return sample_problems
    
    def convert_to_standard_format(self, problems: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert CodeChef problems to our standardized format"""
        print("🔄 Converting CodeChef problems to standardized format...")
        
        standardized_problems = []
        
        for problem in problems:
            # Convert difficulty to standard format
            difficulty = problem.get('difficulty', 'Medium').lower()
            rating = problem.get('rating', 1500)
            
            # Normalize tags
            tags = problem.get('tags', [])
            normalized_tags = [tag.lower().replace(' ', '_').replace('-', '_') for tag in tags]
            
            # Add contest type as tag
            contest_type = problem.get('contest_type', '').lower().replace(' ', '_').replace('-', '_')
            if contest_type and contest_type not in normalized_tags:
                normalized_tags.append(contest_type)
            
            # Create problem ID with codechef prefix
            problem_id = problem.get('id', '').replace('cc_', 'codechef_')
            
            std_problem = {
                "id": problem_id,
                "source": "codechef",
                "title": problem.get('title', ''),
                "description": problem.get('description', ''),
                "difficulty": {
                    "level": difficulty,
                    "rating": rating,
                    "source_scale": "codechef_estimated"
                },
                "tags": normalized_tags,
                "company_tags": [],  # CodeChef doesn't provide company tags
                "constraints": {},
                "test_cases": [],
                "editorial": None,
                "metadata": {
                    "created_date": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "source_url": f"https://www.codechef.com/problems/{problem.get('id', '').replace('cc_', '')}",
                    "acquisition_method": "static_dataset",
                    "contest": problem.get('contest', ''),
                    "contest_type": problem.get('contest_type', ''),
                    "is_competitive_programming": True,
                    "platform_specialty": "monthly_contests_and_practice"
                }
            }
            
            standardized_problems.append(std_problem)
        
        print(f"✅ Converted {len(standardized_problems)} CodeChef problems")
        return standardized_problems
    
    def create_codechef_analytics(self, problems: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create analytics for CodeChef data"""
        print("📊 Creating CodeChef analytics...")
        
        # Contest type distribution
        contest_types = {}
        for p in problems:
            contest_type = p['metadata'].get('contest_type', 'Unknown')
            contest_types[contest_type] = contest_types.get(contest_type, 0) + 1
        
        # Difficulty distribution
        difficulty_dist = {}
        for p in problems:
            diff = p['difficulty']['level']
            difficulty_dist[diff] = difficulty_dist.get(diff, 0) + 1
        
        # Rating distribution
        ratings = [p['difficulty']['rating'] for p in problems]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        
        # Tag analysis
        all_tags = []
        for p in problems:
            all_tags.extend(p['tags'])
        
        from collections import Counter
        tag_freq = Counter(all_tags)
        
        # Educational content analysis
        educational_problems = [p for p in problems if 'tutorial' in p['tags'] or p['metadata'].get('contest_type') == 'Educational']
        
        analytics = {
            "collection_info": {
                "total_problems": len(problems),
                "source": "codechef_competitive_programming",
                "collection_date": datetime.now().isoformat(),
                "is_competitive_programming": True
            },
            "contest_analysis": {
                "contest_types_covered": len(contest_types),
                "contest_type_distribution": contest_types,
                "has_long_challenges": contest_types.get('Long Challenge', 0) > 0,
                "has_short_contests": contest_types.get('Cook-Off', 0) > 0 or contest_types.get('Lunchtime', 0) > 0
            },
            "difficulty_analysis": {
                "distribution": difficulty_dist,
                "average_rating": round(avg_rating, 1),
                "rating_range": {
                    "min": min(ratings) if ratings else None,
                    "max": max(ratings) if ratings else None
                }
            },
            "tag_analysis": {
                "total_unique_tags": len(tag_freq),
                "most_common_tags": dict(tag_freq.most_common(15)),
                "algorithmic_topics": {
                    tag: count for tag, count in tag_freq.items()
                    if any(keyword in tag for keyword in ['dp', 'graph', 'tree', 'math', 'greedy', 'binary'])
                }
            },
            "educational_value": {
                "educational_problems": len(educational_problems),
                "tutorial_content": len([p for p in problems if 'tutorial' in p['tags']]),
                "practice_problems": contest_types.get('Practice', 0),
                "beginner_friendly": len([p for p in problems if p['difficulty']['rating'] <= 1000])
            },
            "competitive_programming_coverage": {
                "covers_icpc_style": contest_types.get('ICPC Practice', 0) > 0,
                "math_problems": len([t for t in tag_freq if 'math' in t]),
                "advanced_algorithms": len([p for p in problems if p['difficulty']['rating'] >= 2000]),
                "interview_relevant": len([p for p in problems if any(tag in p['tags'] for tag in ['dynamic_programming', 'graphs', 'trees', 'binary_search'])])
            }
        }
        
        return analytics
    
    def save_codechef_data(self, problems: List[Dict[str, Any]], analytics: Dict[str, Any]):
        """Save CodeChef data"""
        print("💾 Saving CodeChef data...")
        
        # Save raw problems
        raw_file = self.codechef_dir / "codechef_problems.json"
        with open(raw_file, 'w', encoding='utf-8') as f:
            json.dump(problems, f, indent=2, ensure_ascii=False)
        print(f"📄 Saved CodeChef problems: {raw_file}")
        
        # Save analytics
        analytics_file = self.codechef_dir / "codechef_analytics.json"
        with open(analytics_file, 'w', encoding='utf-8') as f:
            json.dump(analytics, f, indent=2, ensure_ascii=False)
        print(f"📊 Saved CodeChef analytics: {analytics_file}")
        
        # Save to processed directory
        processed_dir = self.data_dir / "processed"
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        processed_file = processed_dir / "codechef_problems_unified.json"
        with open(processed_file, 'w', encoding='utf-8') as f:
            json.dump(problems, f, indent=2, ensure_ascii=False)
        print(f"📄 Saved processed CodeChef problems: {processed_file}")
        
        return {
            "raw_file": str(raw_file),
            "processed_file": str(processed_file),
            "analytics_file": str(analytics_file)
        }
    
    def collect_problems(self) -> List[Dict[str, Any]]:
        """Main collection method"""
        print("🔍 Starting CodeChef problem collection...")
        
        # Create sample problems
        sample_problems = self.create_sample_codechef_problems()
        
        # Convert to standard format
        standardized_problems = self.convert_to_standard_format(sample_problems)
        
        # Create analytics
        analytics = self.create_codechef_analytics(standardized_problems)
        
        # Save data
        file_paths = self.save_codechef_data(standardized_problems, analytics)
        
        return standardized_problems

def main():
    """Main CodeChef collection function"""
    print("CodeChef Problem Collection - Phase 2.3")
    print("="*60)
    
    data_dir = Path("data")
    collector = CodeChefCollector(data_dir)
    
    # Collect problems
    problems = collector.collect_problems()
    
    print(f"\n" + "="*60)
    print("📋 CODECHEF COLLECTION SUMMARY")
    print("="*60)
    print(f"📊 Total Problems: {len(problems)}")
    
    # Contest type distribution
    contest_types = {}
    for p in problems:
        contest_type = p['metadata'].get('contest_type', 'Unknown')
        contest_types[contest_type] = contest_types.get(contest_type, 0) + 1
    
    print(f"\n🏆 Contest Types:")
    for contest_type, count in sorted(contest_types.items()):
        print(f"   {contest_type}: {count} problems")
    
    # Difficulty distribution
    difficulties = {}
    for p in problems:
        diff = p['difficulty']['level']
        difficulties[diff] = difficulties.get(diff, 0) + 1
    
    print(f"\n📊 Difficulty Distribution:")
    for diff, count in difficulties.items():
        percentage = (count / len(problems)) * 100
        print(f"   {diff.title()}: {count} ({percentage:.1f}%)")
    
    # Rating range
    ratings = [p['difficulty']['rating'] for p in problems]
    print(f"\n⭐ Rating Range: {min(ratings)} - {max(ratings)} (avg: {sum(ratings)/len(ratings):.0f})")
    
    # Educational content
    educational = len([p for p in problems if 'tutorial' in p['tags'] or p['metadata'].get('contest_type') == 'Educational'])
    print(f"\n📚 Educational Problems: {educational}")
    
    print(f"\n📁 Files Created:")
    print(f"   • Raw data: data/raw/codechef/codechef_problems.json")
    print(f"   • Processed: data/processed/codechef_problems_unified.json")
    print(f"   • Analytics: data/raw/codechef/codechef_analytics.json")
    
    print(f"\n✅ CodeChef collection completed!")
    print(f"🔗 Ready to integrate with existing datasets!")

if __name__ == "__main__":
    main()

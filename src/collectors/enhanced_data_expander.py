"""
Enhanced Data Expander for DSATrain
Adds more diverse, high-quality problems to expand the dataset
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path
import uuid

# Database imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.models.database import DatabaseConfig, Problem, Solution
from src.analysis.code_quality import PythonCodeAnalyzer

# Setup logging with UTF-8 encoding for Windows
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/data_expansion.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EnhancedDataExpander:
    """Enhanced data expander with diverse problem set"""
    
    def __init__(self):
        self.db_config = DatabaseConfig()
        self.session_factory = self.db_config.SessionLocal
        self.code_analyzer = PythonCodeAnalyzer()
        
    def get_expanded_problem_set(self) -> List[Dict[str, Any]]:
        """Get an expanded set of diverse, high-quality problems"""
        
        problems = [
            # Arrays & Two Pointers
            {
                "id": f"leetcode_{uuid.uuid4().hex[:8]}_3sum",
                "platform": "leetcode",
                "platform_id": "15",
                "title": "3Sum",
                "difficulty": "Medium",
                "description": "Given an integer array nums, return all the triplets [nums[i], nums[j], nums[k]] such that i != j, i != k, and j != k, and nums[i] + nums[j] + nums[k] == 0.",
                "algorithm_tags": ["two_pointers", "sorting", "array"],
                "data_structures": ["array"],
                "companies": ["Google", "Facebook", "Amazon", "Microsoft"],
                "acceptance_rate": 32.1,
                "google_interview_frequency": 95.0
            },
            {
                "id": f"leetcode_{uuid.uuid4().hex[:8]}_container_water",
                "platform": "leetcode", 
                "platform_id": "11",
                "title": "Container With Most Water",
                "difficulty": "Medium",
                "description": "You are given an integer array height of length n. There are n vertical lines drawn such that the two endpoints of the ith line are (i, 0) and (i, height[i]).",
                "algorithm_tags": ["two_pointers", "greedy"],
                "data_structures": ["array"],
                "companies": ["Google", "Apple", "Bloomberg"],
                "acceptance_rate": 54.3,
                "google_interview_frequency": 88.0
            },
            
            # Dynamic Programming
            {
                "id": f"leetcode_{uuid.uuid4().hex[:8]}_coin_change",
                "platform": "leetcode",
                "platform_id": "322",
                "title": "Coin Change",
                "difficulty": "Medium",
                "description": "You are given an integer array coins representing coins of different denominations and an integer amount representing a total amount of money.",
                "algorithm_tags": ["dynamic_programming", "bfs"],
                "data_structures": ["array"],
                "companies": ["Google", "Amazon", "Uber"],
                "acceptance_rate": 40.7,
                "google_interview_frequency": 92.0
            },
            {
                "id": f"leetcode_{uuid.uuid4().hex[:8]}_longest_increasing",
                "platform": "leetcode",
                "platform_id": "300",
                "title": "Longest Increasing Subsequence",
                "difficulty": "Medium",
                "description": "Given an integer array nums, return the length of the longest strictly increasing subsequence.",
                "algorithm_tags": ["dynamic_programming", "binary_search"],
                "data_structures": ["array"],
                "companies": ["Google", "Microsoft", "Facebook"],
                "acceptance_rate": 47.8,
                "google_interview_frequency": 85.0
            },
            
            # Trees & Graphs
            {
                "id": f"leetcode_{uuid.uuid4().hex[:8]}_binary_tree_max_path",
                "platform": "leetcode",
                "platform_id": "124",
                "title": "Binary Tree Maximum Path Sum",
                "difficulty": "Hard",
                "description": "A path in a binary tree is a sequence of nodes where each pair of adjacent nodes in the sequence has an edge connecting them.",
                "algorithm_tags": ["tree", "dfs", "recursion"],
                "data_structures": ["binary_tree"],
                "companies": ["Google", "Amazon", "Facebook"],
                "acceptance_rate": 38.2,
                "google_interview_frequency": 90.0
            },
            {
                "id": f"leetcode_{uuid.uuid4().hex[:8]}_course_schedule",
                "platform": "leetcode",
                "platform_id": "207",
                "title": "Course Schedule",
                "difficulty": "Medium",
                "description": "There are a total of numCourses courses you have to take, labeled from 0 to numCourses - 1.",
                "algorithm_tags": ["graph", "topological_sort", "dfs", "bfs"],
                "data_structures": ["graph"],
                "companies": ["Google", "Facebook", "Zenefits"],
                "acceptance_rate": 46.9,
                "google_interview_frequency": 87.0
            },
            
            # Strings & Sliding Window
            {
                "id": f"leetcode_{uuid.uuid4().hex[:8]}_min_window_substring",
                "platform": "leetcode",
                "platform_id": "76",
                "title": "Minimum Window Substring",
                "difficulty": "Hard",
                "description": "Given two strings s and t of lengths m and n respectively, return the minimum window substring of s such that every character in t (including duplicates) is included in the window.",
                "algorithm_tags": ["sliding_window", "hash_table", "string"],
                "data_structures": ["string", "hash_map"],
                "companies": ["Google", "Facebook", "Uber", "LinkedIn"],
                "acceptance_rate": 38.7,
                "google_interview_frequency": 94.0
            },
            {
                "id": f"leetcode_{uuid.uuid4().hex[:8]}_group_anagrams",
                "platform": "leetcode",
                "platform_id": "49",
                "title": "Group Anagrams",
                "difficulty": "Medium",
                "description": "Given an array of strings strs, group the anagrams together. You can return the answer in any order.",
                "algorithm_tags": ["hash_table", "string", "sorting"],
                "data_structures": ["string", "hash_map"],
                "companies": ["Google", "Amazon", "Facebook"],
                "acceptance_rate": 67.1,
                "google_interview_frequency": 83.0
            },
            
            # Binary Search
            {
                "id": f"leetcode_{uuid.uuid4().hex[:8]}_search_rotated_array",
                "platform": "leetcode",
                "platform_id": "33",
                "title": "Search in Rotated Sorted Array",
                "difficulty": "Medium",
                "description": "There is an integer array nums sorted in ascending order (with distinct values). Prior to being passed to your function, nums is possibly rotated at an unknown pivot index k.",
                "algorithm_tags": ["binary_search", "array"],
                "data_structures": ["array"],
                "companies": ["Google", "Facebook", "Microsoft"],
                "acceptance_rate": 38.9,
                "google_interview_frequency": 89.0
            },
            {
                "id": f"leetcode_{uuid.uuid4().hex[:8]}_find_peak_element",
                "platform": "leetcode",
                "platform_id": "162",
                "title": "Find Peak Element",
                "difficulty": "Medium",
                "description": "A peak element is an element that is strictly greater than its neighbors. Given a 0-indexed integer array nums, find a peak element, and return its index.",
                "algorithm_tags": ["binary_search", "array"],
                "data_structures": ["array"],
                "companies": ["Google", "Microsoft", "Facebook"],
                "acceptance_rate": 45.2,
                "google_interview_frequency": 82.0
            },
            
            # Backtracking
            {
                "id": f"leetcode_{uuid.uuid4().hex[:8]}_combination_sum",
                "platform": "leetcode",
                "platform_id": "39",
                "title": "Combination Sum",
                "difficulty": "Medium",
                "description": "Given an array of distinct integers candidates and a target integer target, return a list of all unique combinations of candidates where the chosen numbers sum to target.",
                "algorithm_tags": ["backtracking", "array"],
                "data_structures": ["array"],
                "companies": ["Google", "Airbnb", "Facebook"],
                "acceptance_rate": 68.9,
                "google_interview_frequency": 81.0
            },
            {
                "id": f"leetcode_{uuid.uuid4().hex[:8]}_word_search",
                "platform": "leetcode",
                "platform_id": "79",
                "title": "Word Search",
                "difficulty": "Medium",
                "description": "Given an m x n grid of characters board and a string word, return true if word exists in the grid.",
                "algorithm_tags": ["backtracking", "matrix", "dfs"],
                "data_structures": ["matrix"],
                "companies": ["Google", "Microsoft", "Facebook"],
                "acceptance_rate": 40.1,
                "google_interview_frequency": 86.0
            },
            
            # Heap & Priority Queue
            {
                "id": f"leetcode_{uuid.uuid4().hex[:8]}_top_k_frequent",
                "platform": "leetcode",
                "platform_id": "347",
                "title": "Top K Frequent Elements",
                "difficulty": "Medium",
                "description": "Given an integer array nums and an integer k, return the k most frequent elements. You may return the answer in any order.",
                "algorithm_tags": ["heap", "hash_table", "divide_and_conquer"],
                "data_structures": ["heap", "hash_map"],
                "companies": ["Google", "Amazon", "Facebook"],
                "acceptance_rate": 63.4,
                "google_interview_frequency": 88.0
            },
            {
                "id": f"leetcode_{uuid.uuid4().hex[:8]}_meeting_rooms_ii",
                "platform": "leetcode",
                "platform_id": "253",
                "title": "Meeting Rooms II",
                "difficulty": "Medium",
                "description": "Given an array of meeting time intervals intervals where intervals[i] = [starti, endi], return the minimum number of conference rooms required.",
                "algorithm_tags": ["heap", "sorting", "greedy"],
                "data_structures": ["heap"],
                "companies": ["Google", "Facebook", "Amazon"],
                "acceptance_rate": 49.2,
                "google_interview_frequency": 93.0
            },
            
            # Codeforces Problems
            {
                "id": f"codeforces_{uuid.uuid4().hex[:8]}_div2_a",
                "platform": "codeforces",
                "platform_id": "1500A",
                "title": "Going Home",
                "difficulty": "Medium",
                "description": "Find four distinct indices such that their values sum to a target value.",
                "algorithm_tags": ["hash_table", "implementation"],
                "data_structures": ["array", "hash_map"],
                "companies": [],
                "acceptance_rate": 35.0,
                "google_interview_frequency": 75.0
            },
            {
                "id": f"codeforces_{uuid.uuid4().hex[:8]}_dp_problem",
                "platform": "codeforces",
                "platform_id": "1300B",
                "title": "Assigning to Classes",
                "difficulty": "Medium",
                "description": "Assign students to classes to minimize the difference in skill levels.",
                "algorithm_tags": ["sorting", "greedy", "constructive"],
                "data_structures": ["array"],
                "companies": [],
                "acceptance_rate": 42.0,
                "google_interview_frequency": 70.0
            },
        ]
        
        # Calculate quality and relevance scores for each problem
        for problem in problems:
            problem['quality_score'] = self._calculate_quality_score(problem)
            problem['google_interview_relevance'] = self._calculate_google_relevance(problem)
            problem['collected_at'] = datetime.now()
            
        return problems
    
    def get_sample_solutions(self) -> List[Dict[str, Any]]:
        """Get sample solutions for the new problems"""
        solutions = [
            # Two Sum solution
            {
                "problem_identifier": "3sum",
                "code": '''def threeSum(nums):
    """
    Find all unique triplets that sum to zero.
    Time: O(n²), Space: O(1) excluding output
    """
    nums.sort()
    result = []
    
    for i in range(len(nums) - 2):
        # Skip duplicates for first element
        if i > 0 and nums[i] == nums[i-1]:
            continue
            
        left, right = i + 1, len(nums) - 1
        
        while left < right:
            current_sum = nums[i] + nums[left] + nums[right]
            
            if current_sum == 0:
                result.append([nums[i], nums[left], nums[right]])
                
                # Skip duplicates for second and third elements
                while left < right and nums[left] == nums[left + 1]:
                    left += 1
                while left < right and nums[right] == nums[right - 1]:
                    right -= 1
                    
                left += 1
                right -= 1
            elif current_sum < 0:
                left += 1
            else:
                right -= 1
                
    return result''',
                "approach_type": "two_pointers",
                "time_complexity": "O(n²)",
                "space_complexity": "O(1)",
                "explanation": "Sort array and use two pointers technique with duplicate handling"
            },
            
            # Container with most water
            {
                "problem_identifier": "container_water",
                "code": '''def maxArea(height):
    """
    Find maximum water container area using two pointers.
    Time: O(n), Space: O(1)
    """
    left, right = 0, len(height) - 1
    max_area = 0
    
    while left < right:
        # Calculate current area
        width = right - left
        current_height = min(height[left], height[right])
        current_area = width * current_height
        max_area = max(max_area, current_area)
        
        # Move the pointer with smaller height
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
            
    return max_area''',
                "approach_type": "two_pointers",
                "time_complexity": "O(n)",
                "space_complexity": "O(1)",
                "explanation": "Use two pointers to find maximum area by always moving the shorter line"
            },
            
            # Coin Change DP
            {
                "problem_identifier": "coin_change",
                "code": '''def coinChange(coins, amount):
    """
    Find minimum coins needed for amount using dynamic programming.
    Time: O(amount * coins), Space: O(amount)
    """
    if amount == 0:
        return 0
        
    # Initialize DP array with impossible value
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    
    # For each amount from 1 to target
    for i in range(1, amount + 1):
        # Try each coin
        for coin in coins:
            if coin <= i:
                dp[i] = min(dp[i], dp[i - coin] + 1)
    
    return dp[amount] if dp[amount] != float('inf') else -1''',
                "approach_type": "dynamic_programming",
                "time_complexity": "O(amount * coins)",
                "space_complexity": "O(amount)",
                "explanation": "Bottom-up DP building minimum coins needed for each amount"
            },
            
            # Binary Tree Maximum Path Sum
            {
                "problem_identifier": "binary_tree_max_path",
                "code": '''def maxPathSum(root):
    """
    Find maximum path sum in binary tree.
    Time: O(n), Space: O(h) where h is height
    """
    def max_gain(node):
        nonlocal max_sum
        if not node:
            return 0
        
        # Maximum gain from left and right subtrees
        left_gain = max(max_gain(node.left), 0)
        right_gain = max(max_gain(node.right), 0)
        
        # Price of new path through current node
        price_newpath = node.val + left_gain + right_gain
        max_sum = max(max_sum, price_newpath)
        
        # Return max gain if continuing path through node
        return node.val + max(left_gain, right_gain)
    
    max_sum = float('-inf')
    max_gain(root)
    return max_sum''',
                "approach_type": "dfs_recursion",
                "time_complexity": "O(n)",
                "space_complexity": "O(h)",
                "explanation": "DFS with global maximum tracking, considering paths through each node"
            },
            
            # Minimum Window Substring
            {
                "problem_identifier": "min_window_substring",
                "code": '''def minWindow(s, t):
    """
    Find minimum window substring using sliding window.
    Time: O(|s| + |t|), Space: O(|s| + |t|)
    """
    if not s or not t:
        return ""
    
    # Character frequency map for t
    dict_t = {}
    for char in t:
        dict_t[char] = dict_t.get(char, 0) + 1
    
    required = len(dict_t)
    formed = 0
    window_counts = {}
    
    # Two pointers
    l, r = 0, 0
    ans = float("inf"), None, None
    
    while r < len(s):
        # Add character from right to window
        character = s[r]
        window_counts[character] = window_counts.get(character, 0) + 1
        
        # Check if frequency matches required frequency
        if character in dict_t and window_counts[character] == dict_t[character]:
            formed += 1
        
        # Contract window from left
        while l <= r and formed == required:
            character = s[l]
            
            # Update result if this window is smaller
            if r - l + 1 < ans[0]:
                ans = (r - l + 1, l, r)
            
            # Remove character from left
            window_counts[character] -= 1
            if character in dict_t and window_counts[character] < dict_t[character]:
                formed -= 1
            
            l += 1    
        
        r += 1    
    
    return "" if ans[0] == float("inf") else s[ans[1] : ans[2] + 1]''',
                "approach_type": "sliding_window",
                "time_complexity": "O(|s| + |t|)",
                "space_complexity": "O(|s| + |t|)",
                "explanation": "Sliding window with frequency tracking to find minimum valid window"
            }
        ]
        
        return solutions
    
    def _calculate_quality_score(self, problem: Dict[str, Any]) -> float:
        """Calculate problem quality score"""
        score = 50.0  # Base score
        
        # Company backing (major tech companies)
        companies = problem.get('companies', [])
        tech_giants = ['google', 'facebook', 'amazon', 'microsoft', 'apple']
        company_score = sum(15 for company in companies if company.lower() in tech_giants)
        score += min(company_score, 40.0)
        
        # Algorithm diversity and relevance
        algorithm_tags = problem.get('algorithm_tags', [])
        high_value_algorithms = [
            'dynamic_programming', 'binary_search', 'two_pointers', 'sliding_window',
            'dfs', 'bfs', 'backtracking', 'heap', 'graph', 'tree'
        ]
        
        for tag in algorithm_tags:
            if tag in high_value_algorithms:
                score += 8.0
        
        # Acceptance rate (balanced problems are better for learning)
        acceptance_rate = problem.get('acceptance_rate', 50.0)
        if 25.0 <= acceptance_rate <= 60.0:
            score += 15.0
        elif 20.0 <= acceptance_rate <= 70.0:
            score += 10.0
        
        # Google interview frequency
        google_freq = problem.get('google_interview_frequency', 0.0)
        if google_freq >= 85.0:
            score += 10.0
        elif google_freq >= 75.0:
            score += 5.0
        
        return min(score, 100.0)
    
    def _calculate_google_relevance(self, problem: Dict[str, Any]) -> float:
        """Calculate Google interview relevance"""
        score = 0.0
        
        # Base score from frequency
        google_freq = problem.get('google_interview_frequency', 0.0)
        score += google_freq * 0.6  # Scale to max 60 points
        
        # Algorithm relevance
        algorithm_tags = problem.get('algorithm_tags', [])
        google_relevant_algorithms = {
            'dynamic_programming': 15,
            'binary_search': 12,
            'two_pointers': 10,
            'sliding_window': 10,
            'dfs': 8,
            'bfs': 8,
            'backtracking': 8,
            'heap': 8,
            'graph': 10,
            'tree': 10,
            'hash_table': 6
        }
        
        for tag in algorithm_tags:
            score += google_relevant_algorithms.get(tag, 2)
        
        # Difficulty bonus (Google likes Medium/Hard)
        difficulty = problem.get('difficulty', '').lower()
        if difficulty == 'hard':
            score += 15.0
        elif difficulty == 'medium':
            score += 10.0
        elif difficulty == 'easy':
            score += 5.0
        
        # Company presence
        companies = problem.get('companies', [])
        if 'Google' in companies:
            score += 20.0
        
        return min(score, 100.0)
    
    async def expand_dataset(self):
        """Expand the dataset with new problems and solutions"""
        logger.info("Starting dataset expansion...")
        
        db_session = self.session_factory()
        try:
            # Get new problems
            new_problems = self.get_expanded_problem_set()
            logger.info(f"Generated {len(new_problems)} new problems")
            
            # Store problems
            stored_problems = 0
            for problem_data in new_problems:
                try:
                    # Check if problem already exists
                    existing = db_session.query(Problem).filter_by(id=problem_data['id']).first()
                    if existing:
                        continue
                    
                    # Create problem instance
                    problem = Problem(
                        id=problem_data['id'],
                        platform=problem_data['platform'],
                        platform_id=problem_data['platform_id'],
                        title=problem_data['title'],
                        difficulty=problem_data['difficulty'],
                        description=problem_data['description'],
                        algorithm_tags=problem_data['algorithm_tags'],
                        data_structures=problem_data.get('data_structures', []),
                        google_interview_relevance=problem_data['google_interview_relevance'],
                        quality_score=problem_data['quality_score'],
                        acceptance_rate=problem_data.get('acceptance_rate'),
                        companies=problem_data.get('companies', []),
                        collected_at=problem_data['collected_at']
                    )
                    
                    db_session.add(problem)
                    stored_problems += 1
                    
                except Exception as e:
                    logger.error(f"Error storing problem {problem_data.get('id')}: {e}")
                    db_session.rollback()
                    continue
            
            # Commit problems
            db_session.commit()
            logger.info(f"Stored {stored_problems} new problems")
            
            # Generate and store solutions
            sample_solutions = self.get_sample_solutions()
            stored_solutions = 0
            
            for solution_data in sample_solutions:
                try:
                    # Find matching problem
                    problem_match = None
                    for problem_data in new_problems:
                        if solution_data['problem_identifier'] in problem_data['id']:
                            problem_match = problem_data
                            break
                    
                    if not problem_match:
                        continue
                    
                    # Analyze code quality
                    quality_metrics = self.code_analyzer.analyze_code(solution_data['code'])
                    
                    solution_id = f"{problem_match['id']}_solution_1"
                    
                    solution = Solution(
                        id=solution_id,
                        problem_id=problem_match['id'],
                        code=solution_data['code'],
                        language='python',
                        approach_type=solution_data['approach_type'],
                        algorithm_tags=[solution_data['approach_type']],
                        time_complexity=solution_data['time_complexity'],
                        space_complexity=solution_data['space_complexity'],
                        overall_quality_score=quality_metrics.overall_score,
                        readability_score=quality_metrics.readability_score,
                        documentation_score=quality_metrics.documentation_score,
                        efficiency_score=quality_metrics.efficiency_score,
                        maintainability_score=quality_metrics.maintainability_score,
                        style_score=quality_metrics.style_score,
                        explanation=solution_data['explanation'],
                        google_interview_relevance=problem_match['google_interview_relevance'],
                        educational_value=85.0,
                        implementation_difficulty=3,
                        conceptual_difficulty=4
                    )
                    
                    db_session.add(solution)
                    stored_solutions += 1
                    
                except Exception as e:
                    logger.error(f"Error storing solution: {e}")
                    db_session.rollback()
                    continue
            
            # Commit solutions
            db_session.commit()
            logger.info(f"Stored {stored_solutions} new solutions")
            
            logger.info(f"Dataset expansion completed! Added {stored_problems} problems and {stored_solutions} solutions")
            
        finally:
            db_session.close()


async def main():
    """Main entry point"""
    expander = EnhancedDataExpander()
    await expander.expand_dataset()


if __name__ == "__main__":
    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)
    asyncio.run(main())

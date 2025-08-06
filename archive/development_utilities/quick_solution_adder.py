"""
Quick solution addition script to expand our solution dataset
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.models.database import DatabaseConfig, Problem, Solution
from src.analysis.code_quality import PythonCodeAnalyzer
from datetime import datetime

class QuickSolutionAdder:
    """Quickly add more solutions to existing problems"""
    
    def __init__(self):
        self.db_config = DatabaseConfig()
        self.session_factory = self.db_config.SessionLocal
        self.code_analyzer = PythonCodeAnalyzer()
    
    def get_additional_solutions(self):
        """Get additional solution implementations"""
        solutions = [
            # Two Sum - Alternative approach
            {
                "problem_pattern": "two_sum",
                "code": '''def twoSum(nums, target):
    """
    Two Sum using sorting and two pointers.
    Time: O(n log n), Space: O(n)
    """
    # Create array of (value, index) pairs
    indexed_nums = [(num, i) for i, num in enumerate(nums)]
    
    # Sort by value
    indexed_nums.sort()
    
    left, right = 0, len(indexed_nums) - 1
    
    while left < right:
        current_sum = indexed_nums[left][0] + indexed_nums[right][0]
        
        if current_sum == target:
            return [indexed_nums[left][1], indexed_nums[right][1]]
        elif current_sum < target:
            left += 1
        else:
            right -= 1
    
    return []''',
                "approach_type": "sorting_two_pointers",
                "time_complexity": "O(n log n)",
                "space_complexity": "O(n)",
                "explanation": "Sort array with indices, then use two pointers technique"
            },
            
            # Binary Search - Template approach
            {
                "problem_pattern": "search_rotated_array",
                "code": '''def search(nums, target):
    """
    Search in rotated sorted array using binary search template.
    Time: O(log n), Space: O(1)
    """
    left, right = 0, len(nums) - 1
    
    while left <= right:
        mid = left + (right - left) // 2
        
        if nums[mid] == target:
            return mid
        
        # Determine which half is sorted
        if nums[left] <= nums[mid]:  # Left half is sorted
            if nums[left] <= target < nums[mid]:
                right = mid - 1  # Target in left half
            else:
                left = mid + 1   # Target in right half
        else:  # Right half is sorted
            if nums[mid] < target <= nums[right]:
                left = mid + 1   # Target in right half
            else:
                right = mid - 1  # Target in left half
    
    return -1''',
                "approach_type": "binary_search",
                "time_complexity": "O(log n)",
                "space_complexity": "O(1)",
                "explanation": "Binary search with rotation handling by checking which half is sorted"
            },
            
            # Container with Most Water - Proof approach
            {
                "problem_pattern": "container_water",
                "code": '''def maxArea(height):
    """
    Container with most water - optimized two pointers with proof.
    Time: O(n), Space: O(1)
    """
    max_area = 0
    left, right = 0, len(height) - 1
    
    while left < right:
        # Calculate current area
        width = right - left
        current_height = min(height[left], height[right])
        current_area = width * current_height
        max_area = max(max_area, current_area)
        
        # Move the pointer with shorter height
        # Proof: Moving the taller pointer can never increase area
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
    
    return max_area''',
                "approach_type": "two_pointers_optimized",
                "time_complexity": "O(n)",
                "space_complexity": "O(1)",
                "explanation": "Two pointers with mathematical proof of optimality"
            },
            
            # 3Sum - Optimized with early termination
            {
                "problem_pattern": "3sum",
                "code": '''def threeSum(nums):
    """
    3Sum with optimizations and early termination.
    Time: O(n²), Space: O(1) excluding output
    """
    if len(nums) < 3:
        return []
    
    nums.sort()
    result = []
    
    for i in range(len(nums) - 2):
        # Early termination: if smallest number > 0, no solution
        if nums[i] > 0:
            break
            
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
                "approach_type": "two_pointers_optimized",
                "time_complexity": "O(n²)",
                "space_complexity": "O(1)",
                "explanation": "Optimized 3Sum with early termination and duplicate handling"
            },
            
            # Top K Frequent - Bucket Sort approach
            {
                "problem_pattern": "top_k_frequent",
                "code": '''def topKFrequent(nums, k):
    """
    Top K frequent elements using bucket sort approach.
    Time: O(n), Space: O(n)
    """
    from collections import Counter
    
    # Count frequencies
    counter = Counter(nums)
    
    # Create buckets: index = frequency, value = list of numbers
    buckets = [[] for _ in range(len(nums) + 1)]
    
    # Fill buckets
    for num, freq in counter.items():
        buckets[freq].append(num)
    
    # Collect top k elements from highest frequency buckets
    result = []
    for i in range(len(buckets) - 1, 0, -1):
        if buckets[i]:
            result.extend(buckets[i])
            if len(result) >= k:
                break
    
    return result[:k]''',
                "approach_type": "bucket_sort",
                "time_complexity": "O(n)",
                "space_complexity": "O(n)",
                "explanation": "Bucket sort approach for O(n) time complexity instead of O(n log n)"
            },
            
            # Coin Change - Optimized DP
            {
                "problem_pattern": "coin_change",
                "code": '''def coinChange(coins, amount):
    """
    Coin change with space-optimized DP and early termination.
    Time: O(amount * coins), Space: O(amount)
    """
    if amount == 0:
        return 0
    if amount < 0:
        return -1
    
    # Sort coins in descending order for better pruning
    coins.sort(reverse=True)
    
    # DP array: dp[i] = minimum coins needed for amount i
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    
    for coin in coins:
        for i in range(coin, amount + 1):
            if dp[i - coin] != float('inf'):
                dp[i] = min(dp[i], dp[i - coin] + 1)
    
    return dp[amount] if dp[amount] != float('inf') else -1''',
                "approach_type": "dynamic_programming_optimized",
                "time_complexity": "O(amount * coins)",
                "space_complexity": "O(amount)",
                "explanation": "Optimized DP with coin sorting for better performance"
            }
        ]
        
        return solutions
    
    async def add_solutions(self):
        """Add solutions to existing problems"""
        print("Adding additional solutions...")
        
        db_session = self.session_factory()
        try:
            # Get additional solutions
            additional_solutions = self.get_additional_solutions()
            
            # Get existing problems
            problems = db_session.query(Problem).all()
            
            added_count = 0
            
            for solution_data in additional_solutions:
                # Find matching problem
                matching_problem = None
                for problem in problems:
                    if solution_data['problem_pattern'] in problem.id.lower():
                        matching_problem = problem
                        break
                
                if not matching_problem:
                    continue
                
                # Check if similar solution already exists
                existing_solutions = db_session.query(Solution).filter_by(
                    problem_id=matching_problem.id
                ).all()
                
                # Generate unique solution ID
                solution_num = len(existing_solutions) + 1
                solution_id = f"{matching_problem.id}_solution_{solution_num}"
                
                # Analyze code quality
                try:
                    quality_metrics = self.code_analyzer.analyze_code(solution_data['code'])
                    
                    # Create solution
                    solution = Solution(
                        id=solution_id,
                        problem_id=matching_problem.id,
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
                        google_interview_relevance=matching_problem.google_interview_relevance,
                        educational_value=85.0,
                        implementation_difficulty=3,
                        conceptual_difficulty=4,
                        created_at=datetime.now()
                    )
                    
                    db_session.add(solution)
                    added_count += 1
                    print(f"✓ Added solution for {matching_problem.title}")
                    
                except Exception as e:
                    print(f"✗ Error adding solution for {matching_problem.title}: {e}")
                    continue
            
            # Commit all solutions
            db_session.commit()
            print(f"\n✅ Successfully added {added_count} additional solutions!")
            
        except Exception as e:
            print(f"❌ Error adding solutions: {e}")
            db_session.rollback()
        finally:
            db_session.close()

async def main():
    """Main entry point"""
    adder = QuickSolutionAdder()
    await adder.add_solutions()

if __name__ == "__main__":
    asyncio.run(main())

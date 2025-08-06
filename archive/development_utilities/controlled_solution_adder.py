"""
Controlled Solution Addition with Better ID Management
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.models.database import DatabaseConfig, Problem, Solution
from src.analysis.code_quality import PythonCodeAnalyzer
from datetime import datetime
import uuid

class ControlledSolutionAdder:
    """Add solutions with proper ID management"""
    
    def __init__(self):
        self.db_config = DatabaseConfig()
        self.session_factory = self.db_config.SessionLocal
        self.code_analyzer = PythonCodeAnalyzer()
    
    def get_high_quality_solutions(self):
        """Get a focused set of high-quality solutions"""
        return [
            # Dynamic Programming - Fibonacci with memoization
            {
                "pattern": "dynamic_programming",
                "code": '''def fibMemo(n, memo={}):
    """
    Fibonacci with memoization
    Time: O(n), Space: O(n)
    """
    if n in memo:
        return memo[n]
    if n <= 2:
        return 1
    
    memo[n] = fibMemo(n-1, memo) + fibMemo(n-2, memo)
    return memo[n]''',
                "approach": "memoization",
                "time": "O(n)",
                "space": "O(n)",
                "explanation": "Top-down dynamic programming with memoization"
            },
            
            # Two Pointers - Remove duplicates
            {
                "pattern": "two_pointers",
                "code": '''def removeDuplicates(nums):
    """
    Remove duplicates from sorted array
    Time: O(n), Space: O(1)
    """
    if not nums:
        return 0
    
    write_index = 1
    
    for read_index in range(1, len(nums)):
        if nums[read_index] != nums[read_index - 1]:
            nums[write_index] = nums[read_index]
            write_index += 1
    
    return write_index''',
                "approach": "two_pointer_inplace",
                "time": "O(n)",
                "space": "O(1)",
                "explanation": "Two pointer technique for in-place duplicate removal"
            },
            
            # Binary Search - Peak element
            {
                "pattern": "binary_search",
                "code": '''def findPeakElement(nums):
    """
    Find peak element using binary search
    Time: O(log n), Space: O(1)
    """
    left, right = 0, len(nums) - 1
    
    while left < right:
        mid = (left + right) // 2
        
        if nums[mid] > nums[mid + 1]:
            # Peak is in left half (including mid)
            right = mid
        else:
            # Peak is in right half
            left = mid + 1
    
    return left''',
                "approach": "binary_search_peak",
                "time": "O(log n)",
                "space": "O(1)",
                "explanation": "Binary search to find peak element efficiently"
            },
            
            # Graph - Union Find
            {
                "pattern": "graph",
                "code": '''class UnionFind:
    """
    Union Find (Disjoint Set) implementation
    Time: O(α(n)) per operation, Space: O(n)
    """
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.components = n
    
    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # Path compression
        return self.parent[x]
    
    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        
        # Union by rank
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
        
        self.components -= 1
        return True''',
                "approach": "union_find",
                "time": "O(α(n))",
                "space": "O(n)",
                "explanation": "Union Find with path compression and union by rank"
            },
            
            # Heap - Merge intervals
            {
                "pattern": "heap",
                "code": '''def mergeIntervals(intervals):
    """
    Merge overlapping intervals
    Time: O(n log n), Space: O(1)
    """
    if not intervals:
        return []
    
    # Sort by start time
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]
    
    for current in intervals[1:]:
        last = merged[-1]
        
        if current[0] <= last[1]:
            # Overlapping intervals, merge them
            merged[-1] = [last[0], max(last[1], current[1])]
        else:
            # Non-overlapping interval
            merged.append(current)
    
    return merged''',
                "approach": "interval_merging",
                "time": "O(n log n)",
                "space": "O(1)",
                "explanation": "Sort and merge overlapping intervals efficiently"
            },
            
            # Sliding Window - Max in window
            {
                "pattern": "sliding_window",
                "code": '''def maxSlidingWindow(nums, k):
    """
    Maximum element in sliding window using deque
    Time: O(n), Space: O(k)
    """
    from collections import deque
    
    if not nums or k == 0:
        return []
    
    dq = deque()  # Store indices
    result = []
    
    for i in range(len(nums)):
        # Remove indices outside current window
        while dq and dq[0] <= i - k:
            dq.popleft()
        
        # Remove smaller elements from back
        while dq and nums[dq[-1]] < nums[i]:
            dq.pop()
        
        dq.append(i)
        
        # Add maximum to result (window is complete)
        if i >= k - 1:
            result.append(nums[dq[0]])
    
    return result''',
                "approach": "deque_sliding_window",
                "time": "O(n)",
                "space": "O(k)",
                "explanation": "Deque-based sliding window maximum tracking"
            }
        ]
    
    async def add_solutions_carefully(self):
        """Add solutions with careful ID management"""
        print("🎯 Starting controlled solution addition...")
        
        db_session = self.session_factory()
        try:
            solutions_to_add = self.get_high_quality_solutions()
            problems = db_session.query(Problem).all()
            
            added_count = 0
            
            for solution_data in solutions_to_add:
                # Find problems that match the pattern
                matching_problems = []
                for problem in problems:
                    # Check algorithm tags for pattern match
                    if any(tag in solution_data['pattern'] or solution_data['pattern'] in tag 
                          for tag in problem.algorithm_tags):
                        matching_problems.append(problem)
                
                # Add to first 2 matching problems
                for problem in matching_problems[:2]:
                    try:
                        # Get current solution count for this problem
                        existing_count = db_session.query(Solution).filter_by(
                            problem_id=problem.id
                        ).count()
                        
                        # Generate unique ID with UUID
                        solution_id = f"{problem.id}_sol_{uuid.uuid4().hex[:8]}"
                        
                        # Ensure ID is unique
                        while db_session.query(Solution).filter_by(id=solution_id).first():
                            solution_id = f"{problem.id}_sol_{uuid.uuid4().hex[:8]}"
                        
                        # Analyze code quality
                        quality_metrics = self.code_analyzer.analyze_code(solution_data['code'])
                        
                        # Create solution
                        solution = Solution(
                            id=solution_id,
                            problem_id=problem.id,
                            code=solution_data['code'],
                            language='python',
                            approach_type=solution_data['approach'],
                            algorithm_tags=[solution_data['approach']],
                            time_complexity=solution_data['time'],
                            space_complexity=solution_data['space'],
                            overall_quality_score=quality_metrics.overall_score,
                            readability_score=quality_metrics.readability_score,
                            documentation_score=quality_metrics.documentation_score,
                            efficiency_score=quality_metrics.efficiency_score,
                            maintainability_score=quality_metrics.maintainability_score,
                            style_score=quality_metrics.style_score,
                            explanation=solution_data['explanation'],
                            google_interview_relevance=problem.google_interview_relevance,
                            educational_value=85.0,
                            implementation_difficulty=3,
                            conceptual_difficulty=4,
                            created_at=datetime.now()
                        )
                        
                        db_session.add(solution)
                        db_session.flush()  # Flush to check for errors
                        added_count += 1
                        print(f"  ✅ Added {solution_data['approach']} solution for {problem.title}")
                        
                    except Exception as e:
                        print(f"  ❌ Error adding solution for {problem.title}: {e}")
                        db_session.rollback()
                        continue
            
            # Final commit
            db_session.commit()
            print(f"\n🎉 Successfully added {added_count} new solutions!")
            
            # Get final stats
            total_solutions = db_session.query(Solution).count()
            print(f"📊 Total solutions in database: {total_solutions}")
            
        except Exception as e:
            print(f"❌ Error during addition: {e}")
            db_session.rollback()
        finally:
            db_session.close()

async def main():
    """Main entry point"""
    adder = ControlledSolutionAdder()
    await adder.add_solutions_carefully()

if __name__ == "__main__":
    asyncio.run(main())

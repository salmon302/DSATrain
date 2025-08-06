"""
Advanced Solution Expansion for DSATrain
Comprehensive solution collection across all algorithm categories
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.models.database import DatabaseConfig, Problem, Solution
from src.analysis.code_quality import PythonCodeAnalyzer
from datetime import datetime
import uuid

class AdvancedSolutionExpander:
    """Comprehensive solution expansion across all problem types"""
    
    def __init__(self):
        self.db_config = DatabaseConfig()
        self.session_factory = self.db_config.SessionLocal
        self.code_analyzer = PythonCodeAnalyzer()
    
    def get_comprehensive_solutions(self):
        """Get comprehensive solution set covering all major patterns"""
        return {
            # Dynamic Programming Solutions
            "dynamic_programming": [
                {
                    "code": '''def coinChange(coins, amount):
    """
    Coin Change - Space Optimized DP
    Time: O(amount * coins), Space: O(amount)
    """
    if amount == 0:
        return 0
    
    # Bottom-up DP
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    
    for i in range(1, amount + 1):
        for coin in coins:
            if coin <= i and dp[i - coin] != float('inf'):
                dp[i] = min(dp[i], dp[i - coin] + 1)
    
    return dp[amount] if dp[amount] != float('inf') else -1''',
                    "approach": "bottom_up_dp",
                    "time": "O(amount * coins)",
                    "space": "O(amount)",
                    "explanation": "Bottom-up DP building solutions from smaller subproblems"
                },
                {
                    "code": '''def longestIncreasingSubsequence(nums):
    """
    LIS using Binary Search optimization
    Time: O(n log n), Space: O(n)
    """
    if not nums:
        return 0
    
    # tails[i] = smallest ending element of all increasing subsequences of length i+1
    tails = []
    
    for num in nums:
        # Binary search for the position to insert/replace
        left, right = 0, len(tails)
        while left < right:
            mid = (left + right) // 2
            if tails[mid] < num:
                left = mid + 1
            else:
                right = mid
        
        # If num is larger than all elements, append it
        if left == len(tails):
            tails.append(num)
        else:
            tails[left] = num
    
    return len(tails)''',
                    "approach": "binary_search_optimization",
                    "time": "O(n log n)",
                    "space": "O(n)",
                    "explanation": "Binary search optimization for LIS problem"
                }
            ],
            
            # Tree Algorithm Solutions
            "tree": [
                {
                    "code": '''def maxPathSum(root):
    """
    Binary Tree Maximum Path Sum - Recursive DFS
    Time: O(n), Space: O(h) where h is height
    """
    def dfs(node):
        nonlocal max_sum
        if not node:
            return 0
        
        # Get max gain from left and right subtrees
        left_gain = max(dfs(node.left), 0)
        right_gain = max(dfs(node.right), 0)
        
        # Current max path through this node
        current_max = node.val + left_gain + right_gain
        max_sum = max(max_sum, current_max)
        
        # Return max gain if we continue the path through this node
        return node.val + max(left_gain, right_gain)
    
    max_sum = float('-inf')
    dfs(root)
    return max_sum''',
                    "approach": "recursive_dfs",
                    "time": "O(n)",
                    "space": "O(h)",
                    "explanation": "DFS with path sum tracking through each node"
                },
                {
                    "code": '''def isValidBST(root):
    """
    Validate BST using inorder traversal
    Time: O(n), Space: O(h)
    """
    def inorder(node):
        if not node:
            return True
        
        # Check left subtree
        if not inorder(node.left):
            return False
        
        # Check current node
        if self.prev and self.prev.val >= node.val:
            return False
        self.prev = node
        
        # Check right subtree
        return inorder(node.right)
    
    self.prev = None
    return inorder(root)''',
                    "approach": "inorder_traversal",
                    "time": "O(n)",
                    "space": "O(h)",
                    "explanation": "Inorder traversal to validate BST property"
                }
            ],
            
            # Graph Algorithm Solutions
            "graph": [
                {
                    "code": '''def canFinish(numCourses, prerequisites):
    """
    Course Schedule - Topological Sort using DFS
    Time: O(V + E), Space: O(V + E)
    """
    # Build adjacency list
    graph = {i: [] for i in range(numCourses)}
    for course, prereq in prerequisites:
        graph[prereq].append(course)
    
    # 0: unvisited, 1: visiting, 2: visited
    state = [0] * numCourses
    
    def hasCycle(course):
        if state[course] == 1:  # Currently visiting - cycle detected
            return True
        if state[course] == 2:  # Already visited
            return False
        
        state[course] = 1  # Mark as visiting
        for neighbor in graph[course]:
            if hasCycle(neighbor):
                return True
        state[course] = 2  # Mark as visited
        return False
    
    # Check for cycles in all components
    for course in range(numCourses):
        if hasCycle(course):
            return False
    
    return True''',
                    "approach": "topological_sort_dfs",
                    "time": "O(V + E)",
                    "space": "O(V + E)",
                    "explanation": "DFS-based cycle detection for topological sorting"
                },
                {
                    "code": '''def numIslands(grid):
    """
    Number of Islands - DFS approach
    Time: O(m * n), Space: O(m * n) worst case
    """
    if not grid or not grid[0]:
        return 0
    
    rows, cols = len(grid), len(grid[0])
    count = 0
    
    def dfs(r, c):
        # Check bounds and if it's water or already visited
        if (r < 0 or r >= rows or c < 0 or c >= cols or 
            grid[r][c] != '1'):
            return
        
        # Mark as visited
        grid[r][c] = '0'
        
        # Explore all 4 directions
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        for dr, dc in directions:
            dfs(r + dr, c + dc)
    
    # Find all islands
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '1':
                dfs(r, c)
                count += 1
    
    return count''',
                    "approach": "dfs_grid_traversal",
                    "time": "O(m * n)",
                    "space": "O(m * n)",
                    "explanation": "DFS to mark connected components (islands)"
                }
            ],
            
            # Sliding Window Solutions
            "sliding_window": [
                {
                    "code": '''def lengthOfLongestSubstring(s):
    """
    Longest Substring Without Repeating Characters
    Time: O(n), Space: O(min(m, n)) where m is charset size
    """
    char_index = {}
    left = 0
    max_length = 0
    
    for right in range(len(s)):
        char = s[right]
        
        # If character is already in current window, move left pointer
        if char in char_index and char_index[char] >= left:
            left = char_index[char] + 1
        
        char_index[char] = right
        max_length = max(max_length, right - left + 1)
    
    return max_length''',
                    "approach": "sliding_window_hashmap",
                    "time": "O(n)",
                    "space": "O(min(m, n))",
                    "explanation": "Sliding window with hash map for character tracking"
                },
                {
                    "code": '''def minWindow(s, t):
    """
    Minimum Window Substring - Optimized sliding window
    Time: O(|s| + |t|), Space: O(|s| + |t|)
    """
    if not s or not t or len(s) < len(t):
        return ""
    
    # Count characters in t
    t_count = {}
    for char in t:
        t_count[char] = t_count.get(char, 0) + 1
    
    required = len(t_count)
    formed = 0
    window_counts = {}
    
    # Two pointers
    left = right = 0
    min_len = float('inf')
    min_left = 0
    
    while right < len(s):
        # Expand window
        char = s[right]
        window_counts[char] = window_counts.get(char, 0) + 1
        
        if char in t_count and window_counts[char] == t_count[char]:
            formed += 1
        
        # Contract window
        while left <= right and formed == required:
            # Update result if smaller window found
            if right - left + 1 < min_len:
                min_len = right - left + 1
                min_left = left
            
            char = s[left]
            window_counts[char] -= 1
            if char in t_count and window_counts[char] < t_count[char]:
                formed -= 1
            
            left += 1
        
        right += 1
    
    return "" if min_len == float('inf') else s[min_left:min_left + min_len]''',
                    "approach": "two_pointer_sliding_window",
                    "time": "O(|s| + |t|)",
                    "space": "O(|s| + |t|)",
                    "explanation": "Two-pointer sliding window with frequency tracking"
                }
            ],
            
            # Backtracking Solutions
            "backtracking": [
                {
                    "code": '''def combinationSum(candidates, target):
    """
    Combination Sum - Backtracking with pruning
    Time: O(2^n), Space: O(target/min(candidates))
    """
    def backtrack(remaining, start, path):
        if remaining == 0:
            result.append(path[:])
            return
        if remaining < 0:
            return
        
        for i in range(start, len(candidates)):
            # Pruning: if current candidate > remaining, skip
            if candidates[i] > remaining:
                break
            
            path.append(candidates[i])
            # Use same index since we can reuse numbers
            backtrack(remaining - candidates[i], i, path)
            path.pop()
    
    candidates.sort()  # Sort for pruning optimization
    result = []
    backtrack(target, 0, [])
    return result''',
                    "approach": "backtracking_with_pruning",
                    "time": "O(2^n)",
                    "space": "O(target/min(candidates))",
                    "explanation": "Backtracking with sorting and pruning optimizations"
                },
                {
                    "code": '''def exist(board, word):
    """
    Word Search - Backtracking on 2D grid
    Time: O(m * n * 4^L), Space: O(L) where L is word length
    """
    if not board or not board[0] or not word:
        return False
    
    rows, cols = len(board), len(board[0])
    
    def backtrack(r, c, index):
        # Found the word
        if index == len(word):
            return True
        
        # Check bounds and character match
        if (r < 0 or r >= rows or c < 0 or c >= cols or 
            board[r][c] != word[index] or board[r][c] == '#'):
            return False
        
        # Mark as visited
        temp = board[r][c]
        board[r][c] = '#'
        
        # Explore all 4 directions
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        found = any(backtrack(r + dr, c + dc, index + 1) 
                   for dr, dc in directions)
        
        # Restore cell
        board[r][c] = temp
        return found
    
    # Try starting from each cell
    for r in range(rows):
        for c in range(cols):
            if backtrack(r, c, 0):
                return True
    
    return False''',
                    "approach": "backtracking_2d_grid",
                    "time": "O(m * n * 4^L)",
                    "space": "O(L)",
                    "explanation": "Backtracking with visited cell marking and restoration"
                }
            ],
            
            # Heap/Priority Queue Solutions
            "heap": [
                {
                    "code": '''def topKFrequent(nums, k):
    """
    Top K Frequent Elements - Min Heap approach
    Time: O(n log k), Space: O(n + k)
    """
    import heapq
    from collections import Counter
    
    # Count frequencies
    count = Counter(nums)
    
    # Use min heap to keep top k elements
    heap = []
    for num, freq in count.items():
        heapq.heappush(heap, (freq, num))
        if len(heap) > k:
            heapq.heappop(heap)
    
    # Extract elements (in reverse order for most frequent first)
    return [num for freq, num in heap]''',
                    "approach": "min_heap_topk",
                    "time": "O(n log k)",
                    "space": "O(n + k)",
                    "explanation": "Min heap to maintain top k frequent elements efficiently"
                },
                {
                    "code": '''def findKthLargest(nums, k):
    """
    Kth Largest Element - QuickSelect algorithm
    Time: O(n) average, O(n²) worst, Space: O(1)
    """
    def quickselect(left, right, k_smallest):
        # Base case: the list contains only one element
        if left == right:
            return nums[left]
        
        # Select random pivot
        import random
        pivot_index = random.randint(left, right)
        
        # Partition around pivot
        pivot_index = partition(left, right, pivot_index)
        
        # Compare pivot position with k
        if k_smallest == pivot_index:
            return nums[k_smallest]
        elif k_smallest < pivot_index:
            return quickselect(left, pivot_index - 1, k_smallest)
        else:
            return quickselect(pivot_index + 1, right, k_smallest)
    
    def partition(left, right, pivot_index):
        pivot = nums[pivot_index]
        # Move pivot to end
        nums[pivot_index], nums[right] = nums[right], nums[pivot_index]
        
        # Partition
        store_index = left
        for i in range(left, right):
            if nums[i] < pivot:
                nums[store_index], nums[i] = nums[i], nums[store_index]
                store_index += 1
        
        # Move pivot to final position
        nums[right], nums[store_index] = nums[store_index], nums[right]
        return store_index
    
    # kth largest is (n-k)th smallest
    return quickselect(0, len(nums) - 1, len(nums) - k)''',
                    "approach": "quickselect",
                    "time": "O(n) average",
                    "space": "O(1)",
                    "explanation": "QuickSelect algorithm for finding kth largest element"
                }
            ]
        }
    
    async def expand_solutions(self):
        """Add comprehensive solutions across all categories"""
        print("🚀 Starting comprehensive solution expansion...")
        
        db_session = self.session_factory()
        try:
            # Get all solutions by category
            all_solutions = self.get_comprehensive_solutions()
            
            # Get existing problems
            problems = db_session.query(Problem).all()
            print(f"📊 Found {len(problems)} problems to enhance")
            
            added_count = 0
            
            for category, solutions in all_solutions.items():
                print(f"\n🔧 Processing {category} solutions...")
                
                for solution_data in solutions:
                    # Find matching problems by algorithm tags
                    matching_problems = [
                        p for p in problems 
                        if any(tag in p.algorithm_tags for tag in [category, solution_data['approach'].split('_')[0]])
                    ]
                    
                    for problem in matching_problems[:2]:  # Limit to 2 problems per solution pattern
                        try:
                            # Check existing solutions count
                            existing_count = db_session.query(Solution).filter_by(
                                problem_id=problem.id
                            ).count()
                            
                            # Skip if already has many solutions
                            if existing_count >= 3:
                                continue
                            
                            # Generate unique solution ID
                            solution_id = f"{problem.id}_solution_{existing_count + 1}"
                            
                            # Analyze code quality
                            quality_metrics = self.code_analyzer.analyze_code(solution_data['code'])
                            
                            # Create solution
                            solution = Solution(
                                id=solution_id,
                                problem_id=problem.id,
                                code=solution_data['code'],
                                language='python',
                                approach_type=solution_data['approach'],
                                algorithm_tags=[solution_data['approach'], category],
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
                                educational_value=90.0,
                                implementation_difficulty=4,
                                conceptual_difficulty=4,
                                created_at=datetime.now()
                            )
                            
                            db_session.add(solution)
                            added_count += 1
                            print(f"  ✅ Added {solution_data['approach']} solution for {problem.title}")
                            
                        except Exception as e:
                            print(f"  ❌ Error adding solution for {problem.title}: {e}")
                            continue
            
            # Commit all solutions
            db_session.commit()
            print(f"\n🎉 Successfully added {added_count} comprehensive solutions!")
            print(f"📈 Total solutions now: {db_session.query(Solution).count()}")
            
        except Exception as e:
            print(f"❌ Error during expansion: {e}")
            db_session.rollback()
        finally:
            db_session.close()

async def main():
    """Main entry point"""
    expander = AdvancedSolutionExpander()
    await expander.expand_solutions()

if __name__ == "__main__":
    asyncio.run(main())

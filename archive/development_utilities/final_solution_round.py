"""
Final Solution Round - Additional High-Quality Solutions
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.models.database import DatabaseConfig, Problem, Solution
from src.analysis.code_quality import PythonCodeAnalyzer
from datetime import datetime
import uuid

class FinalSolutionRound:
    """Add the final batch of solutions"""
    
    def __init__(self):
        self.db_config = DatabaseConfig()
        self.session_factory = self.db_config.SessionLocal
        self.code_analyzer = PythonCodeAnalyzer()
    
    def get_final_solution_batch(self):
        """Get additional high-quality solutions"""
        return [
            # Backtracking - N-Queens approach
            {
                "pattern": "backtracking",
                "code": '''def solveNQueens(n):
    """
    N-Queens backtracking solution
    Time: O(N!), Space: O(N²)
    """
    def is_safe(board, row, col):
        # Check column
        for i in range(row):
            if board[i][col] == 'Q':
                return False
        
        # Check diagonal (top-left to bottom-right)
        i, j = row - 1, col - 1
        while i >= 0 and j >= 0:
            if board[i][j] == 'Q':
                return False
            i -= 1
            j -= 1
        
        # Check diagonal (top-right to bottom-left)
        i, j = row - 1, col + 1
        while i >= 0 and j < n:
            if board[i][j] == 'Q':
                return False
            i -= 1
            j += 1
        
        return True
    
    def backtrack(board, row):
        if row == n:
            return [[''.join(row) for row in board]]
        
        solutions = []
        for col in range(n):
            if is_safe(board, row, col):
                board[row][col] = 'Q'
                solutions.extend(backtrack(board, row + 1))
                board[row][col] = '.'  # backtrack
        
        return solutions
    
    board = [['.' for _ in range(n)] for _ in range(n)]
    return backtrack(board, 0)''',
                "approach": "backtracking_nqueens",
                "time": "O(N!)",
                "space": "O(N²)",
                "explanation": "Classic backtracking with constraint checking"
            },
            
            # Trie - Prefix tree implementation
            {
                "pattern": "trie",
                "code": '''class TrieNode:
    """Trie node with children and end marker"""
    def __init__(self):
        self.children = {}
        self.is_end = False

class Trie:
    """
    Prefix tree (Trie) implementation
    Time: O(m) per operation, Space: O(ALPHABET_SIZE * N * M)
    """
    def __init__(self):
        self.root = TrieNode()
    
    def insert(self, word):
        """Insert word into trie"""
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True
    
    def search(self, word):
        """Search for exact word"""
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end
    
    def starts_with(self, prefix):
        """Check if any word starts with prefix"""
        node = self.root
        for char in prefix:
            if char not in node.children:
                return False
            node = node.children[char]
        return True''',
                "approach": "trie_implementation",
                "time": "O(m)",
                "space": "O(ALPHABET_SIZE * N * M)",
                "explanation": "Prefix tree for efficient string operations"
            },
            
            # Greedy - Activity selection
            {
                "pattern": "greedy",
                "code": '''def activitySelection(activities):
    """
    Activity selection using greedy approach
    Time: O(n log n), Space: O(1)
    """
    # Sort by end time (greedy choice)
    activities.sort(key=lambda x: x[1])
    
    selected = []
    last_end_time = 0
    
    for start, end in activities:
        # If activity doesn't overlap with last selected
        if start >= last_end_time:
            selected.append((start, end))
            last_end_time = end
    
    return selected

def fractionalKnapsack(items, capacity):
    """
    Fractional knapsack using greedy approach
    Time: O(n log n), Space: O(1)
    """
    # Sort by value/weight ratio (greedy choice)
    items.sort(key=lambda x: x[1]/x[0], reverse=True)
    
    total_value = 0
    current_weight = 0
    
    for weight, value in items:
        if current_weight + weight <= capacity:
            # Take entire item
            current_weight += weight
            total_value += value
        else:
            # Take fraction of item
            remaining = capacity - current_weight
            total_value += value * (remaining / weight)
            break
    
    return total_value''',
                "approach": "greedy_optimization",
                "time": "O(n log n)",
                "space": "O(1)",
                "explanation": "Greedy algorithms for optimization problems"
            },
            
            # Divide and Conquer - Merge sort
            {
                "pattern": "divide_conquer",
                "code": '''def mergeSort(arr):
    """
    Merge sort using divide and conquer
    Time: O(n log n), Space: O(n)
    """
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = mergeSort(arr[:mid])
    right = mergeSort(arr[mid:])
    
    return merge(left, right)

def merge(left, right):
    """Merge two sorted arrays"""
    result = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    # Add remaining elements
    result.extend(left[i:])
    result.extend(right[j:])
    
    return result

def quickSelect(arr, k):
    """
    Quick select for kth smallest element
    Time: O(n) average, O(n²) worst, Space: O(log n)
    """
    def partition(arr, low, high):
        pivot = arr[high]
        i = low - 1
        
        for j in range(low, high):
            if arr[j] <= pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
        
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        return i + 1
    
    def quickselect_util(arr, low, high, k):
        if low <= high:
            pi = partition(arr, low, high)
            
            if pi == k:
                return arr[pi]
            elif pi > k:
                return quickselect_util(arr, low, pi - 1, k)
            else:
                return quickselect_util(arr, pi + 1, high, k)
    
    return quickselect_util(arr[:], 0, len(arr) - 1, k - 1)''',
                "approach": "divide_and_conquer",
                "time": "O(n log n)",
                "space": "O(n)",
                "explanation": "Classic divide and conquer algorithms"
            },
            
            # Matrix - Spiral traversal
            {
                "pattern": "matrix",
                "code": '''def spiralOrder(matrix):
    """
    Spiral matrix traversal
    Time: O(m*n), Space: O(1)
    """
    if not matrix or not matrix[0]:
        return []
    
    result = []
    top, bottom = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1
    
    while top <= bottom and left <= right:
        # Traverse right
        for col in range(left, right + 1):
            result.append(matrix[top][col])
        top += 1
        
        # Traverse down
        for row in range(top, bottom + 1):
            result.append(matrix[row][right])
        right -= 1
        
        if top <= bottom:
            # Traverse left
            for col in range(right, left - 1, -1):
                result.append(matrix[bottom][col])
            bottom -= 1
        
        if left <= right:
            # Traverse up
            for row in range(bottom, top - 1, -1):
                result.append(matrix[row][left])
            left += 1
    
    return result''',
                "approach": "matrix_spiral",
                "time": "O(m*n)",
                "space": "O(1)",
                "explanation": "Efficient matrix spiral traversal"
            },
            
            # Bit Manipulation - Advanced operations
            {
                "pattern": "bit_manipulation",
                "code": '''def countSetBits(n):
    """
    Count set bits using Brian Kernighan's algorithm
    Time: O(number of set bits), Space: O(1)
    """
    count = 0
    while n:
        count += 1
        n &= n - 1  # Clear rightmost set bit
    return count

def singleNumber(nums):
    """
    Find single number using XOR
    Time: O(n), Space: O(1)
    """
    result = 0
    for num in nums:
        result ^= num
    return result

def isPowerOfTwo(n):
    """
    Check if number is power of 2
    Time: O(1), Space: O(1)
    """
    return n > 0 and (n & (n - 1)) == 0

def reverseBits(n):
    """
    Reverse bits of a 32-bit integer
    Time: O(1), Space: O(1)
    """
    result = 0
    for i in range(32):
        # Extract LSB and add to result
        result = (result << 1) | (n & 1)
        n >>= 1
    return result''',
                "approach": "bit_manipulation_advanced",
                "time": "O(1) to O(n)",
                "space": "O(1)",
                "explanation": "Advanced bit manipulation techniques"
            }
        ]
    
    async def add_final_solutions(self):
        """Add final batch of solutions"""
        print("🎯 Starting final solution round...")
        
        db_session = self.session_factory()
        try:
            solutions_to_add = self.get_final_solution_batch()
            problems = db_session.query(Problem).all()
            
            added_count = 0
            
            for solution_data in solutions_to_add:
                # Find problems that could use this approach
                suitable_problems = []
                
                for problem in problems:
                    # Get current solution count
                    current_solutions = db_session.query(Solution).filter_by(
                        problem_id=problem.id
                    ).count()
                    
                    # Skip if already has 3+ solutions
                    if current_solutions >= 3:
                        continue
                    
                    # Check if pattern matches problem tags or title
                    pattern_keywords = {
                        'backtracking': ['backtrack', 'permutation', 'combination', 'queens', 'sudoku'],
                        'trie': ['prefix', 'word', 'search', 'autocomplete'],
                        'greedy': ['greedy', 'interval', 'activity', 'minimum', 'maximum'],
                        'divide_conquer': ['sort', 'search', 'merge', 'quick'],
                        'matrix': ['matrix', 'grid', 'spiral', '2d'],
                        'bit_manipulation': ['bit', 'xor', 'power', 'single']
                    }
                    
                    pattern = solution_data['pattern']
                    if pattern in pattern_keywords:
                        keywords = pattern_keywords[pattern]
                        title_lower = problem.title.lower()
                        tags_lower = [tag.lower() for tag in problem.algorithm_tags]
                        
                        if any(keyword in title_lower for keyword in keywords) or \
                           any(keyword in tag for tag in tags_lower for keyword in keywords):
                            suitable_problems.append(problem)
                
                # Add to first 2 suitable problems
                for problem in suitable_problems[:2]:
                    try:
                        # Generate unique ID
                        solution_id = f"{problem.id}_sol_{uuid.uuid4().hex[:8]}"
                        
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
                            algorithm_tags=[solution_data['approach'], pattern],
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
                            educational_value=88.0,
                            implementation_difficulty=4,
                            conceptual_difficulty=4,
                            created_at=datetime.now()
                        )
                        
                        db_session.add(solution)
                        db_session.flush()
                        added_count += 1
                        print(f"  ✅ Added {solution_data['approach']} solution for {problem.title}")
                        
                    except Exception as e:
                        print(f"  ❌ Error adding solution for {problem.title}: {e}")
                        db_session.rollback()
                        continue
            
            # Final commit
            db_session.commit()
            print(f"\n🎉 Successfully added {added_count} more solutions!")
            
            # Get final stats
            total_solutions = db_session.query(Solution).count()
            total_problems = db_session.query(Problem).count()
            avg_solutions = total_solutions / total_problems if total_problems > 0 else 0
            print(f"📊 Final stats: {total_solutions} solutions for {total_problems} problems")
            print(f"📊 Average solutions per problem: {avg_solutions:.1f}")
            
        except Exception as e:
            print(f"❌ Error during final addition: {e}")
            db_session.rollback()
        finally:
            db_session.close()

async def main():
    """Main entry point"""
    adder = FinalSolutionRound()
    await adder.add_final_solutions()

if __name__ == "__main__":
    asyncio.run(main())

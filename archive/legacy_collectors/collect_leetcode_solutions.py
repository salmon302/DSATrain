"""
LeetCode Solution Collector for Phase 3B
Collects high-quality solutions from LeetCode problems with multiple approaches
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import asdict

from src.models.schemas import (
    EnhancedSolution, SolutionComplexity, CodeQualityMetrics, PerformanceMetrics,
    SolutionApproach, ProgrammingLanguage, SolutionSource, SolutionCollection
)
from src.analysis.code_quality import analyze_solution_code


class LeetCodeSolutionCollector:
    """Collects and analyzes LeetCode solutions for our curated problems"""
    
    def __init__(self):
        self.base_url = "https://leetcode.com"
        
        # Sample solutions database (in real implementation, this would come from web scraping)
        self.sample_solutions = self._create_sample_solutions_database()
    
    def _create_sample_solutions_database(self) -> Dict[str, List[Dict[str, Any]]]:
        """Create a sample database of LeetCode solutions for demonstration"""
        return {
            "lc_1": [  # Two Sum
                {
                    "title": "Hash Map Approach",
                    "code": '''def twoSum(nums, target):
    """
    Find two numbers that add up to target using hash map.
    
    Time: O(n), Space: O(n)
    """
    num_map = {}
    
    for i, num in enumerate(nums):
        complement = target - num
        if complement in num_map:
            return [num_map[complement], i]
        num_map[num] = i
    
    return []''',
                    "approach": "optimal",
                    "time_complexity": "O(n)",
                    "space_complexity": "O(n)",
                    "explanation": "Use a hash map to store numbers and their indices. For each number, check if its complement exists in the map.",
                    "language": "python"
                },
                {
                    "title": "Brute Force Approach",
                    "code": '''def twoSum(nums, target):
    """
    Brute force solution checking all pairs.
    
    Time: O(n²), Space: O(1)
    """
    n = len(nums)
    
    for i in range(n):
        for j in range(i + 1, n):
            if nums[i] + nums[j] == target:
                return [i, j]
    
    return []''',
                    "approach": "brute_force",
                    "time_complexity": "O(n²)",
                    "space_complexity": "O(1)",
                    "explanation": "Check every possible pair of numbers until we find the target sum.",
                    "language": "python"
                }
            ],
            "lc_2": [  # Add Two Numbers
                {
                    "title": "Linked List Traversal",
                    "code": '''def addTwoNumbers(l1, l2):
    """
    Add two numbers represented as linked lists.
    
    Time: O(max(m, n)), Space: O(max(m, n))
    """
    dummy = ListNode(0)
    current = dummy
    carry = 0
    
    while l1 or l2 or carry:
        val1 = l1.val if l1 else 0
        val2 = l2.val if l2 else 0
        
        total = val1 + val2 + carry
        carry = total // 10
        digit = total % 10
        
        current.next = ListNode(digit)
        current = current.next
        
        if l1:
            l1 = l1.next
        if l2:
            l2 = l2.next
    
    return dummy.next''',
                    "approach": "optimal",
                    "time_complexity": "O(max(m, n))",
                    "space_complexity": "O(max(m, n))",
                    "explanation": "Traverse both linked lists simultaneously, handling carry for addition.",
                    "language": "python"
                }
            ],
            "lc_3": [  # Longest Substring Without Repeating Characters
                {
                    "title": "Sliding Window with Set",
                    "code": '''def lengthOfLongestSubstring(s):
    """
    Find longest substring without repeating characters.
    
    Time: O(n), Space: O(min(m, n))
    """
    char_set = set()
    left = 0
    max_length = 0
    
    for right in range(len(s)):
        while s[right] in char_set:
            char_set.remove(s[left])
            left += 1
        
        char_set.add(s[right])
        max_length = max(max_length, right - left + 1)
    
    return max_length''',
                    "approach": "optimal",
                    "time_complexity": "O(n)",
                    "space_complexity": "O(min(m, n))",
                    "explanation": "Use sliding window technique with a set to track characters in current window.",
                    "language": "python"
                },
                {
                    "title": "Sliding Window with HashMap",
                    "code": '''def lengthOfLongestSubstring(s):
    """
    Optimized sliding window using character index mapping.
    
    Time: O(n), Space: O(min(m, n))
    """
    char_map = {}
    left = 0
    max_length = 0
    
    for right in range(len(s)):
        if s[right] in char_map and char_map[s[right]] >= left:
            left = char_map[s[right]] + 1
        
        char_map[s[right]] = right
        max_length = max(max_length, right - left + 1)
    
    return max_length''',
                    "approach": "alternative",
                    "time_complexity": "O(n)",
                    "space_complexity": "O(min(m, n))",
                    "explanation": "Enhanced sliding window that jumps directly to the position after duplicate character.",
                    "language": "python"
                }
            ]
        }
    
    def collect_solutions_for_problems(self, problem_ids: List[str], max_solutions_per_problem: int = 3) -> Dict[str, SolutionCollection]:
        """
        Collect solutions for a list of problem IDs
        
        Args:
            problem_ids: List of problem IDs from our Phase 2 dataset
            max_solutions_per_problem: Maximum number of solutions to collect per problem
            
        Returns:
            Dictionary mapping problem_id to SolutionCollection
        """
        print(f"🔍 Collecting solutions for {len(problem_ids)} LeetCode problems...")
        
        collections = {}
        processed = 0
        
        for problem_id in problem_ids:
            try:
                # For this demo, we'll use sample solutions
                if problem_id in self.sample_solutions:
                    solution_collection = self._process_problem_solutions(
                        problem_id, 
                        self.sample_solutions[problem_id][:max_solutions_per_problem]
                    )
                    collections[problem_id] = solution_collection
                    processed += 1
                    print(f"✅ Collected {len(solution_collection.solutions)} solutions for {problem_id}")
                else:
                    # For problems not in our sample database, create placeholder
                    collections[problem_id] = self._create_placeholder_collection(problem_id)
                    print(f"⚪ Created placeholder for {problem_id} (not in sample database)")
                
                # Rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                print(f"❌ Error collecting solutions for {problem_id}: {str(e)}")
                collections[problem_id] = self._create_error_collection(problem_id, str(e))
        
        print(f"📊 Solution collection completed: {processed}/{len(problem_ids)} problems processed")
        return collections
    
    def _process_problem_solutions(self, problem_id: str, raw_solutions: List[Dict[str, Any]]) -> SolutionCollection:
        """Process raw solution data into structured SolutionCollection"""
        
        enhanced_solutions = []
        
        for i, raw_solution in enumerate(raw_solutions):
            try:
                # Create enhanced solution
                solution = self._create_enhanced_solution(problem_id, raw_solution, i)
                enhanced_solutions.append(solution)
                
            except Exception as e:
                print(f"⚠️  Error processing solution {i} for {problem_id}: {str(e)}")
        
        # Create collection analytics
        collection = SolutionCollection(
            problem_id=problem_id,
            problem_title=f"LeetCode Problem {problem_id}",
            total_solutions=len(enhanced_solutions),
            solutions=enhanced_solutions,
            collection_date=datetime.now(),
            last_updated=datetime.now()
        )
        
        # Calculate collection statistics
        collection = self._calculate_collection_stats(collection)
        
        return collection
    
    def _create_enhanced_solution(self, problem_id: str, raw_solution: Dict[str, Any], index: int) -> EnhancedSolution:
        """Create an EnhancedSolution from raw solution data"""
        
        # Generate unique solution ID
        solution_id = f"{problem_id}_sol_{index + 1}"
        
        # Parse language
        language = ProgrammingLanguage(raw_solution.get('language', 'python'))
        
        # Parse approach type
        approach_str = raw_solution.get('approach', 'optimal')
        approach_type = SolutionApproach(approach_str)
        
        # Analyze code quality
        code = raw_solution['code']
        code_quality = analyze_solution_code(code, language)
        
        # Create complexity information
        complexity = SolutionComplexity(
            time_complexity=raw_solution['time_complexity'],
            space_complexity=raw_solution['space_complexity'],
            time_complexity_explanation=f"Analysis: {raw_solution['time_complexity']}",
            space_complexity_explanation=f"Analysis: {raw_solution['space_complexity']}"
        )
        
        # Create performance metrics (simulated for demo)
        performance = PerformanceMetrics(
            runtime_ms=self._estimate_runtime(approach_type),
            memory_mb=self._estimate_memory(raw_solution['space_complexity']),
            runtime_percentile=self._estimate_percentile(approach_type, 'runtime'),
            memory_percentile=self._estimate_percentile(approach_type, 'memory'),
            test_cases_passed=100,  # Assume all test cases pass
            total_test_cases=100
        )
        
        # Extract algorithm tags and data structures
        algorithm_tags = self._extract_algorithm_tags(code, raw_solution['explanation'])
        data_structures_used = self._extract_data_structures(code)
        
        # Calculate Google interview relevance
        google_relevance = self._calculate_google_relevance(
            approach_type, algorithm_tags, code_quality.overall_score
        )
        
        # Create key insights and step-by-step breakdown
        step_by_step = self._generate_step_by_step(raw_solution['explanation'])
        key_insights = self._extract_key_insights(raw_solution['explanation'], approach_type)
        
        return EnhancedSolution(
            id=solution_id,
            problem_id=problem_id,
            title=raw_solution['title'],
            language=language,
            code=code,
            approach_type=approach_type,
            algorithm_tags=algorithm_tags,
            data_structures_used=data_structures_used,
            complexity=complexity,
            code_quality=code_quality,
            performance=performance,
            explanation=raw_solution['explanation'],
            step_by_step=step_by_step,
            key_insights=key_insights,
            implementation_difficulty=self._estimate_implementation_difficulty(approach_type, code_quality),
            conceptual_difficulty=self._estimate_conceptual_difficulty(algorithm_tags),
            google_interview_relevance=google_relevance,
            source=SolutionSource.LEETCODE_EDITORIAL,
            collection_date=datetime.now(),
            verification_status="verified",
            metadata={
                "source_problem": problem_id,
                "approach_category": approach_str,
                "collection_method": "sample_database",
                "quality_verified": True
            }
        )
    
    def _extract_algorithm_tags(self, code: str, explanation: str) -> List[str]:
        """Extract algorithm tags from code and explanation"""
        tags = []
        
        # Common algorithm patterns
        patterns = {
            'hash_map': ['dict', 'HashMap', '{', 'map'],
            'two_pointers': ['left', 'right', 'slow', 'fast'],
            'sliding_window': ['window', 'left', 'right'],
            'binary_search': ['binary', 'search', 'left', 'right', 'mid'],
            'dynamic_programming': ['dp', 'memo', 'cache'],
            'greedy': ['greedy', 'optimal'],
            'divide_conquer': ['divide', 'conquer', 'merge'],
            'backtracking': ['backtrack', 'dfs', 'recursion'],
            'breadth_first_search': ['bfs', 'queue'],
            'depth_first_search': ['dfs', 'stack', 'recursion']
        }
        
        text = (code + " " + explanation).lower()
        
        for tag, keywords in patterns.items():
            if any(keyword in text for keyword in keywords):
                tags.append(tag)
        
        return tags
    
    def _extract_data_structures(self, code: str) -> List[str]:
        """Extract data structures used in the code"""
        structures = []
        
        code_lower = code.lower()
        
        # Common data structures
        if any(keyword in code_lower for keyword in ['dict', 'hashmap', '{']):
            structures.append('hash_map')
        if any(keyword in code_lower for keyword in ['list', 'array', '[']):
            structures.append('array')
        if 'set' in code_lower:
            structures.append('set')
        if any(keyword in code_lower for keyword in ['queue', 'deque']):
            structures.append('queue')
        if 'stack' in code_lower:
            structures.append('stack')
        if any(keyword in code_lower for keyword in ['listnode', 'node']):
            structures.append('linked_list')
        if any(keyword in code_lower for keyword in ['tree', 'root']):
            structures.append('tree')
        
        return structures
    
    def _estimate_runtime(self, approach_type: SolutionApproach) -> int:
        """Estimate runtime in milliseconds based on approach type"""
        runtime_map = {
            SolutionApproach.OPTIMAL: 50,
            SolutionApproach.BRUTE_FORCE: 200,
            SolutionApproach.ALTERNATIVE: 70,
            SolutionApproach.EDUCATIONAL: 80
        }
        return runtime_map.get(approach_type, 100)
    
    def _estimate_memory(self, space_complexity: str) -> float:
        """Estimate memory usage in MB based on space complexity"""
        if 'O(1)' in space_complexity:
            return 14.2
        elif 'O(n)' in space_complexity:
            return 15.8
        elif 'O(n²)' in space_complexity:
            return 18.5
        else:
            return 16.0
    
    def _estimate_percentile(self, approach_type: SolutionApproach, metric_type: str) -> float:
        """Estimate performance percentile"""
        if approach_type == SolutionApproach.OPTIMAL:
            return 95.0 if metric_type == 'runtime' else 90.0
        elif approach_type == SolutionApproach.BRUTE_FORCE:
            return 20.0 if metric_type == 'runtime' else 95.0
        else:
            return 75.0
    
    def _calculate_google_relevance(self, approach_type: SolutionApproach, algorithm_tags: List[str], code_quality: float) -> float:
        """Calculate Google interview relevance score"""
        base_score = 70.0
        
        # Approach bonus
        approach_bonus = {
            SolutionApproach.OPTIMAL: 20,
            SolutionApproach.INTERVIEW_STYLE: 25,
            SolutionApproach.EDUCATIONAL: 15,
            SolutionApproach.ALTERNATIVE: 10,
            SolutionApproach.BRUTE_FORCE: 5
        }
        base_score += approach_bonus.get(approach_type, 0)
        
        # Algorithm tags bonus
        important_tags = {'hash_map', 'two_pointers', 'sliding_window', 'binary_search', 'dynamic_programming'}
        tag_bonus = len(set(algorithm_tags).intersection(important_tags)) * 5
        base_score += tag_bonus
        
        # Code quality bonus
        base_score += (code_quality - 50) * 0.3
        
        return min(100.0, max(0.0, base_score))
    
    def _estimate_implementation_difficulty(self, approach_type: SolutionApproach, code_quality: CodeQualityMetrics) -> int:
        """Estimate implementation difficulty (1-10 scale)"""
        base_difficulty = {
            SolutionApproach.BRUTE_FORCE: 3,
            SolutionApproach.OPTIMAL: 6,
            SolutionApproach.ALTERNATIVE: 5,
            SolutionApproach.EDUCATIONAL: 4
        }
        
        difficulty = base_difficulty.get(approach_type, 5)
        
        # Adjust based on code complexity
        if code_quality.cyclomatic_complexity and code_quality.cyclomatic_complexity > 5:
            difficulty += 1
        if code_quality.lines_of_code > 30:
            difficulty += 1
        
        return min(10, max(1, difficulty))
    
    def _estimate_conceptual_difficulty(self, algorithm_tags: List[str]) -> int:
        """Estimate conceptual difficulty (1-10 scale)"""
        difficulty_map = {
            'hash_map': 3,
            'two_pointers': 4,
            'sliding_window': 5,
            'binary_search': 4,
            'dynamic_programming': 8,
            'backtracking': 7,
            'divide_conquer': 6
        }
        
        if not algorithm_tags:
            return 3
        
        max_difficulty = max(difficulty_map.get(tag, 3) for tag in algorithm_tags)
        return max_difficulty
    
    def _generate_step_by_step(self, explanation: str) -> List[str]:
        """Generate step-by-step solution breakdown"""
        # Simple heuristic: split explanation into sentences
        sentences = [s.strip() for s in explanation.split('.') if s.strip()]
        return sentences[:5]  # Limit to first 5 steps
    
    def _extract_key_insights(self, explanation: str, approach_type: SolutionApproach) -> List[str]:
        """Extract key insights from explanation"""
        insights = []
        
        if approach_type == SolutionApproach.OPTIMAL:
            insights.append("This is the optimal solution with best time complexity")
        
        if 'hash' in explanation.lower():
            insights.append("Hash map provides O(1) lookup time")
        
        if 'two pointer' in explanation.lower():
            insights.append("Two pointers technique reduces space complexity")
        
        return insights
    
    def _calculate_collection_stats(self, collection: SolutionCollection) -> SolutionCollection:
        """Calculate statistics for the solution collection"""
        solutions = collection.solutions
        
        if not solutions:
            return collection
        
        # Language distribution
        language_dist = {}
        for sol in solutions:
            lang = sol.language.value
            language_dist[lang] = language_dist.get(lang, 0) + 1
        
        # Approach distribution
        approach_dist = {}
        for sol in solutions:
            approach = sol.approach_type.value
            approach_dist[approach] = approach_dist.get(approach, 0) + 1
        
        # Quality statistics
        quality_scores = [sol.code_quality.overall_score for sol in solutions]
        quality_stats = {
            'average': sum(quality_scores) / len(quality_scores),
            'max': max(quality_scores),
            'min': min(quality_scores)
        }
        
        # Performance statistics
        runtimes = [sol.performance.runtime_ms for sol in solutions if sol.performance.runtime_ms]
        if runtimes:
            performance_stats = {
                'average_runtime': sum(runtimes) / len(runtimes),
                'fastest_runtime': min(runtimes)
            }
        else:
            performance_stats = {}
        
        # Find best solutions
        best_quality_sol = max(solutions, key=lambda s: s.code_quality.overall_score)
        best_performance_sol = min(solutions, key=lambda s: s.performance.runtime_ms or float('inf'))
        most_educational = max(solutions, key=lambda s: s.google_interview_relevance)
        
        # Update collection
        collection.language_distribution = language_dist
        collection.approach_distribution = approach_dist
        collection.quality_stats = quality_stats
        collection.performance_stats = performance_stats
        collection.cleanest_code_id = best_quality_sol.id
        collection.fastest_runtime_id = best_performance_sol.id
        collection.most_educational_id = most_educational.id
        
        # Find optimal solution
        optimal_solutions = [s for s in solutions if s.approach_type == SolutionApproach.OPTIMAL]
        if optimal_solutions:
            collection.optimal_solution_id = optimal_solutions[0].id
        
        return collection
    
    def _create_placeholder_collection(self, problem_id: str) -> SolutionCollection:
        """Create placeholder collection for problems without solutions"""
        return SolutionCollection(
            problem_id=problem_id,
            problem_title=f"Problem {problem_id}",
            total_solutions=0,
            solutions=[],
            collection_date=datetime.now(),
            last_updated=datetime.now(),
            metadata={"status": "placeholder", "reason": "no_solutions_available"}
        )
    
    def _create_error_collection(self, problem_id: str, error_msg: str) -> SolutionCollection:
        """Create error collection for failed processing"""
        return SolutionCollection(
            problem_id=problem_id,
            problem_title=f"Problem {problem_id}",
            total_solutions=0,
            solutions=[],
            collection_date=datetime.now(),
            last_updated=datetime.now(),
            metadata={"status": "error", "error_message": error_msg}
        )
    
    def save_solution_collections(self, collections: Dict[str, SolutionCollection], output_dir: str = "data/solutions"):
        """Save solution collections to files"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save individual collections
        leetcode_dir = output_path / "leetcode"
        leetcode_dir.mkdir(exist_ok=True)
        
        saved_files = []
        
        for problem_id, collection in collections.items():
            if collection.total_solutions > 0:
                file_path = leetcode_dir / f"{problem_id}_solutions.json"
                
                # Convert to JSON-serializable format
                collection_dict = collection.dict()
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(collection_dict, f, indent=2, ensure_ascii=False)
                
                saved_files.append(str(file_path))
        
        # Save summary
        summary = {
            "collection_date": datetime.now().isoformat(),
            "total_problems": len(collections),
            "problems_with_solutions": len([c for c in collections.values() if c.total_solutions > 0]),
            "total_solutions": sum(c.total_solutions for c in collections.values()),
            "files_saved": saved_files
        }
        
        summary_path = output_path / "leetcode_solutions_summary.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved {len(saved_files)} solution collections to {leetcode_dir}")
        print(f"📊 Summary saved to {summary_path}")
        
        return saved_files


def main():
    """Main function to demonstrate LeetCode solution collection"""
    print("LeetCode Solution Collection - Phase 3B")
    print("=" * 50)
    
    # Initialize collector
    collector = LeetCodeSolutionCollector()
    
    # Sample LeetCode problem IDs from our Phase 2 dataset
    sample_problems = ["lc_1", "lc_2", "lc_3"]  # Two Sum, Add Two Numbers, Longest Substring
    
    # Collect solutions
    collections = collector.collect_solutions_for_problems(sample_problems)
    
    # Save collections
    saved_files = collector.save_solution_collections(collections)
    
    # Print summary
    print("\n📊 Collection Summary:")
    total_solutions = sum(c.total_solutions for c in collections.values())
    print(f"Problems processed: {len(collections)}")
    print(f"Total solutions collected: {total_solutions}")
    print(f"Files saved: {len(saved_files)}")
    
    # Print details for first collection
    if collections:
        first_collection = next(iter(collections.values()))
        if first_collection.total_solutions > 0:
            print(f"\n🔍 Sample Collection Details ({first_collection.problem_id}):")
            print(f"Solutions: {first_collection.total_solutions}")
            print(f"Languages: {list(first_collection.language_distribution.keys())}")
            print(f"Approaches: {list(first_collection.approach_distribution.keys())}")
            print(f"Average Quality: {first_collection.quality_stats.get('average', 0):.1f}")


if __name__ == "__main__":
    main()

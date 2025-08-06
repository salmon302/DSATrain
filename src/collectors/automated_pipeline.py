"""
Phase 4 Automated Collection Pipeline
Scalable, database-integrated data collection system
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Set
from pathlib import Path
import hashlib
import time
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import traceback

# Database imports
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.models.database import DatabaseConfig, Problem, Solution, SystemMetrics
from src.models.schemas import Difficulty, SolutionAnalytics

# Analysis imports
from src.analysis.code_quality import PythonCodeAnalyzer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/collection_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class CollectionConfig:
    """Configuration for collection pipeline"""
    platforms: List[str]
    max_problems_per_platform: int = 1000
    max_solutions_per_problem: int = 10
    collection_interval_hours: int = 24
    quality_threshold: float = 70.0
    google_interview_relevance_threshold: float = 60.0
    concurrent_requests: int = 10
    request_delay_seconds: float = 1.0
    retry_attempts: int = 3
    backup_directory: str = "data/backups"


class PlatformCollector:
    """Base class for platform-specific collectors"""
    
    def __init__(self, platform_name: str, session: aiohttp.ClientSession, db_session):
        self.platform_name = platform_name
        self.session = session
        self.db_session = db_session
        self.code_analyzer = PythonCodeAnalyzer()
        
    async def collect_problems(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """Collect problems from platform (to be implemented by subclasses)"""
        raise NotImplementedError
        
    async def collect_solutions(self, problem_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Collect solutions for a problem (to be implemented by subclasses)"""
        raise NotImplementedError
        
    def calculate_google_interview_relevance(self, problem_data: Dict[str, Any]) -> float:
        """Calculate Google interview relevance score"""
        score = 0.0
        
        # Algorithm type relevance
        algorithm_tags = problem_data.get('algorithm_tags', [])
        high_relevance_algorithms = [
            'dynamic_programming', 'graph_algorithms', 'tree_algorithms',
            'binary_search', 'two_pointers', 'sliding_window', 'backtracking',
            'divide_and_conquer', 'greedy_algorithms', 'sorting_searching'
        ]
        
        for tag in algorithm_tags:
            if tag in high_relevance_algorithms:
                score += 15.0
        
        # Difficulty relevance (Medium and Hard are more Google-like)
        difficulty = problem_data.get('difficulty', '').lower()
        if difficulty == 'medium':
            score += 20.0
        elif difficulty == 'hard':
            score += 25.0
        elif difficulty == 'easy':
            score += 10.0
        
        # Company tags
        companies = problem_data.get('companies', [])
        if 'google' in [c.lower() for c in companies]:
            score += 30.0
        
        # Quality indicators
        if problem_data.get('quality_score', 0) > 80.0:
            score += 10.0
            
        return min(score, 100.0)


class LeetCodeCollector(PlatformCollector):
    """Enhanced LeetCode collector for Phase 4"""
    
    def __init__(self, session: aiohttp.ClientSession, db_session):
        super().__init__("leetcode", session, db_session)
        self.base_url = "https://leetcode.com/api"
        
    async def collect_problems(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """Collect LeetCode problems"""
        problems = []
        
        try:
            # Generate sample LeetCode problems for demonstration
            sample_problems = [
                {
                    "id": "leetcode_two_sum",
                    "platform_id": "1",
                    "title": "Two Sum",
                    "difficulty": "Easy",
                    "description": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
                    "algorithm_tags": ["hash_table", "array"],
                    "data_structures": ["array", "hash_map"],
                    "constraints": {"time_limit": 1000, "memory_limit": 256},
                    "companies": ["Google", "Amazon", "Facebook"],
                    "acceptance_rate": 49.5,
                    "frequency_score": 95.0
                },
                {
                    "id": "leetcode_median_sorted_arrays",
                    "platform_id": "4",
                    "title": "Median of Two Sorted Arrays",
                    "difficulty": "Hard",
                    "description": "Given two sorted arrays nums1 and nums2 of size m and n respectively, return the median of the two sorted arrays.",
                    "algorithm_tags": ["binary_search", "divide_and_conquer"],
                    "data_structures": ["array"],
                    "constraints": {"time_limit": 2000, "memory_limit": 256},
                    "companies": ["Google", "Microsoft", "Apple"],
                    "acceptance_rate": 35.2,
                    "frequency_score": 85.0
                },
                {
                    "id": "leetcode_longest_substring",
                    "platform_id": "3",
                    "title": "Longest Substring Without Repeating Characters",
                    "difficulty": "Medium",
                    "description": "Given a string s, find the length of the longest substring without repeating characters.",
                    "algorithm_tags": ["sliding_window", "hash_table"],
                    "data_structures": ["hash_map", "string"],
                    "constraints": {"time_limit": 1000, "memory_limit": 256},
                    "companies": ["Google", "Amazon", "Bloomberg"],
                    "acceptance_rate": 33.8,
                    "frequency_score": 90.0
                },
                {
                    "id": "leetcode_valid_parentheses",
                    "platform_id": "20",
                    "title": "Valid Parentheses",
                    "difficulty": "Easy",
                    "description": "Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.",
                    "algorithm_tags": ["stack"],
                    "data_structures": ["stack"],
                    "constraints": {"time_limit": 1000, "memory_limit": 256},
                    "companies": ["Google", "Facebook", "Microsoft"],
                    "acceptance_rate": 40.7,
                    "frequency_score": 88.0
                },
                {
                    "id": "leetcode_merge_k_sorted_lists",
                    "platform_id": "23",
                    "title": "Merge k Sorted Lists",
                    "difficulty": "Hard",
                    "description": "You are given an array of k linked-lists lists, each linked-list is sorted in ascending order.",
                    "algorithm_tags": ["heap", "divide_and_conquer", "linked_list"],
                    "data_structures": ["linked_list", "heap"],
                    "constraints": {"time_limit": 2000, "memory_limit": 256},
                    "companies": ["Google", "Amazon", "Facebook"],
                    "acceptance_rate": 47.1,
                    "frequency_score": 82.0
                }
            ]
            
            for problem_data in sample_problems[:limit]:
                # Calculate quality and relevance scores
                problem_data['quality_score'] = self._calculate_quality_score(problem_data)
                problem_data['google_interview_relevance'] = self.calculate_google_interview_relevance(problem_data)
                problem_data['platform'] = self.platform_name
                problem_data['collected_at'] = datetime.now()
                
                problems.append(problem_data)
                
                # Simulate API delay
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Error collecting LeetCode problems: {e}")
            
        return problems
    
    def _calculate_quality_score(self, problem_data: Dict[str, Any]) -> float:
        """Calculate problem quality score"""
        score = 50.0  # Base score
        
        # Company backing
        if problem_data.get('companies'):
            score += 20.0
            
        # Acceptance rate (balanced is better)
        acceptance_rate = problem_data.get('acceptance_rate', 50.0)
        if 30.0 <= acceptance_rate <= 60.0:
            score += 15.0
        elif 20.0 <= acceptance_rate <= 70.0:
            score += 10.0
            
        # Algorithm diversity
        if len(problem_data.get('algorithm_tags', [])) >= 2:
            score += 15.0
            
        return min(score, 100.0)
    
    async def collect_solutions(self, problem_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Collect solutions for LeetCode problem"""
        solutions = []
        
        # Sample solutions for demonstration
        sample_solutions = {
            "leetcode_two_sum": [
                {
                    "code": """def twoSum(nums, target):
    # Hash table approach - O(n) time, O(n) space
    num_map = {}
    
    for i, num in enumerate(nums):
        complement = target - num
        if complement in num_map:
            return [num_map[complement], i]
        num_map[num] = i
    
    return []""",
                    "approach_type": "hash_table",
                    "time_complexity": "O(n)",
                    "space_complexity": "O(n)",
                    "explanation": "Use hash table to store numbers and their indices for O(1) lookup"
                },
                {
                    "code": """def twoSum(nums, target):
    # Brute force approach - O(n²) time, O(1) space
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    
    return []""",
                    "approach_type": "brute_force",
                    "time_complexity": "O(n²)",
                    "space_complexity": "O(1)",
                    "explanation": "Check all pairs to find the target sum"
                }
            ]
        }
        
        if problem_id in sample_solutions:
            for i, solution_data in enumerate(sample_solutions[problem_id][:limit]):
                solution_id = f"{problem_id}_solution_{i+1}"
                
                # Analyze code quality
                quality_metrics = self.code_analyzer.analyze_solution_code(solution_data['code'])
                
                solution = {
                    'id': solution_id,
                    'problem_id': problem_id,
                    'code': solution_data['code'],
                    'language': 'python',
                    'approach_type': solution_data['approach_type'],
                    'algorithm_tags': [solution_data['approach_type']],
                    'time_complexity': solution_data['time_complexity'],
                    'space_complexity': solution_data['space_complexity'],
                    'explanation': solution_data['explanation'],
                    'overall_quality_score': quality_metrics.overall_score,
                    'readability_score': quality_metrics.readability_score,
                    'documentation_score': quality_metrics.documentation_score,
                    'efficiency_score': quality_metrics.efficiency_score,
                    'maintainability_score': quality_metrics.maintainability_score,
                    'style_score': quality_metrics.style_score,
                    'google_interview_relevance': 85.0,
                    'educational_value': 80.0,
                    'implementation_difficulty': 3,
                    'conceptual_difficulty': 4
                }
                
                solutions.append(solution)
        
        return solutions


class CodeforceCollector(PlatformCollector):
    """Enhanced Codeforces collector for Phase 4"""
    
    def __init__(self, session: aiohttp.ClientSession, db_session):
        super().__init__("codeforces", session, db_session)
        self.base_url = "https://codeforces.com/api"
        
    async def collect_problems(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """Collect Codeforces problems"""
        problems = []
        
        try:
            # Generate sample Codeforces problems
            sample_problems = [
                {
                    "id": "codeforces_1A",
                    "platform_id": "1A",
                    "title": "Theatre Square",
                    "difficulty": "Easy",
                    "description": "Calculate minimum number of square flagstones needed to cover a rectangular theatre square.",
                    "algorithm_tags": ["math", "greedy"],
                    "data_structures": ["math"],
                    "constraints": {"time_limit": 1000, "memory_limit": 256},
                    "category": "implementation"
                },
                {
                    "id": "codeforces_1200C",
                    "platform_id": "1200C",
                    "title": "Round Corridor",
                    "difficulty": "Medium",
                    "description": "Determine if you can move from one sector to another in a circular corridor.",
                    "algorithm_tags": ["math", "number_theory"],
                    "data_structures": ["math"],
                    "constraints": {"time_limit": 1000, "memory_limit": 256},
                    "category": "math"
                },
                {
                    "id": "codeforces_1400E",
                    "platform_id": "1400E",
                    "title": "Clear the Multiset",
                    "difficulty": "Hard",
                    "description": "Find minimum operations to clear a multiset using two types of operations.",
                    "algorithm_tags": ["dynamic_programming", "greedy"],
                    "data_structures": ["array"],
                    "constraints": {"time_limit": 2000, "memory_limit": 256},
                    "category": "dp"
                }
            ]
            
            for problem_data in sample_problems[:limit]:
                problem_data['quality_score'] = self._calculate_quality_score(problem_data)
                problem_data['google_interview_relevance'] = self.calculate_google_interview_relevance(problem_data)
                problem_data['platform'] = self.platform_name
                problem_data['collected_at'] = datetime.now()
                
                problems.append(problem_data)
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Error collecting Codeforces problems: {e}")
            
        return problems
    
    def _calculate_quality_score(self, problem_data: Dict[str, Any]) -> float:
        """Calculate problem quality score"""
        score = 60.0  # Base score for Codeforces (generally high quality)
        
        # Category bonus
        category = problem_data.get('category', '')
        if category in ['dp', 'graph', 'math']:
            score += 20.0
        elif category in ['implementation', 'greedy']:
            score += 15.0
            
        # Algorithm diversity
        if len(problem_data.get('algorithm_tags', [])) >= 2:
            score += 20.0
            
        return min(score, 100.0)


class AutomatedCollectionPipeline:
    """Main collection pipeline orchestrator"""
    
    def __init__(self, config: CollectionConfig):
        self.config = config
        self.db_config = DatabaseConfig()
        self.session_factory = self.db_config.SessionLocal
        
        # Ensure directories exist
        Path(config.backup_directory).mkdir(parents=True, exist_ok=True)
        Path("logs").mkdir(exist_ok=True)
        
    async def run_collection_cycle(self):
        """Run a complete collection cycle"""
        logger.info("🚀 Starting automated collection cycle")
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                db_session = self.session_factory()
                
                try:
                    # Initialize collectors
                    collectors = {}
                    if "leetcode" in self.config.platforms:
                        collectors["leetcode"] = LeetCodeCollector(session, db_session)
                    if "codeforces" in self.config.platforms:
                        collectors["codeforces"] = CodeforceCollector(session, db_session)
                    
                    # Collect problems from all platforms
                    all_problems = []
                    for platform, collector in collectors.items():
                        logger.info(f"📊 Collecting problems from {platform}")
                        problems = await collector.collect_problems(self.config.max_problems_per_platform)
                        all_problems.extend(problems)
                        logger.info(f"✅ Collected {len(problems)} problems from {platform}")
                    
                    # Store problems in database
                    stored_problems = await self._store_problems(db_session, all_problems)
                    logger.info(f"💾 Stored {stored_problems} problems in database")
                    
                    # Collect solutions for high-quality problems
                    total_solutions = 0
                    high_quality_problems = db_session.query(Problem).filter(
                        Problem.quality_score >= self.config.quality_threshold
                    ).limit(50).all()  # Limit for demo
                    
                    for problem in high_quality_problems:
                        platform_collector = collectors.get(problem.platform)
                        if platform_collector:
                            solutions = await platform_collector.collect_solutions(
                                problem.id, self.config.max_solutions_per_problem
                            )
                            stored_solutions = await self._store_solutions(db_session, solutions)
                            total_solutions += stored_solutions
                    
                    logger.info(f"💾 Stored {total_solutions} solutions in database")
                    
                    # Record system metrics
                    await self._record_system_metrics(db_session, {
                        'collection_cycle_duration_seconds': time.time() - start_time,
                        'problems_collected': len(all_problems),
                        'problems_stored': stored_problems,
                        'solutions_stored': total_solutions,
                        'platforms_processed': len(collectors)
                    })
                    
                    # Create backup
                    await self._create_backup(db_session)
                    
                    logger.info("✅ Collection cycle completed successfully")
                    
                finally:
                    db_session.close()
                    
        except Exception as e:
            logger.error(f"❌ Collection cycle failed: {e}")
            logger.error(traceback.format_exc())
    
    async def _store_problems(self, db_session, problems: List[Dict[str, Any]]) -> int:
        """Store problems in database"""
        stored_count = 0
        
        for problem_data in problems:
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
                    category=problem_data.get('category'),
                    description=problem_data.get('description'),
                    constraints=problem_data.get('constraints'),
                    algorithm_tags=problem_data['algorithm_tags'],
                    data_structures=problem_data.get('data_structures'),
                    google_interview_relevance=problem_data['google_interview_relevance'],
                    quality_score=problem_data['quality_score'],
                    acceptance_rate=problem_data.get('acceptance_rate'),
                    frequency_score=problem_data.get('frequency_score'),
                    companies=problem_data.get('companies'),
                    collected_at=problem_data['collected_at']
                )
                
                db_session.add(problem)
                stored_count += 1
                
            except IntegrityError:
                db_session.rollback()
                continue
            except Exception as e:
                logger.error(f"Error storing problem {problem_data.get('id')}: {e}")
                db_session.rollback()
                continue
        
        try:
            db_session.commit()
        except Exception as e:
            logger.error(f"Error committing problems: {e}")
            db_session.rollback()
        
        return stored_count
    
    async def _store_solutions(self, db_session, solutions: List[Dict[str, Any]]) -> int:
        """Store solutions in database"""
        stored_count = 0
        
        for solution_data in solutions:
            try:
                # Check if solution already exists
                existing = db_session.query(Solution).filter_by(id=solution_data['id']).first()
                if existing:
                    continue
                
                # Create solution instance
                solution = Solution(
                    id=solution_data['id'],
                    problem_id=solution_data['problem_id'],
                    code=solution_data['code'],
                    language=solution_data['language'],
                    approach_type=solution_data['approach_type'],
                    algorithm_tags=solution_data['algorithm_tags'],
                    time_complexity=solution_data['time_complexity'],
                    space_complexity=solution_data['space_complexity'],
                    overall_quality_score=solution_data['overall_quality_score'],
                    readability_score=solution_data['readability_score'],
                    documentation_score=solution_data['documentation_score'],
                    efficiency_score=solution_data['efficiency_score'],
                    maintainability_score=solution_data['maintainability_score'],
                    style_score=solution_data['style_score'],
                    explanation=solution_data.get('explanation'),
                    google_interview_relevance=solution_data['google_interview_relevance'],
                    educational_value=solution_data['educational_value'],
                    implementation_difficulty=solution_data['implementation_difficulty'],
                    conceptual_difficulty=solution_data['conceptual_difficulty']
                )
                
                db_session.add(solution)
                stored_count += 1
                
            except IntegrityError:
                db_session.rollback()
                continue
            except Exception as e:
                logger.error(f"Error storing solution {solution_data.get('id')}: {e}")
                db_session.rollback()
                continue
        
        try:
            db_session.commit()
        except Exception as e:
            logger.error(f"Error committing solutions: {e}")
            db_session.rollback()
        
        return stored_count
    
    async def _record_system_metrics(self, db_session, metrics: Dict[str, float]):
        """Record system performance metrics"""
        for metric_name, value in metrics.items():
            try:
                metric = SystemMetrics(
                    metric_name=metric_name,
                    metric_value=value,
                    metric_category='collection_performance',
                    recorded_at=datetime.now()
                )
                db_session.add(metric)
            except Exception as e:
                logger.error(f"Error recording metric {metric_name}: {e}")
        
        try:
            db_session.commit()
        except Exception as e:
            logger.error(f"Error committing metrics: {e}")
            db_session.rollback()
    
    async def _create_backup(self, db_session):
        """Create database backup"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = Path(self.config.backup_directory) / f"database_backup_{timestamp}.json"
            
            # Export key data for backup
            problems = db_session.query(Problem).all()
            solutions = db_session.query(Solution).all()
            
            backup_data = {
                'timestamp': timestamp,
                'problems': [p.to_dict() for p in problems],
                'solutions': [s.to_dict() for s in solutions],
                'stats': {
                    'total_problems': len(problems),
                    'total_solutions': len(solutions)
                }
            }
            
            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2, default=str)
                
            logger.info(f"📦 Database backup created: {backup_file}")
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")


async def main():
    """Main entry point for collection pipeline"""
    config = CollectionConfig(
        platforms=["leetcode", "codeforces"],
        max_problems_per_platform=10,  # Small number for demo
        max_solutions_per_problem=2,
        quality_threshold=70.0,
        google_interview_relevance_threshold=60.0
    )
    
    pipeline = AutomatedCollectionPipeline(config)
    await pipeline.run_collection_cycle()


if __name__ == "__main__":
    asyncio.run(main())

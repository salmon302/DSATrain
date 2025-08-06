"""
Enhanced Difficulty Analyzer for Skill Tree System
Analyzes existing problems and assigns granular difficulty metrics
"""

from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from src.models.database import Problem, DatabaseConfig
import json
import logging
from dataclasses import dataclass
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DifficultyPattern(Enum):
    """Patterns for difficulty classification"""
    IMPLEMENTATION_HEAVY = "implementation_heavy"
    CONCEPTUAL_HEAVY = "conceptual_heavy"
    ALGORITHM_SPECIFIC = "algorithm_specific"
    DATA_STRUCTURE_FOCUSED = "data_structure_focused"
    OPTIMIZATION_REQUIRED = "optimization_required"
    EDGE_CASE_COMPLEX = "edge_case_complex"


@dataclass
class DifficultyMetrics:
    """Enhanced difficulty metrics for a problem"""
    sub_difficulty_level: int  # 1-5 within Easy/Medium/Hard
    conceptual_difficulty: int  # 0-100 conceptual understanding required
    implementation_complexity: int  # 0-100 implementation difficulty
    prerequisite_skills: List[str]  # Required skills
    difficulty_pattern: str  # Primary difficulty pattern
    confidence_score: float  # How confident we are in the assessment


class EnhancedDifficultyAnalyzer:
    """Analyzes and assigns enhanced difficulty metrics to problems"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        
        # Skill complexity mapping (how hard each skill typically is)
        self.skill_complexity = {
            "arrays": 20, "strings": 25, "hash_tables": 30, "two_pointers": 40,
            "sliding_window": 45, "binary_search": 50, "trees": 55, "graphs": 70,
            "dynamic_programming": 80, "backtracking": 65, "greedy": 45,
            "bit_manipulation": 60, "mathematics": 35, "sorting": 30,
            "divide_and_conquer": 70, "trie": 60, "union_find": 65,
            "segment_tree": 85, "fenwick_tree": 80, "graph_algorithms": 75
        }
        
        # Algorithm complexity indicators
        self.complex_algorithms = {
            "dp", "dynamic_programming", "backtracking", "graph", "dfs", "bfs",
            "dijkstra", "floyd_warshall", "segment_tree", "fenwick_tree",
            "union_find", "kmp", "rabin_karp", "manacher", "suffix_array"
        }
        
        # Easy indicators
        self.easy_indicators = {
            "simulation", "implementation", "brute_force", "array_manipulation",
            "string_manipulation", "basic_math", "linear_search"
        }
    
    def analyze_problem_difficulty(self, problem: Problem) -> DifficultyMetrics:
        """Analyze a single problem and return enhanced difficulty metrics"""
        
        # Get algorithm tags for analysis
        algorithm_tags = problem.algorithm_tags or []
        
        # Calculate base metrics
        conceptual_score = self._calculate_conceptual_difficulty(problem, algorithm_tags)
        implementation_score = self._calculate_implementation_complexity(problem, algorithm_tags)
        sub_level = self._calculate_sub_difficulty_level(problem, conceptual_score, implementation_score)
        prerequisites = self._determine_prerequisite_skills(algorithm_tags)
        pattern = self._identify_difficulty_pattern(problem, algorithm_tags)
        confidence = self._calculate_confidence_score(problem, algorithm_tags)
        
        return DifficultyMetrics(
            sub_difficulty_level=sub_level,
            conceptual_difficulty=conceptual_score,
            implementation_complexity=implementation_score,
            prerequisite_skills=prerequisites,
            difficulty_pattern=pattern,
            confidence_score=confidence
        )
    
    def _calculate_conceptual_difficulty(self, problem: Problem, tags: List[str]) -> int:
        """Calculate conceptual difficulty (0-100)"""
        base_score = 30  # Base conceptual requirement
        
        # Algorithm complexity contribution
        for tag in tags:
            if tag.lower() in self.complex_algorithms:
                base_score += 25
            elif tag.lower() in self.easy_indicators:
                base_score -= 10
        
        # Adjust based on problem difficulty
        if problem.difficulty == "Easy":
            base_score = min(base_score, 50)
        elif problem.difficulty == "Medium":
            base_score = max(30, min(base_score + 20, 80))
        elif problem.difficulty == "Hard":
            base_score = max(50, base_score + 30)
        
        # Google relevance factor (higher relevance often means more conceptual depth)
        if problem.google_interview_relevance:
            relevance_boost = int(problem.google_interview_relevance * 0.3)
            base_score += relevance_boost
        
        return min(100, max(0, base_score))
    
    def _calculate_implementation_complexity(self, problem: Problem, tags: List[str]) -> int:
        """Calculate implementation complexity (0-100)"""
        base_score = 25  # Base implementation requirement
        
        # Count of different concepts (more concepts = more implementation complexity)
        concept_count = len(set(tags) & set(self.skill_complexity.keys()))
        base_score += concept_count * 8
        
        # Specific algorithm complexity
        for tag in tags:
            if tag.lower() in ["implementation", "simulation"]:
                base_score += 20
            elif tag.lower() in ["data_structures", "segment_tree", "fenwick_tree"]:
                base_score += 30
            elif tag.lower() in self.easy_indicators:
                base_score -= 5
        
        # Adjust based on problem difficulty
        if problem.difficulty == "Easy":
            base_score = min(base_score, 45)
        elif problem.difficulty == "Medium":
            base_score = max(25, min(base_score + 15, 75))
        elif problem.difficulty == "Hard":
            base_score = max(40, base_score + 25)
        
        # Quality score factor (higher quality often means cleaner implementation)
        if problem.quality_score and problem.quality_score > 90:
            base_score -= 5  # High quality problems are often cleaner to implement
        
        return min(100, max(0, base_score))
    
    def _calculate_sub_difficulty_level(self, problem: Problem, conceptual: int, implementation: int) -> int:
        """Calculate sub-difficulty level (1-5) within the main difficulty category"""
        
        # Combined complexity score
        combined_score = (conceptual + implementation) / 2
        
        # Map to 1-5 scale based on main difficulty
        if problem.difficulty == "Easy":
            if combined_score <= 25: return 1
            elif combined_score <= 35: return 2
            elif combined_score <= 45: return 3
            elif combined_score <= 55: return 4
            else: return 5
        elif problem.difficulty == "Medium":
            if combined_score <= 40: return 1
            elif combined_score <= 50: return 2
            elif combined_score <= 60: return 3
            elif combined_score <= 70: return 4
            else: return 5
        else:  # Hard
            if combined_score <= 55: return 1
            elif combined_score <= 65: return 2
            elif combined_score <= 75: return 3
            elif combined_score <= 85: return 4
            else: return 5
    
    def _determine_prerequisite_skills(self, tags: List[str]) -> List[str]:
        """Determine prerequisite skills based on algorithm tags"""
        prerequisites = set()
        
        # Skill dependency mapping
        dependencies = {
            "dynamic_programming": ["arrays", "recursion"],
            "graphs": ["trees", "dfs_bfs"],
            "backtracking": ["recursion", "trees"],
            "binary_search": ["arrays", "sorting"],
            "segment_tree": ["trees", "binary_search"],
            "union_find": ["trees", "graphs"],
            "trie": ["trees", "strings"],
            "sliding_window": ["two_pointers", "arrays"],
            "kmp": ["strings", "pattern_matching"]
        }
        
        for tag in tags:
            if tag.lower() in dependencies:
                prerequisites.update(dependencies[tag.lower()])
        
        return list(prerequisites)
    
    def _identify_difficulty_pattern(self, problem: Problem, tags: List[str]) -> str:
        """Identify the primary difficulty pattern"""
        
        if any(tag in ["implementation", "simulation"] for tag in tags):
            return DifficultyPattern.IMPLEMENTATION_HEAVY.value
        elif any(tag in ["dp", "dynamic_programming", "graphs"] for tag in tags):
            return DifficultyPattern.CONCEPTUAL_HEAVY.value
        elif any(tag in ["segment_tree", "fenwick_tree", "union_find"] for tag in tags):
            return DifficultyPattern.DATA_STRUCTURE_FOCUSED.value
        elif any(tag in ["optimization", "greedy"] for tag in tags):
            return DifficultyPattern.OPTIMIZATION_REQUIRED.value
        elif len(tags) > 4:
            return DifficultyPattern.EDGE_CASE_COMPLEX.value
        else:
            return DifficultyPattern.ALGORITHM_SPECIFIC.value
    
    def _calculate_confidence_score(self, problem: Problem, tags: List[str]) -> float:
        """Calculate confidence in difficulty assessment (0-1)"""
        confidence = 0.7  # Base confidence
        
        # More tags = higher confidence
        if len(tags) >= 3:
            confidence += 0.1
        if len(tags) >= 5:
            confidence += 0.1
        
        # Quality score boosts confidence
        if problem.quality_score and problem.quality_score > 95:
            confidence += 0.1
        
        # Google relevance score boosts confidence
        if problem.google_interview_relevance and problem.google_interview_relevance > 80:
            confidence += 0.05
        
        return min(1.0, confidence)
    
    def process_all_problems(self, batch_size: int = 100) -> Dict[str, int]:
        """Process all problems in the database with enhanced difficulty analysis"""
        
        logger.info("🔍 Starting enhanced difficulty analysis for all problems...")
        
        total_problems = self.db.query(Problem).count()
        processed = 0
        updated = 0
        
        # Process in batches
        offset = 0
        while offset < total_problems:
            batch = self.db.query(Problem).offset(offset).limit(batch_size).all()
            
            for problem in batch:
                try:
                    # Analyze difficulty
                    metrics = self.analyze_problem_difficulty(problem)
                    
                    # Update problem with new metrics
                    problem.sub_difficulty_level = metrics.sub_difficulty_level
                    problem.conceptual_difficulty = metrics.conceptual_difficulty
                    problem.implementation_complexity = metrics.implementation_complexity
                    problem.prerequisite_skills = metrics.prerequisite_skills
                    problem.skill_tree_position = {
                        "difficulty_pattern": metrics.difficulty_pattern,
                        "confidence_score": metrics.confidence_score,
                        "analyzed_at": "2025-07-31T10:00:00Z"
                    }
                    
                    updated += 1
                    
                except Exception as e:
                    logger.error(f"❌ Error processing problem {problem.id}: {str(e)}")
                
                processed += 1
                
                if processed % 50 == 0:
                    logger.info(f"📊 Processed {processed}/{total_problems} problems...")
            
            # Commit batch
            self.db.commit()
            offset += batch_size
        
        logger.info(f"✅ Enhanced difficulty analysis completed!")
        logger.info(f"   📊 Processed: {processed} problems")
        logger.info(f"   ✨ Updated: {updated} problems")
        
        return {
            "total_processed": processed,
            "total_updated": updated,
            "success_rate": round((updated / processed) * 100, 2) if processed > 0 else 0
        }
    
    def get_difficulty_distribution(self) -> Dict[str, Dict[str, int]]:
        """Get distribution of new difficulty metrics"""
        
        results = {}
        
        # Sub-difficulty distribution
        for difficulty in ["Easy", "Medium", "Hard"]:
            results[difficulty] = {}
            for sub_level in range(1, 6):
                count = self.db.query(Problem).filter(
                    Problem.difficulty == difficulty,
                    Problem.sub_difficulty_level == sub_level
                ).count()
                results[difficulty][f"Level_{sub_level}"] = count
        
        return results


# CLI function for testing
def main():
    """Main function for testing the enhanced difficulty analyzer"""
    
    # Use the new skill tree database
    db_config = DatabaseConfig("sqlite:///./dsatrain_skilltree.db")
    session = db_config.get_session()
    
    try:
        analyzer = EnhancedDifficultyAnalyzer(session)
        
        # Test with existing problems (if any)
        total_problems = session.query(Problem).count()
        
        if total_problems == 0:
            print("⚠️ No problems found in database. Please populate with data first.")
            return
        
        print(f"🔍 Found {total_problems} problems to analyze")
        
        # Process all problems
        results = analyzer.process_all_problems()
        
        print(f"\n📊 Analysis Results:")
        print(f"   Total Processed: {results['total_processed']}")
        print(f"   Total Updated: {results['total_updated']}")
        print(f"   Success Rate: {results['success_rate']}%")
        
        # Show distribution
        distribution = analyzer.get_difficulty_distribution()
        print(f"\n📈 Difficulty Distribution:")
        for difficulty, levels in distribution.items():
            print(f"   {difficulty}:")
            for level, count in levels.items():
                print(f"     {level}: {count} problems")
    
    finally:
        session.close()


if __name__ == "__main__":
    main()

"""
Enhanced Problem Similarity Engine for Skill Tree System
Builds problem clusters and calculates advanced similarity metrics
"""

from typing import Dict, List, Optional, Tuple, Set
from sqlalchemy.orm import Session
from src.models.database import Problem, ProblemCluster, DatabaseConfig
import json
import logging
from dataclasses import dataclass
from collections import defaultdict, Counter
import math
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SimilarityScore:
    """Detailed similarity score between two problems"""
    algorithm_similarity: float
    pattern_similarity: float
    difficulty_similarity: float
    data_structure_similarity: float
    complexity_similarity: float
    combined_score: float
    explanation: str


class EnhancedSimilarityEngine:
    """Enhanced problem similarity analysis and clustering"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        
        # Algorithm pattern groups for similarity
        self.algorithm_patterns = {
            "array_processing": ["arrays", "two_pointers", "sliding_window", "prefix_sum"],
            "string_algorithms": ["strings", "kmp", "rabin_karp", "manacher", "suffix_array"],
            "tree_algorithms": ["trees", "binary_tree", "bst", "dfs", "bfs", "tree_dp"],
            "graph_algorithms": ["graphs", "dfs", "bfs", "dijkstra", "floyd_warshall", "mst"],
            "dynamic_programming": ["dp", "dynamic_programming", "memoization", "optimization"],
            "sorting_searching": ["sorting", "binary_search", "quicksort", "mergesort"],
            "data_structures": ["stack", "queue", "heap", "priority_queue", "hash_table"],
            "advanced_structures": ["segment_tree", "fenwick_tree", "union_find", "trie"],
            "mathematical": ["math", "number_theory", "combinatorics", "probability"],
            "greedy_algorithms": ["greedy", "optimization", "interval_scheduling"],
            "divide_conquer": ["divide_and_conquer", "merge", "binary_search"],
            "backtracking": ["backtracking", "recursion", "permutations", "combinations"]
        }
        
        # Data structure complexity mapping
        self.structure_complexity = {
            "array": 1, "string": 1, "hash_table": 2, "stack": 2, "queue": 2,
            "linked_list": 2, "tree": 3, "heap": 3, "graph": 4, "trie": 4,
            "segment_tree": 5, "fenwick_tree": 5, "union_find": 4
        }
    
    def calculate_similarity(self, problem1: Problem, problem2: Problem) -> SimilarityScore:
        """Calculate comprehensive similarity between two problems"""
        
        # Extract tags
        tags1 = set(problem1.algorithm_tags or [])
        tags2 = set(problem2.algorithm_tags or [])
        
        # Calculate individual similarity components
        algo_sim = self._algorithm_similarity(tags1, tags2)
        pattern_sim = self._pattern_similarity(tags1, tags2)
        diff_sim = self._difficulty_similarity(problem1, problem2)
        struct_sim = self._data_structure_similarity(
            problem1.data_structures or [], 
            problem2.data_structures or []
        )
        complex_sim = self._complexity_similarity(problem1, problem2)
        
        # Calculate weighted combined score
        weights = {
            'algorithm': 0.35,
            'pattern': 0.25,
            'difficulty': 0.15,
            'structure': 0.15,
            'complexity': 0.10
        }
        
        combined = (
            algo_sim * weights['algorithm'] +
            pattern_sim * weights['pattern'] +
            diff_sim * weights['difficulty'] +
            struct_sim * weights['structure'] +
            complex_sim * weights['complexity']
        )
        
        # Generate explanation
        explanation = self._generate_explanation(
            algo_sim, pattern_sim, diff_sim, struct_sim, complex_sim, combined
        )
        
        return SimilarityScore(
            algorithm_similarity=algo_sim,
            pattern_similarity=pattern_sim,
            difficulty_similarity=diff_sim,
            data_structure_similarity=struct_sim,
            complexity_similarity=complex_sim,
            combined_score=combined,
            explanation=explanation
        )
    
    def _algorithm_similarity(self, tags1: Set[str], tags2: Set[str]) -> float:
        """Calculate algorithm tag similarity using Jaccard coefficient"""
        if not tags1 or not tags2:
            return 0.0
        
        intersection = len(tags1.intersection(tags2))
        union = len(tags1.union(tags2))
        
        return intersection / union if union > 0 else 0.0
    
    def _pattern_similarity(self, tags1: Set[str], tags2: Set[str]) -> float:
        """Calculate similarity based on algorithm pattern groups"""
        
        # Find which pattern groups each problem belongs to
        patterns1 = set()
        patterns2 = set()
        
        for pattern, algorithms in self.algorithm_patterns.items():
            if any(tag in algorithms for tag in tags1):
                patterns1.add(pattern)
            if any(tag in algorithms for tag in tags2):
                patterns2.add(pattern)
        
        if not patterns1 or not patterns2:
            return 0.0
        
        intersection = len(patterns1.intersection(patterns2))
        union = len(patterns1.union(patterns2))
        
        return intersection / union if union > 0 else 0.0
    
    def _difficulty_similarity(self, problem1: Problem, problem2: Problem) -> float:
        """Calculate difficulty-based similarity"""
        
        # Main difficulty similarity
        difficulty_map = {'Easy': 1, 'Medium': 2, 'Hard': 3}
        diff1 = difficulty_map.get(problem1.difficulty, 2)
        diff2 = difficulty_map.get(problem2.difficulty, 2)
        
        base_similarity = 1.0 - abs(diff1 - diff2) / 2.0
        
        # Sub-difficulty similarity (if available)
        if hasattr(problem1, 'sub_difficulty_level') and hasattr(problem2, 'sub_difficulty_level'):
            if problem1.sub_difficulty_level and problem2.sub_difficulty_level:
                sub_diff = abs(problem1.sub_difficulty_level - problem2.sub_difficulty_level)
                sub_similarity = 1.0 - sub_diff / 4.0  # Max difference is 4
                base_similarity = (base_similarity + sub_similarity) / 2
        
        return max(0.0, base_similarity)
    
    def _data_structure_similarity(self, structures1: List[str], structures2: List[str]) -> float:
        """Calculate data structure usage similarity"""
        if not structures1 or not structures2:
            return 0.0
        
        set1 = set(structures1)
        set2 = set(structures2)
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def _complexity_similarity(self, problem1: Problem, problem2: Problem) -> float:
        """Calculate time/space complexity similarity"""
        
        # Simple implementation - can be enhanced with actual complexity parsing
        quality_sim = 0.0
        
        if problem1.quality_score and problem2.quality_score:
            quality_diff = abs(problem1.quality_score - problem2.quality_score)
            quality_sim = 1.0 - quality_diff / 100.0
        
        relevance_sim = 0.0
        if problem1.google_interview_relevance and problem2.google_interview_relevance:
            relevance_diff = abs(problem1.google_interview_relevance - problem2.google_interview_relevance)
            relevance_sim = 1.0 - relevance_diff / 100.0
        
        return (quality_sim + relevance_sim) / 2 if quality_sim > 0 or relevance_sim > 0 else 0.5
    
    def _generate_explanation(self, algo: float, pattern: float, diff: float, 
                            struct: float, complex: float, combined: float) -> str:
        """Generate human-readable explanation for similarity score"""
        
        explanations = []
        
        if algo > 0.7:
            explanations.append(f"Strong algorithm overlap ({algo:.2f})")
        elif algo > 0.4:
            explanations.append(f"Moderate algorithm similarity ({algo:.2f})")
        
        if pattern > 0.6:
            explanations.append(f"Similar solution patterns ({pattern:.2f})")
        
        if diff > 0.8:
            explanations.append("Same difficulty level")
        elif diff > 0.5:
            explanations.append("Similar difficulty")
        
        if struct > 0.6:
            explanations.append(f"Similar data structures ({struct:.2f})")
        
        if combined > 0.8:
            summary = "Very similar problems"
        elif combined > 0.6:
            summary = "Moderately similar problems"
        elif combined > 0.4:
            summary = "Some similarity"
        else:
            summary = "Low similarity"
        
        return f"{summary}: {', '.join(explanations)}" if explanations else summary
    
    def find_similar_problems(self, problem_id: str, limit: int = 10, 
                            min_similarity: float = 0.3) -> List[Tuple[Problem, SimilarityScore]]:
        """Find most similar problems to a given problem"""
        
        target_problem = self.db.query(Problem).filter(Problem.id == problem_id).first()
        if not target_problem:
            return []
        
        # Get all other problems
        all_problems = self.db.query(Problem).filter(Problem.id != problem_id).all()
        
        similarities = []
        for problem in all_problems:
            similarity = self.calculate_similarity(target_problem, problem)
            if similarity.combined_score >= min_similarity:
                similarities.append((problem, similarity))
        
        # Sort by similarity score
        similarities.sort(key=lambda x: x[1].combined_score, reverse=True)
        
        return similarities[:limit]
    
    def create_problem_clusters(self, similarity_threshold: float = 0.6) -> Dict[str, int]:
        """Create clusters of similar problems for skill tree organization"""
        
        logger.info(f"🔍 Starting problem clustering with threshold {similarity_threshold}")
        
        # Get all problems grouped by skill area and difficulty
        problems_by_category = defaultdict(list)
        
        all_problems = self.db.query(Problem).all()
        
        for problem in all_problems:
            if not problem.algorithm_tags:
                continue
                
            # Determine primary skill area
            primary_skill = self._determine_primary_skill(problem.algorithm_tags)
            key = f"{primary_skill}_{problem.difficulty}"
            problems_by_category[key].append(problem)
        
        clusters_created = 0
        
        for category, problems in problems_by_category.items():
            if len(problems) < 2:
                continue
                
            logger.info(f"📊 Clustering {len(problems)} problems in category: {category}")
            
            # Create clusters for this category
            category_clusters = self._cluster_problems(problems, similarity_threshold)
            
            # Save clusters to database
            for i, cluster_problems in enumerate(category_clusters):
                if len(cluster_problems) >= 2:  # Only save clusters with multiple problems
                    cluster = self._create_cluster_record(category, i, cluster_problems)
                    self.db.add(cluster)
                    clusters_created += 1
        
        self.db.commit()
        
        logger.info(f"✅ Created {clusters_created} problem clusters")
        
        return {
            "total_clusters": clusters_created,
            "categories_processed": len(problems_by_category),
            "total_problems": len(all_problems)
        }
    
    def _determine_primary_skill(self, algorithm_tags: List[str]) -> str:
        """Determine the primary skill area for a problem"""
        
        # Count pattern matches
        pattern_counts = defaultdict(int)
        
        for pattern, algorithms in self.algorithm_patterns.items():
            for tag in algorithm_tags:
                if tag.lower() in [alg.lower() for alg in algorithms]:
                    pattern_counts[pattern] += 1
        
        if pattern_counts:
            return max(pattern_counts.items(), key=lambda x: x[1])[0]
        
        # Fallback to first tag
        return algorithm_tags[0] if algorithm_tags else "general"
    
    def _cluster_problems(self, problems: List[Problem], threshold: float) -> List[List[Problem]]:
        """Cluster problems using similarity threshold"""
        
        clusters = []
        unclustered = problems.copy()
        
        while unclustered:
            # Start new cluster with first unclustered problem
            seed = unclustered.pop(0)
            cluster = [seed]
            
            # Find similar problems to add to cluster
            remaining = unclustered.copy()
            for problem in remaining:
                similarity = self.calculate_similarity(seed, problem)
                if similarity.combined_score >= threshold:
                    cluster.append(problem)
                    unclustered.remove(problem)
            
            clusters.append(cluster)
        
        return clusters
    
    def _create_cluster_record(self, category: str, cluster_id: int, 
                             problems: List[Problem]) -> ProblemCluster:
        """Create a ProblemCluster database record"""
        
        primary_skill, difficulty = category.split('_', 1)
        
        # Calculate cluster statistics
        total_quality = sum(p.quality_score or 0 for p in problems)
        avg_quality = total_quality / len(problems) if problems else 0
        
        total_relevance = sum(p.google_interview_relevance or 0 for p in problems)
        avg_relevance = total_relevance / len(problems) if problems else 0
        
        # Get all unique algorithm tags
        all_tags = set()
        for problem in problems:
            if problem.algorithm_tags:
                all_tags.update(problem.algorithm_tags)
        
        # Select representative problems (up to 3)
        representatives = sorted(problems, key=lambda p: p.quality_score or 0, reverse=True)[:3]
        representative_ids = [p.id for p in representatives]
        
        all_problem_ids = [p.id for p in problems]
        
        cluster = ProblemCluster(
            id=str(uuid.uuid4()),
            cluster_name=f"{primary_skill.title()} {difficulty} - Cluster {cluster_id + 1}",
            primary_skill_area=primary_skill,
            difficulty_level=difficulty,
            representative_problems=representative_ids,
            all_problems=all_problem_ids,
            similarity_threshold=0.6,  # Default threshold
            cluster_size=len(problems),
            avg_quality_score=avg_quality,
            avg_google_relevance=avg_relevance,
            algorithm_tags=list(all_tags)
        )
        
        return cluster
    
    def get_cluster_statistics(self) -> Dict[str, any]:
        """Get statistics about created clusters"""
        
        total_clusters = self.db.query(ProblemCluster).count()
        
        # Clusters by skill area
        skill_areas = defaultdict(int)
        difficulties = defaultdict(int)
        
        clusters = self.db.query(ProblemCluster).all()
        
        for cluster in clusters:
            skill_areas[cluster.primary_skill_area] += 1
            difficulties[cluster.difficulty_level] += 1
        
        return {
            "total_clusters": total_clusters,
            "clusters_by_skill": dict(skill_areas),
            "clusters_by_difficulty": dict(difficulties),
            "average_cluster_size": sum(c.cluster_size for c in clusters) / len(clusters) if clusters else 0
        }


# CLI function for testing
def main():
    """Main function for testing the enhanced similarity engine"""
    
    # Use the new skill tree database
    db_config = DatabaseConfig("sqlite:///./dsatrain_skilltree.db")
    session = db_config.get_session()
    
    try:
        engine = EnhancedSimilarityEngine(session)
        
        # Test with existing problems (if any)
        total_problems = session.query(Problem).count()
        
        if total_problems == 0:
            print("⚠️ No problems found in database. Please populate with data first.")
            return
        
        print(f"🔍 Found {total_problems} problems for similarity analysis")
        
        # Create clusters
        cluster_results = engine.create_problem_clusters(similarity_threshold=0.5)
        
        print(f"\n📊 Clustering Results:")
        print(f"   Total Clusters: {cluster_results['total_clusters']}")
        print(f"   Categories Processed: {cluster_results['categories_processed']}")
        print(f"   Total Problems: {cluster_results['total_problems']}")
        
        # Show cluster statistics
        stats = engine.get_cluster_statistics()
        print(f"\n📈 Cluster Statistics:")
        print(f"   Average Cluster Size: {stats['average_cluster_size']:.2f}")
        print(f"   Clusters by Skill Area:")
        for skill, count in stats['clusters_by_skill'].items():
            print(f"     {skill}: {count} clusters")
        
        # Test similarity for first problem (if exists)
        first_problem = session.query(Problem).first()
        if first_problem:
            print(f"\n🔗 Testing similarity for problem: {first_problem.id}")
            similar = engine.find_similar_problems(first_problem.id, limit=3)
            
            for i, (problem, similarity) in enumerate(similar, 1):
                print(f"   {i}. {problem.id} (Score: {similarity.combined_score:.3f})")
                print(f"      {similarity.explanation}")
    
    finally:
        session.close()


if __name__ == "__main__":
    main()

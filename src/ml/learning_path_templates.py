"""
Learning Path Template Manager
Creates and manages predefined learning path templates for common goals
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging

from ..models.database import LearningPathTemplate, Problem
from .learning_path_engine import SkillArea, DifficultyLevel

logger = logging.getLogger(__name__)


class LearningPathTemplateManager:
    """
    Manager for creating and updating learning path templates
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def create_all_templates(self) -> List[LearningPathTemplate]:
        """Create all predefined learning path templates"""
        
        templates = [
            self._create_google_interview_template(),
            self._create_faang_prep_template(),
            self._create_competitive_programming_template(),
            self._create_fundamentals_template(),
            self._create_dynamic_programming_mastery_template(),
            self._create_graph_algorithms_template(),
            self._create_system_design_prep_template(),
            self._create_quick_interview_prep_template()
        ]
        
        # Save all templates to database
        for template in templates:
            existing = self.db.query(LearningPathTemplate).filter(
                LearningPathTemplate.id == template.id
            ).first()
            
            if not existing:
                self.db.add(template)
                logger.info(f"Created template: {template.name}")
            else:
                # Update existing template
                for attr, value in template.__dict__.items():
                    if not attr.startswith('_'):
                        setattr(existing, attr, value)
                logger.info(f"Updated template: {template.name}")
        
        self.db.commit()
        return templates
    
    def _create_google_interview_template(self) -> LearningPathTemplate:
        """Create Google/Meta interview preparation template"""
        
        return LearningPathTemplate(
            id="google_interview_12w",
            name="Google Interview Mastery (12 Weeks)",
            description="Comprehensive 12-week program designed specifically for Google/Meta technical interviews. Covers all essential algorithms and data structures with Google-style problems.",
            category="interview_prep",
            target_skill_level="intermediate",
            estimated_duration_weeks=12,
            prerequisite_skills=[
                SkillArea.ARRAYS.value,
                "basic_programming"
            ],
            learning_objectives=[
                {
                    "week": 1,
                    "skills": [SkillArea.ARRAYS.value, SkillArea.STRINGS.value],
                    "target_level": 0.7,
                    "focus": "Foundation building"
                },
                {
                    "week": 2,
                    "skills": [SkillArea.HASH_TABLES.value, SkillArea.TWO_POINTERS.value],
                    "target_level": 0.7,
                    "focus": "Pattern recognition"
                },
                {
                    "week": 3,
                    "skills": [SkillArea.SLIDING_WINDOW.value],
                    "target_level": 0.6,
                    "focus": "Advanced array techniques"
                },
                {
                    "week": 4,
                    "skills": [SkillArea.TREES.value],
                    "target_level": 0.8,
                    "focus": "Tree traversal and manipulation"
                },
                {
                    "week": 5,
                    "skills": [SkillArea.BINARY_SEARCH.value],
                    "target_level": 0.7,
                    "focus": "Search algorithms"
                },
                {
                    "week": 6,
                    "skills": [SkillArea.GRAPHS.value],
                    "target_level": 0.7,
                    "focus": "Graph fundamentals"
                },
                {
                    "week": 7,
                    "skills": [SkillArea.DYNAMIC_PROGRAMMING.value],
                    "target_level": 0.6,
                    "focus": "DP introduction"
                },
                {
                    "week": 8,
                    "skills": [SkillArea.DYNAMIC_PROGRAMMING.value],
                    "target_level": 0.8,
                    "focus": "Advanced DP patterns"
                },
                {
                    "week": 9,
                    "skills": [SkillArea.GREEDY.value, SkillArea.BACKTRACKING.value],
                    "target_level": 0.7,
                    "focus": "Advanced algorithms"
                },
                {
                    "week": 10,
                    "skills": ["mixed_practice"],
                    "target_level": 0.8,
                    "focus": "Integration and speed"
                },
                {
                    "week": 11,
                    "skills": ["mock_interviews"],
                    "target_level": 0.9,
                    "focus": "Interview simulation"
                },
                {
                    "week": 12,
                    "skills": ["system_design_basics"],
                    "target_level": 0.6,
                    "focus": "System design prep"
                }
            ],
            problem_sequence_template={
                "selection_criteria": {
                    "platforms": ["leetcode", "google"],
                    "min_quality_score": 85,
                    "google_interview_relevance": 70,
                    "difficulty_progression": "gradual",
                    "problems_per_week": 15
                },
                "difficulty_distribution": {
                    "weeks_1_3": {"Easy": 60, "Medium": 40, "Hard": 0},
                    "weeks_4_6": {"Easy": 30, "Medium": 60, "Hard": 10},
                    "weeks_7_9": {"Easy": 20, "Medium": 60, "Hard": 20},
                    "weeks_10_12": {"Easy": 10, "Medium": 50, "Hard": 40}
                }
            },
            adaptation_rules={
                "performance_thresholds": {
                    "struggling": {"success_rate": 0.6, "avg_time_multiplier": 1.5},
                    "excelling": {"success_rate": 0.9, "avg_time_multiplier": 0.7}
                },
                "adaptations": {
                    "struggling": {
                        "add_easier_problems": True,
                        "extend_timeline": True,
                        "add_concept_review": True
                    },
                    "excelling": {
                        "skip_easier_problems": True,
                        "add_challenge_problems": True,
                        "accelerate_timeline": True
                    }
                }
            },
            difficulty_curve={
                "type": "gradual_increase",
                "starting_difficulty": 0.3,
                "peak_difficulty": 0.8,
                "plateau_weeks": [10, 11, 12]
            },
            concept_order=[
                SkillArea.ARRAYS.value,
                SkillArea.STRINGS.value,
                SkillArea.HASH_TABLES.value,
                SkillArea.TWO_POINTERS.value,
                SkillArea.SLIDING_WINDOW.value,
                SkillArea.TREES.value,
                SkillArea.BINARY_SEARCH.value,
                SkillArea.GRAPHS.value,
                SkillArea.DYNAMIC_PROGRAMMING.value,
                SkillArea.GREEDY.value,
                SkillArea.BACKTRACKING.value
            ],
            tags=["google", "meta", "faang", "interview", "comprehensive"],
            created_by="system",
            status="active"
        )
    
    def _create_faang_prep_template(self) -> LearningPathTemplate:
        """Create general FAANG interview preparation template"""
        
        return LearningPathTemplate(
            id="faang_prep_10w",
            name="FAANG Interview Bootcamp (10 Weeks)",
            description="Intensive 10-week program covering all major tech company interview patterns. High-frequency problems from Google, Meta, Amazon, Apple, and Netflix.",
            category="interview_prep",
            target_skill_level="intermediate",
            estimated_duration_weeks=10,
            prerequisite_skills=[
                SkillArea.ARRAYS.value,
                SkillArea.STRINGS.value,
                "basic_algorithms"
            ],
            learning_objectives=[
                {
                    "phase": "foundation",
                    "weeks": [1, 2],
                    "skills": [SkillArea.ARRAYS.value, SkillArea.HASH_TABLES.value, SkillArea.TWO_POINTERS.value],
                    "target_level": 0.8
                },
                {
                    "phase": "core_structures",
                    "weeks": [3, 4, 5],
                    "skills": [SkillArea.TREES.value, SkillArea.GRAPHS.value, SkillArea.BINARY_SEARCH.value],
                    "target_level": 0.8
                },
                {
                    "phase": "advanced_algorithms",
                    "weeks": [6, 7, 8],
                    "skills": [SkillArea.DYNAMIC_PROGRAMMING.value, SkillArea.GREEDY.value, SkillArea.BACKTRACKING.value],
                    "target_level": 0.7
                },
                {
                    "phase": "mastery",
                    "weeks": [9, 10],
                    "skills": ["mixed_practice", "company_specific"],
                    "target_level": 0.9
                }
            ],
            problem_sequence_template={
                "selection_criteria": {
                    "company_tags": ["google", "facebook", "amazon", "apple", "netflix"],
                    "frequency_score": 80,
                    "min_quality_score": 80,
                    "problems_per_week": 18
                },
                "company_distribution": {
                    "google": 30,
                    "facebook": 25,
                    "amazon": 25,
                    "apple": 10,
                    "netflix": 10
                }
            },
            tags=["faang", "interview", "intensive", "high_frequency"],
            created_by="system",
            status="active"
        )
    
    def _create_competitive_programming_template(self) -> LearningPathTemplate:
        """Create competitive programming mastery template"""
        
        return LearningPathTemplate(
            id="competitive_programming_16w",
            name="Competitive Programming Mastery (16 Weeks)",
            description="Comprehensive competitive programming course from beginner to advanced. Covers algorithms, optimization techniques, and contest strategies.",
            category="competitive",
            target_skill_level="advanced",
            estimated_duration_weeks=16,
            prerequisite_skills=[
                SkillArea.ARRAYS.value,
                SkillArea.MATHEMATICS.value,
                "basic_algorithms"
            ],
            learning_objectives=[
                {
                    "phase": "fundamentals",
                    "weeks": [1, 2, 3, 4],
                    "skills": [SkillArea.MATHEMATICS.value, SkillArea.GREEDY.value, SkillArea.SORTING.value],
                    "target_level": 0.9
                },
                {
                    "phase": "graph_theory",
                    "weeks": [5, 6, 7, 8],
                    "skills": [SkillArea.GRAPHS.value, "shortest_paths", "mst", "network_flow"],
                    "target_level": 0.9
                },
                {
                    "phase": "dynamic_programming",
                    "weeks": [9, 10, 11],
                    "skills": [SkillArea.DYNAMIC_PROGRAMMING.value, "optimization_dp"],
                    "target_level": 0.9
                },
                {
                    "phase": "advanced_topics",
                    "weeks": [12, 13, 14],
                    "skills": ["string_algorithms", "computational_geometry", "number_theory"],
                    "target_level": 0.8
                },
                {
                    "phase": "contest_practice",
                    "weeks": [15, 16],
                    "skills": ["contest_strategies", "time_management"],
                    "target_level": 0.9
                }
            ],
            problem_sequence_template={
                "selection_criteria": {
                    "platforms": ["codeforces", "atcoder", "codechef"],
                    "difficulty_range": ["Medium", "Hard"],
                    "algorithm_focus": True,
                    "problems_per_week": 12
                }
            },
            tags=["competitive", "algorithms", "advanced", "contests"],
            created_by="system",
            status="active"
        )
    
    def _create_fundamentals_template(self) -> LearningPathTemplate:
        """Create computer science fundamentals template"""
        
        return LearningPathTemplate(
            id="cs_fundamentals_8w",
            name="CS Fundamentals Refresher (8 Weeks)",
            description="Solid foundation in computer science fundamentals. Perfect for self-taught developers or interview preparation starting from basics.",
            category="foundations",
            target_skill_level="beginner",
            estimated_duration_weeks=8,
            prerequisite_skills=["basic_programming"],
            learning_objectives=[
                {
                    "week": 1,
                    "skills": [SkillArea.ARRAYS.value],
                    "concepts": ["iteration", "indexing", "basic_operations"],
                    "target_level": 0.8
                },
                {
                    "week": 2,
                    "skills": [SkillArea.STRINGS.value],
                    "concepts": ["string_manipulation", "pattern_matching"],
                    "target_level": 0.7
                },
                {
                    "week": 3,
                    "skills": [SkillArea.HASH_TABLES.value],
                    "concepts": ["hashing", "key_value_pairs", "lookup_optimization"],
                    "target_level": 0.7
                },
                {
                    "week": 4,
                    "skills": [SkillArea.TREES.value],
                    "concepts": ["tree_structure", "traversal", "binary_trees"],
                    "target_level": 0.7
                },
                {
                    "week": 5,
                    "skills": [SkillArea.SORTING.value, SkillArea.BINARY_SEARCH.value],
                    "concepts": ["sorting_algorithms", "search_optimization"],
                    "target_level": 0.7
                },
                {
                    "week": 6,
                    "skills": [SkillArea.GRAPHS.value],
                    "concepts": ["graph_representation", "traversal", "basic_algorithms"],
                    "target_level": 0.6
                },
                {
                    "week": 7,
                    "skills": [SkillArea.DYNAMIC_PROGRAMMING.value],
                    "concepts": ["memoization", "optimal_substructure"],
                    "target_level": 0.5
                },
                {
                    "week": 8,
                    "skills": ["review_and_integration"],
                    "concepts": ["problem_solving_strategies", "time_complexity"],
                    "target_level": 0.7
                }
            ],
            problem_sequence_template={
                "selection_criteria": {
                    "difficulty": ["Easy", "Medium"],
                    "educational_value": 85,
                    "problems_per_week": 8,
                    "explanation_quality": "high"
                },
                "difficulty_distribution": {
                    "weeks_1_4": {"Easy": 80, "Medium": 20},
                    "weeks_5_8": {"Easy": 60, "Medium": 40}
                }
            },
            tags=["fundamentals", "beginner", "education", "basics"],
            created_by="system",
            status="active"
        )
    
    def _create_dynamic_programming_mastery_template(self) -> LearningPathTemplate:
        """Create DP mastery template"""
        
        return LearningPathTemplate(
            id="dp_mastery_6w",
            name="Dynamic Programming Mastery (6 Weeks)",
            description="Deep dive into dynamic programming patterns and techniques. From basic memoization to advanced DP optimizations.",
            category="skill_mastery",
            target_skill_level="intermediate",
            estimated_duration_weeks=6,
            prerequisite_skills=[
                SkillArea.ARRAYS.value,
                SkillArea.STRINGS.value,
                "recursion"
            ],
            learning_objectives=[
                {
                    "week": 1,
                    "pattern": "linear_dp",
                    "concepts": ["memoization", "tabulation", "1d_dp"],
                    "target_level": 0.8
                },
                {
                    "week": 2,
                    "pattern": "2d_dp",
                    "concepts": ["grid_dp", "string_dp", "lcs_variations"],
                    "target_level": 0.8
                },
                {
                    "week": 3,
                    "pattern": "knapsack_dp",
                    "concepts": ["0_1_knapsack", "unbounded_knapsack", "subset_sum"],
                    "target_level": 0.8
                },
                {
                    "week": 4,
                    "pattern": "interval_dp",
                    "concepts": ["matrix_chain", "palindrome_partitioning", "burst_balloons"],
                    "target_level": 0.7
                },
                {
                    "week": 5,
                    "pattern": "tree_dp",
                    "concepts": ["tree_based_dp", "diameter_problems", "path_problems"],
                    "target_level": 0.7
                },
                {
                    "week": 6,
                    "pattern": "advanced_dp",
                    "concepts": ["digit_dp", "bitmask_dp", "optimization_techniques"],
                    "target_level": 0.6
                }
            ],
            problem_sequence_template={
                "selection_criteria": {
                    "algorithm_tags": [SkillArea.DYNAMIC_PROGRAMMING.value],
                    "difficulty_progression": True,
                    "pattern_diversity": True,
                    "problems_per_week": 10
                }
            },
            tags=["dynamic_programming", "patterns", "mastery", "optimization"],
            created_by="system",
            status="active"
        )
    
    def _create_graph_algorithms_template(self) -> LearningPathTemplate:
        """Create graph algorithms template"""
        
        return LearningPathTemplate(
            id="graph_algorithms_8w",
            name="Graph Algorithms Deep Dive (8 Weeks)",
            description="Comprehensive coverage of graph algorithms from basic traversal to advanced network flow algorithms.",
            category="skill_mastery",
            target_skill_level="intermediate",
            estimated_duration_weeks=8,
            prerequisite_skills=[
                SkillArea.ARRAYS.value,
                SkillArea.TREES.value,
                "basic_algorithms"
            ],
            learning_objectives=[
                {
                    "week": 1,
                    "topic": "graph_representation",
                    "algorithms": ["adjacency_list", "adjacency_matrix", "edge_list"],
                    "target_level": 0.9
                },
                {
                    "week": 2,
                    "topic": "graph_traversal",
                    "algorithms": ["dfs", "bfs", "topological_sort"],
                    "target_level": 0.9
                },
                {
                    "week": 3,
                    "topic": "shortest_paths",
                    "algorithms": ["dijkstra", "bellman_ford", "floyd_warshall"],
                    "target_level": 0.8
                },
                {
                    "week": 4,
                    "topic": "minimum_spanning_tree",
                    "algorithms": ["kruskal", "prim", "union_find"],
                    "target_level": 0.8
                },
                {
                    "week": 5,
                    "topic": "strongly_connected_components",
                    "algorithms": ["kosaraju", "tarjan", "condensation"],
                    "target_level": 0.7
                },
                {
                    "week": 6,
                    "topic": "network_flow",
                    "algorithms": ["ford_fulkerson", "edmonds_karp", "dinic"],
                    "target_level": 0.6
                },
                {
                    "week": 7,
                    "topic": "advanced_topics",
                    "algorithms": ["bipartite_matching", "minimum_cut", "max_flow_min_cut"],
                    "target_level": 0.6
                },
                {
                    "week": 8,
                    "topic": "applications",
                    "algorithms": ["practical_problems", "optimization", "real_world_graphs"],
                    "target_level": 0.7
                }
            ],
            problem_sequence_template={
                "selection_criteria": {
                    "algorithm_tags": [SkillArea.GRAPHS.value],
                    "algorithm_specific": True,
                    "theory_and_practice": True,
                    "problems_per_week": 8
                }
            },
            tags=["graphs", "algorithms", "network_theory", "advanced"],
            created_by="system",
            status="active"
        )
    
    def _create_system_design_prep_template(self) -> LearningPathTemplate:
        """Create system design preparation template"""
        
        return LearningPathTemplate(
            id="system_design_prep_6w",
            name="System Design Interview Prep (6 Weeks)",
            description="Introduction to system design concepts for technical interviews. Covers scalability, reliability, and common system design patterns.",
            category="interview_prep",
            target_skill_level="advanced",
            estimated_duration_weeks=6,
            prerequisite_skills=[
                SkillArea.HASH_TABLES.value,
                SkillArea.GRAPHS.value,
                "data_structures_basics",
                "algorithm_complexity"
            ],
            learning_objectives=[
                {
                    "week": 1,
                    "topic": "fundamentals",
                    "concepts": ["scalability", "reliability", "consistency", "availability"],
                    "target_level": 0.7
                },
                {
                    "week": 2,
                    "topic": "storage_systems",
                    "concepts": ["databases", "caching", "file_systems", "replication"],
                    "target_level": 0.7
                },
                {
                    "week": 3,
                    "topic": "distributed_systems",
                    "concepts": ["load_balancing", "partitioning", "consistent_hashing"],
                    "target_level": 0.6
                },
                {
                    "week": 4,
                    "topic": "microservices",
                    "concepts": ["service_oriented_architecture", "api_design", "communication"],
                    "target_level": 0.6
                },
                {
                    "week": 5,
                    "topic": "case_studies",
                    "concepts": ["url_shortener", "chat_system", "news_feed"],
                    "target_level": 0.7
                },
                {
                    "week": 6,
                    "topic": "advanced_topics",
                    "concepts": ["monitoring", "security", "performance_optimization"],
                    "target_level": 0.6
                }
            ],
            problem_sequence_template={
                "selection_criteria": {
                    "problem_type": "system_design",
                    "complexity": ["basic", "intermediate"],
                    "real_world_relevance": True,
                    "problems_per_week": 4
                }
            },
            tags=["system_design", "scalability", "architecture", "interviews"],
            created_by="system",
            status="active"
        )
    
    def _create_quick_interview_prep_template(self) -> LearningPathTemplate:
        """Create quick 4-week interview prep template"""
        
        return LearningPathTemplate(
            id="quick_interview_4w",
            name="Quick Interview Prep (4 Weeks)",
            description="Intensive 4-week crash course for urgent interview preparation. Covers the most important patterns and high-frequency problems.",
            category="interview_prep",
            target_skill_level="intermediate",
            estimated_duration_weeks=4,
            prerequisite_skills=[
                SkillArea.ARRAYS.value,
                SkillArea.STRINGS.value,
                "basic_programming"
            ],
            learning_objectives=[
                {
                    "week": 1,
                    "focus": "essentials",
                    "skills": [SkillArea.ARRAYS.value, SkillArea.HASH_TABLES.value, SkillArea.TWO_POINTERS.value],
                    "target_level": 0.8
                },
                {
                    "week": 2,
                    "focus": "trees_and_graphs",
                    "skills": [SkillArea.TREES.value, SkillArea.GRAPHS.value],
                    "target_level": 0.7
                },
                {
                    "week": 3,
                    "focus": "dp_and_greedy",
                    "skills": [SkillArea.DYNAMIC_PROGRAMMING.value, SkillArea.GREEDY.value],
                    "target_level": 0.6
                },
                {
                    "week": 4,
                    "focus": "practice_and_review",
                    "skills": ["mixed_practice", "mock_interviews"],
                    "target_level": 0.8
                }
            ],
            problem_sequence_template={
                "selection_criteria": {
                    "frequency_score": 90,
                    "google_interview_relevance": 80,
                    "time_to_solve": "reasonable",
                    "problems_per_week": 20
                },
                "emphasis": "high_frequency_patterns"
            },
            tags=["quick", "intensive", "high_frequency", "urgent"],
            created_by="system",
            status="active"
        )
    
    def get_template_recommendations(
        self,
        user_goals: List[str],
        available_weeks: int,
        current_skill_level: str
    ) -> List[Dict[str, Any]]:
        """Get template recommendations based on user criteria"""
        
        templates = self.db.query(LearningPathTemplate).filter(
            LearningPathTemplate.status == 'active'
        ).all()
        
        recommendations = []
        
        for template in templates:
            score = self._calculate_template_fit_score(
                template, user_goals, available_weeks, current_skill_level
            )
            
            recommendations.append({
                'template': template.to_dict(),
                'fit_score': score,
                'reasons': self._generate_recommendation_reasons(
                    template, user_goals, available_weeks, current_skill_level
                )
            })
        
        # Sort by fit score
        recommendations.sort(key=lambda x: x['fit_score'], reverse=True)
        
        return recommendations[:5]  # Top 5 recommendations
    
    def _calculate_template_fit_score(
        self,
        template: LearningPathTemplate,
        user_goals: List[str],
        available_weeks: int,
        current_skill_level: str
    ) -> float:
        """Calculate how well a template fits user requirements"""
        
        score = 0.0
        
        # Goal alignment (40% of score)
        goal_score = 0.0
        user_goals_lower = [g.lower() for g in user_goals]
        template_tags_lower = [t.lower() for t in (template.tags or [])]
        
        for goal in user_goals_lower:
            if goal in template_tags_lower:
                goal_score += 1.0
            elif any(goal in tag for tag in template_tags_lower):
                goal_score += 0.5
        
        if user_goals:
            goal_score = goal_score / len(user_goals)
        
        score += goal_score * 0.4
        
        # Duration fit (30% of score)
        duration_diff = abs(template.estimated_duration_weeks - available_weeks)
        duration_score = max(0, 1.0 - (duration_diff / 8.0))  # Penalize large differences
        score += duration_score * 0.3
        
        # Skill level fit (30% of score)
        skill_level_score = 1.0 if template.target_skill_level == current_skill_level else 0.7
        score += skill_level_score * 0.3
        
        return min(1.0, score)
    
    def _generate_recommendation_reasons(
        self,
        template: LearningPathTemplate,
        user_goals: List[str],
        available_weeks: int,
        current_skill_level: str
    ) -> List[str]:
        """Generate reasons why this template is recommended"""
        
        reasons = []
        
        # Check goal alignment
        user_goals_lower = [g.lower() for g in user_goals]
        template_tags_lower = [t.lower() for t in (template.tags or [])]
        
        matching_goals = [goal for goal in user_goals_lower if goal in template_tags_lower]
        if matching_goals:
            reasons.append(f"Aligned with your goals: {', '.join(matching_goals)}")
        
        # Check duration
        duration_diff = abs(template.estimated_duration_weeks - available_weeks)
        if duration_diff <= 1:
            reasons.append(f"Perfect duration match ({template.estimated_duration_weeks} weeks)")
        elif duration_diff <= 2:
            reasons.append(f"Good duration fit ({template.estimated_duration_weeks} weeks)")
        
        # Check skill level
        if template.target_skill_level == current_skill_level:
            reasons.append(f"Designed for {current_skill_level} level")
        
        # Add specific template benefits
        if "google" in template_tags_lower:
            reasons.append("Optimized for Google-style interviews")
        if "intensive" in template_tags_lower or "quick" in template_tags_lower:
            reasons.append("Intensive format for rapid skill building")
        if "comprehensive" in template_tags_lower:
            reasons.append("Comprehensive coverage of all essential topics")
        
        return reasons[:3]  # Limit to top 3 reasons

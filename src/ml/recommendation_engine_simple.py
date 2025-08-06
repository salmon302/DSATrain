"""
Simplified ML Recommendation Engine for DSA Training Platform
Basic implementation that works without heavy ML dependencies initially
"""

from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json
import logging
from collections import defaultdict

from ..models.database import Problem, Solution, UserInteraction, LearningPath

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """
    Simplified recommendation engine that provides personalized problem suggestions
    without requiring heavy ML dependencies initially
    """
    
    def __init__(self, db_session: Session):
        """Initialize the recommendation engine with database session"""
        self.db = db_session
        self.is_trained = True  # Mark as trained for simplified version
        
        # Recommendation weights
        self.weights = {
            'content_based': 0.4,
            'collaborative': 0.3,
            'popularity': 0.2,
            'difficulty_progression': 0.1
        }
    
    def train_models(self) -> None:
        """
        Simplified training - just log that training is complete
        """
        try:
            logger.info("Training simplified recommendation models...")
            self.is_trained = True
            logger.info("Simplified models training completed successfully")
            
        except Exception as e:
            logger.error(f"Error training simplified models: {str(e)}")
            raise
    
    def get_personalized_recommendations(
        self,
        user_id: str,
        num_recommendations: int = 10,
        difficulty_preference: Optional[str] = None,
        focus_areas: Optional[List[str]] = None,
        exclude_solved: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get personalized recommendations for a specific user using simplified algorithms
        """
        try:
            # Get user interaction history
            user_history = self._get_user_history(user_id)
            
            # Get candidate problems
            candidates = self._get_candidate_problems(
                user_id, difficulty_preference, focus_areas, exclude_solved
            )
            
            if not candidates:
                logger.warning(f"No candidate problems found for user {user_id}")
                return self._get_fallback_recommendations(num_recommendations)
            
            # Calculate simplified recommendation scores
            recommendations = []
            for problem in candidates:
                score_breakdown = self._calculate_simplified_score(
                    user_id, problem, user_history
                )
                
                rec_item = {
                    **problem.to_dict(),
                    'recommendation_score': score_breakdown['total_score'],
                    'score_breakdown': score_breakdown,
                    'recommendation_reasoning': self._generate_reasoning(
                        problem, score_breakdown, user_history
                    )
                }
                recommendations.append(rec_item)
            
            # Sort by total score and return top N
            recommendations.sort(key=lambda x: x['recommendation_score'], reverse=True)
            
            return recommendations[:num_recommendations]
            
        except Exception as e:
            logger.error(f"Error generating personalized recommendations: {str(e)}")
            return self._get_fallback_recommendations(num_recommendations)
    
    def get_content_based_recommendations(
        self,
        problem_id: str,
        num_recommendations: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get problems similar to a given problem using simplified similarity
        """
        try:
            # Get the reference problem
            ref_problem = self.db.query(Problem).filter(Problem.id == problem_id).first()
            if not ref_problem:
                raise ValueError(f"Problem {problem_id} not found")
            
            # Get all problems for comparison
            all_problems = self.db.query(Problem).all()
            
            # Calculate simplified similarity
            similarities = []
            for problem in all_problems:
                if problem.id == problem_id:
                    continue
                
                similarity_score = self._calculate_content_similarity(ref_problem, problem)
                similarities.append({
                    'problem': problem,
                    'similarity_score': similarity_score
                })
            
            # Sort by similarity and return top N
            similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            recommendations = []
            for item in similarities[:num_recommendations]:
                rec = item['problem'].to_dict()
                rec['similarity_score'] = item['similarity_score']
                rec['recommendation_reason'] = f"Similar to {ref_problem.title}"
                recommendations.append(rec)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating content-based recommendations: {str(e)}")
            return []
    
    def generate_learning_path(
        self,
        user_id: str,
        target_goal: str = "google_interview",
        current_level: str = "intermediate",
        duration_weeks: int = 8
    ) -> Dict[str, Any]:
        """
        Generate a simplified personalized learning path
        """
        try:
            # Get user's current skill assessment
            user_skills = self._assess_user_skills(user_id)
            
            # Define learning objectives based on goal
            objectives = self._get_learning_objectives(target_goal, current_level)
            
            # Select problems for the learning path
            path_problems = self._select_learning_path_problems(
                user_skills, objectives, duration_weeks
            )
            
            # Organize into weekly milestones
            weekly_plan = self._organize_weekly_plan(path_problems, duration_weeks)
            
            # Generate path metadata
            path_data = {
                'id': f"path_{user_id}_{target_goal}_{datetime.now().strftime('%Y%m%d')}",
                'user_id': user_id,
                'target_goal': target_goal,
                'current_level': current_level,
                'duration_weeks': duration_weeks,
                'total_problems': len(path_problems),
                'weekly_plan': weekly_plan,
                'skill_progression': objectives,
                'estimated_completion_time': self._estimate_completion_time(path_problems),
                'created_at': datetime.now().isoformat()
            }
            
            return path_data
            
        except Exception as e:
            logger.error(f"Error generating learning path: {str(e)}")
            return {}
    
    # Private helper methods
    
    def _get_user_history(self, user_id: str) -> List[UserInteraction]:
        """Get user's interaction history"""
        return self.db.query(UserInteraction).filter(
            UserInteraction.user_id == user_id
        ).order_by(UserInteraction.timestamp.desc()).all()
    
    def _get_candidate_problems(
        self,
        user_id: str,
        difficulty_preference: Optional[str],
        focus_areas: Optional[List[str]],
        exclude_solved: bool
    ) -> List[Problem]:
        """Get candidate problems for recommendation"""
        query = self.db.query(Problem)
        
        # Filter by difficulty if specified
        if difficulty_preference:
            query = query.filter(Problem.difficulty == difficulty_preference)
        
        # Filter by focus areas if specified
        if focus_areas:
            # Simplified filter - check if any focus area is in algorithm tags
            for area in focus_areas:
                query = query.filter(Problem.algorithm_tags.contains([area]))
        
        # Exclude solved problems if requested
        if exclude_solved:
            solved_problems = self.db.query(UserInteraction.problem_id).filter(
                UserInteraction.user_id == user_id,
                UserInteraction.action == 'solved'
            ).subquery()
            query = query.filter(~Problem.id.in_(solved_problems))
        
        return query.all()
    
    def _calculate_simplified_score(
        self,
        user_id: str,
        problem: Problem,
        user_history: List[UserInteraction]
    ) -> Dict[str, float]:
        """Calculate simplified recommendation score"""
        
        # Quality score (normalized)
        quality_score = (problem.quality_score or 0.0) / 100.0
        
        # Google interview relevance score (normalized)
        relevance_score = (problem.google_interview_relevance or 0.0) / 100.0
        
        # Popularity score (simplified)
        popularity_score = min(1.0, (problem.popularity_score or 0.0) / 50.0)
        
        # Difficulty progression score
        difficulty_score = self._calculate_difficulty_progression_score(problem, user_history)
        
        # Weighted total score
        total_score = (
            self.weights['content_based'] * (quality_score + relevance_score) / 2 +
            self.weights['collaborative'] * popularity_score +
            self.weights['popularity'] * quality_score +
            self.weights['difficulty_progression'] * difficulty_score
        )
        
        return {
            'quality_score': quality_score,
            'relevance_score': relevance_score,
            'popularity_score': popularity_score,
            'difficulty_score': difficulty_score,
            'total_score': total_score
        }
    
    def _calculate_difficulty_progression_score(
        self,
        problem: Problem,
        user_history: List[UserInteraction]
    ) -> float:
        """Calculate difficulty progression appropriateness score"""
        if not user_history:
            return 0.5  # Neutral score for new users
        
        # Analyze user's recent difficulty levels
        recent_difficulties = []
        for interaction in user_history[:10]:  # Last 10 interactions
            if interaction.problem and interaction.action == 'solved':
                recent_difficulties.append(interaction.problem.difficulty)
        
        if not recent_difficulties:
            return 0.5
        
        # Simple progression logic
        difficulty_levels = {'Easy': 1, 'Medium': 2, 'Hard': 3}
        avg_recent_difficulty = sum(difficulty_levels.get(d, 2) for d in recent_difficulties) / len(recent_difficulties)
        problem_difficulty = difficulty_levels.get(problem.difficulty, 2)
        
        # Prefer problems slightly above current level
        diff = problem_difficulty - avg_recent_difficulty
        if -0.5 <= diff <= 1.0:
            return 1.0
        elif diff > 1.0:
            return max(0.2, 1.0 - (diff - 1.0) * 0.3)
        else:
            return max(0.3, 1.0 + diff * 0.5)
    
    def _calculate_content_similarity(self, problem1: Problem, problem2: Problem) -> float:
        """Calculate simplified content similarity between two problems"""
        # Algorithm tags similarity
        tags1 = set(problem1.algorithm_tags or [])
        tags2 = set(problem2.algorithm_tags or [])
        
        if not tags1 or not tags2:
            tag_similarity = 0.0
        else:
            tag_similarity = len(tags1.intersection(tags2)) / len(tags1.union(tags2))
        
        # Difficulty similarity
        difficulty_levels = {'Easy': 1, 'Medium': 2, 'Hard': 3}
        diff1 = difficulty_levels.get(problem1.difficulty, 2)
        diff2 = difficulty_levels.get(problem2.difficulty, 2)
        difficulty_similarity = 1.0 - abs(diff1 - diff2) / 2.0
        
        # Combined similarity
        return 0.7 * tag_similarity + 0.3 * difficulty_similarity
    
    def _generate_reasoning(
        self,
        problem: Problem,
        score_breakdown: Dict[str, float],
        user_history: List[UserInteraction]
    ) -> str:
        """Generate human-readable recommendation reasoning"""
        reasons = []
        
        if score_breakdown.get('relevance_score', 0) > 0.7:
            reasons.append("Highly relevant for Google interviews")
        
        if score_breakdown.get('quality_score', 0) > 0.8:
            reasons.append("High-quality problem with excellent explanations")
        
        if score_breakdown.get('difficulty_score', 0) > 0.8:
            reasons.append("Perfect difficulty progression")
        
        if score_breakdown.get('popularity_score', 0) > 0.6:
            reasons.append("Popular among users")
        
        if not reasons:
            reasons.append("Good match for your learning goals")
        
        return "; ".join(reasons)
    
    def _get_fallback_recommendations(self, num_recommendations: int) -> List[Dict[str, Any]]:
        """Get fallback recommendations when other methods fail"""
        try:
            problems = self.db.query(Problem).order_by(
                Problem.google_interview_relevance.desc(),
                Problem.quality_score.desc()
            ).limit(num_recommendations).all()
            
            recommendations = []
            for problem in problems:
                rec = problem.to_dict()
                rec['recommendation_score'] = 0.5
                rec['recommendation_reasoning'] = "Fallback recommendation based on quality"
                recommendations.append(rec)
            
            return recommendations
        except Exception as e:
            logger.error(f"Error getting fallback recommendations: {str(e)}")
            return []
    
    def _assess_user_skills(self, user_id: str) -> Dict[str, float]:
        """Simplified user skill assessment"""
        interactions = self.db.query(UserInteraction).filter(
            UserInteraction.user_id == user_id,
            UserInteraction.action == 'solved'
        ).all()
        
        skills = {
            'arrays': 0.5,
            'strings': 0.5,
            'trees': 0.5,
            'graphs': 0.5,
            'dynamic_programming': 0.5,
            'sorting': 0.5,
            'searching': 0.5
        }
        
        # Update skills based on solved problems
        for interaction in interactions:
            if interaction.problem and interaction.problem.algorithm_tags:
                for tag in interaction.problem.algorithm_tags:
                    if tag.lower() in skills:
                        skills[tag.lower()] = min(1.0, skills[tag.lower()] + 0.1)
        
        return skills
    
    def _get_learning_objectives(self, target_goal: str, current_level: str) -> List[str]:
        """Define learning objectives based on goal and level"""
        objectives = {
            'google_interview': {
                'beginner': ['arrays', 'strings', 'hash_tables', 'two_pointers'],
                'intermediate': ['trees', 'graphs', 'dynamic_programming', 'binary_search'],
                'advanced': ['advanced_dp', 'graph_algorithms', 'system_design', 'optimization']
            },
            'competitive': {
                'beginner': ['math', 'greedy', 'implementation', 'brute_force'],
                'intermediate': ['dp', 'graphs', 'number_theory', 'geometry'],
                'advanced': ['advanced_structures', 'flow_networks', 'string_algorithms']
            }
        }
        
        return objectives.get(target_goal, {}).get(current_level, ['general_practice'])
    
    def _select_learning_path_problems(
        self,
        user_skills: Dict[str, float],
        objectives: List[str],
        duration_weeks: int
    ) -> List[Problem]:
        """Select problems for the learning path based on objectives"""
        target_problems_per_week = 5
        total_problems = duration_weeks * target_problems_per_week
        
        problems = []
        for objective in objectives:
            # Get problems related to this objective
            obj_problems = self.db.query(Problem).filter(
                Problem.algorithm_tags.contains([objective])
            ).order_by(
                Problem.google_interview_relevance.desc(),
                Problem.quality_score.desc()
            ).limit(total_problems // len(objectives) if objectives else total_problems).all()
            
            problems.extend(obj_problems)
        
        return problems[:total_problems]
    
    def _organize_weekly_plan(self, problems: List[Problem], duration_weeks: int) -> List[Dict[str, Any]]:
        """Organize problems into weekly learning plan"""
        problems_per_week = max(1, len(problems) // duration_weeks)
        weekly_plan = []
        
        for week in range(duration_weeks):
            start_idx = week * problems_per_week
            end_idx = start_idx + problems_per_week
            week_problems = problems[start_idx:end_idx]
            
            if not week_problems and problems:  # Handle remaining problems
                week_problems = problems[start_idx:]
            
            focus_areas = []
            for p in week_problems:
                if p.algorithm_tags:
                    focus_areas.extend(p.algorithm_tags)
            focus_areas = list(set(focus_areas))[:3]  # Top 3 unique focus areas
            
            weekly_plan.append({
                'week': week + 1,
                'problems': [p.to_dict() for p in week_problems],
                'focus_areas': focus_areas,
                'estimated_hours': len(week_problems) * 2  # 2 hours per problem estimate
            })
        
        return weekly_plan
    
    def _estimate_completion_time(self, problems: List[Problem]) -> Dict[str, int]:
        """Estimate completion time for the learning path"""
        easy_count = sum(1 for p in problems if p.difficulty == 'Easy')
        medium_count = sum(1 for p in problems if p.difficulty == 'Medium')
        hard_count = sum(1 for p in problems if p.difficulty == 'Hard')
        
        # Time estimates in hours
        total_hours = easy_count * 1.5 + medium_count * 2.5 + hard_count * 4.0
        
        return {
            'total_hours': int(total_hours),
            'hours_per_week': int(total_hours / 8),  # Assuming 8-week default
            'easy_problems': easy_count,
            'medium_problems': medium_count,
            'hard_problems': hard_count
        }

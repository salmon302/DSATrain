"""
Enhanced ML Recommendation Engine for DSA Training Platform
Implements collaborative filtering, content-based recommendations, and learning paths
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import logging
from datetime import datetime, timedelta
import json

from ..models.database import Problem, Solution, UserInteraction, LearningPath

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """
    Advanced ML recommendation engine providing personalized problem suggestions
    using collaborative filtering, content-based filtering, and learning path optimization
    """
    
    def __init__(self, db_session: Session):
        """Initialize the recommendation engine with database session"""
        self.db = db_session
        self.tfidf_vectorizer = None
        self.problem_features_matrix = None
        self.scaler = StandardScaler()
        self.is_trained = False
        
        # Recommendation weights
        self.weights = {
            'content_based': 0.4,
            'collaborative': 0.3,
            'popularity': 0.2,
            'difficulty_progression': 0.1
        }
    
    def train_models(self) -> None:
        """
        Train all ML models using current database data
        This should be called when new data is added or periodically
        """
        try:
            logger.info("Training ML recommendation models...")
            
            # Load and prepare data
            problems_df = self._load_problems_data()
            if problems_df.empty:
                logger.warning("No problems data available for training")
                return
            
            # Train content-based model
            self._train_content_based_model(problems_df)
            
            # Train collaborative filtering model
            self._train_collaborative_model()
            
            self.is_trained = True
            logger.info("ML models training completed successfully")
            
        except Exception as e:
            logger.error(f"Error training ML models: {str(e)}")
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
        Get personalized recommendations for a specific user
        
        Args:
            user_id: Unique user identifier
            num_recommendations: Number of recommendations to return
            difficulty_preference: Preferred difficulty level
            focus_areas: List of algorithm/topic areas to focus on
            exclude_solved: Whether to exclude already solved problems
            
        Returns:
            List of recommended problems with scores and reasoning
        """
        try:
            if not self.is_trained:
                logger.warning("Models not trained, training now...")
                self.train_models()
            
            # Get user interaction history
            user_history = self._get_user_history(user_id)
            
            # Get candidate problems
            candidates = self._get_candidate_problems(
                user_id, difficulty_preference, focus_areas, exclude_solved
            )
            
            if not candidates:
                logger.warning(f"No candidate problems found for user {user_id}")
                return self._get_fallback_recommendations(num_recommendations)
            
            # Calculate recommendation scores
            recommendations = []
            for problem in candidates:
                score_breakdown = self._calculate_recommendation_score(
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
        Get problems similar to a given problem using content-based filtering
        
        Args:
            problem_id: ID of the reference problem
            num_recommendations: Number of similar problems to return
            
        Returns:
            List of similar problems with similarity scores
        """
        try:
            if not self.is_trained:
                self.train_models()
            
            # Get the reference problem
            ref_problem = self.db.query(Problem).filter(Problem.id == problem_id).first()
            if not ref_problem:
                raise ValueError(f"Problem {problem_id} not found")
            
            # Get all problems for comparison
            all_problems = self.db.query(Problem).all()
            
            # Calculate content similarity
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
        Generate a personalized learning path for a user
        
        Args:
            user_id: Unique user identifier
            target_goal: Learning objective (google_interview, competitive, general)
            current_level: Current skill level (beginner, intermediate, advanced)
            duration_weeks: Target duration in weeks
            
        Returns:
            Structured learning path with problem sequence and milestones
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
    
    def update_user_interaction(
        self,
        user_id: str,
        problem_id: str,
        action: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Record user interaction for ML model improvement
        
        Args:
            user_id: Unique user identifier
            problem_id: Problem that was interacted with
            action: Type of interaction (viewed, solved, bookmarked, etc.)
            metadata: Additional interaction context
        """
        try:
            # Create new interaction record
            interaction = UserInteraction(
                user_id=user_id,
                problem_id=problem_id,
                action=action,
                interaction_metadata=metadata or {},
                timestamp=datetime.now()
            )
            
            self.db.add(interaction)
            self.db.commit()
            
            logger.info(f"Recorded interaction: {user_id} {action} {problem_id}")
            
        except Exception as e:
            logger.error(f"Error recording user interaction: {str(e)}")
            self.db.rollback()
    
    # Private methods for internal ML operations
    
    def _load_problems_data(self) -> pd.DataFrame:
        """Load problems data into pandas DataFrame for ML processing"""
        problems = self.db.query(Problem).all()
        
        data = []
        for problem in problems:
            data.append({
                'id': problem.id,
                'platform': problem.platform,
                'title': problem.title,
                'difficulty': problem.difficulty,
                'category': problem.category,
                'algorithm_tags': json.dumps(problem.algorithm_tags) if problem.algorithm_tags else '[]',
                'data_structures': json.dumps(problem.data_structures) if problem.data_structures else '[]',
                'google_interview_relevance': problem.google_interview_relevance or 0.0,
                'quality_score': problem.quality_score or 0.0,
                'popularity_score': problem.popularity_score or 0.0,
                'companies': json.dumps(problem.companies) if problem.companies else '[]'
            })
        
        return pd.DataFrame(data)
    
    def _train_content_based_model(self, problems_df: pd.DataFrame) -> None:
        """Train content-based recommendation model using TF-IDF"""
        # Combine text features for TF-IDF
        text_features = []
        for _, row in problems_df.iterrows():
            features = [
                row['title'],
                row['category'] or '',
                row['algorithm_tags'],
                row['data_structures'],
                row['difficulty']
            ]
            text_features.append(' '.join(str(f) for f in features))
        
        # Train TF-IDF vectorizer
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.problem_features_matrix = self.tfidf_vectorizer.fit_transform(text_features)
        
        logger.info(f"Content-based model trained with {len(text_features)} problems")
    
    def _train_collaborative_model(self) -> None:
        """Train collaborative filtering model"""
        # For now, we'll use a simple popularity-based approach
        # In production, you would implement matrix factorization or deep learning
        interactions = self.db.query(UserInteraction).all()
        
        if not interactions:
            logger.warning("No user interactions available for collaborative filtering")
            return
        
        # Calculate problem popularity scores based on interactions
        problem_popularity = {}
        for interaction in interactions:
            if interaction.problem_id not in problem_popularity:
                problem_popularity[interaction.problem_id] = 0
            
            # Weight different actions differently
            weights = {'viewed': 1, 'solved': 5, 'bookmarked': 3, 'rated': 2}
            weight = weights.get(interaction.action, 1)
            problem_popularity[interaction.problem_id] += weight
        
        # Update popularity scores in database
        for problem_id, score in problem_popularity.items():
            problem = self.db.query(Problem).filter(Problem.id == problem_id).first()
            if problem:
                problem.popularity_score = score
        
        self.db.commit()
        logger.info(f"Collaborative model trained with {len(interactions)} interactions")
    
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
            # This is a simplified filter - in production, use proper JSON queries
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
    
    def _calculate_recommendation_score(
        self,
        user_id: str,
        problem: Problem,
        user_history: List[UserInteraction]
    ) -> Dict[str, float]:
        """Calculate comprehensive recommendation score for a problem"""
        
        # Content-based score
        content_score = self._calculate_content_score(problem, user_history)
        
        # Collaborative score
        collaborative_score = self._calculate_collaborative_score(problem, user_id)
        
        # Popularity score
        popularity_score = (problem.popularity_score or 0.0) / 100.0  # Normalize to 0-1
        
        # Difficulty progression score
        difficulty_score = self._calculate_difficulty_progression_score(problem, user_history)
        
        # Weighted total score
        total_score = (
            self.weights['content_based'] * content_score +
            self.weights['collaborative'] * collaborative_score +
            self.weights['popularity'] * popularity_score +
            self.weights['difficulty_progression'] * difficulty_score
        )
        
        return {
            'content_score': content_score,
            'collaborative_score': collaborative_score,
            'popularity_score': popularity_score,
            'difficulty_score': difficulty_score,
            'total_score': total_score
        }
    
    def _calculate_content_score(self, problem: Problem, user_history: List[UserInteraction]) -> float:
        """Calculate content-based recommendation score"""
        # Simple implementation - in production, use proper ML similarity
        base_score = (problem.google_interview_relevance or 0.0) / 100.0
        quality_bonus = (problem.quality_score or 0.0) / 100.0
        
        return min(1.0, base_score + quality_bonus * 0.2)
    
    def _calculate_collaborative_score(self, problem: Problem, user_id: str) -> float:
        """Calculate collaborative filtering score"""
        # Simple implementation - in production, use matrix factorization
        return min(1.0, (problem.popularity_score or 0.0) / 50.0)
    
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
        avg_recent_difficulty = np.mean([difficulty_levels.get(d, 2) for d in recent_difficulties])
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
        """Calculate content similarity between two problems"""
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
        
        if score_breakdown['content_score'] > 0.7:
            reasons.append("Highly relevant for Google interviews")
        
        if score_breakdown['collaborative_score'] > 0.6:
            reasons.append("Popular among similar users")
        
        if score_breakdown['difficulty_score'] > 0.8:
            reasons.append("Perfect difficulty progression")
        
        if problem.quality_score and problem.quality_score > 85:
            reasons.append("High-quality problem with excellent explanations")
        
        if not reasons:
            reasons.append("Good match for your learning goals")
        
        return "; ".join(reasons)
    
    def _get_fallback_recommendations(self, num_recommendations: int) -> List[Dict[str, Any]]:
        """Get fallback recommendations when ML models fail"""
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
        """Assess user's current skill levels across different areas"""
        # Simplified skill assessment - in production, use more sophisticated analysis
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
    
    def _get_learning_objectives(self, target_goal: str, current_level: str) -> Dict[str, Any]:
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
            ).limit(total_problems // len(objectives)).all()
            
            problems.extend(obj_problems)
        
        return problems[:total_problems]
    
    def _organize_weekly_plan(self, problems: List[Problem], duration_weeks: int) -> List[Dict[str, Any]]:
        """Organize problems into weekly learning plan"""
        problems_per_week = len(problems) // duration_weeks
        weekly_plan = []
        
        for week in range(duration_weeks):
            start_idx = week * problems_per_week
            end_idx = start_idx + problems_per_week
            week_problems = problems[start_idx:end_idx]
            
            weekly_plan.append({
                'week': week + 1,
                'problems': [p.to_dict() for p in week_problems],
                'focus_areas': list(set([tag for p in week_problems for tag in (p.algorithm_tags or [])]))[:3],
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

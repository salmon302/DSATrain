"""
User Behavior Tracking Module for DSA Training Platform
Provides comprehensive user interaction tracking and analytics for ML training
"""

from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json
import logging
from collections import defaultdict

from ..models.database import UserInteraction, Problem, Solution

logger = logging.getLogger(__name__)


class UserBehaviorTracker:
    """
    Comprehensive user behavior tracking and analytics system
    Collects and analyzes user interactions for ML recommendation improvement
    """
    
    def __init__(self, db_session: Session):
        """Initialize the behavior tracker with database session"""
        self.db = db_session
    
    def track_problem_view(
        self,
        user_id: str,
        problem_id: str,
        time_spent_seconds: Optional[int] = None,
        session_id: Optional[str] = None,
        device_type: str = "web",
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Track when a user views a problem
        
        Args:
            user_id: Unique user identifier
            problem_id: Problem that was viewed
            time_spent_seconds: Time spent viewing the problem
            session_id: User session identifier
            device_type: Device used (web, mobile, etc.)
            metadata: Additional context data
        """
        try:
            interaction = UserInteraction(
                user_id=user_id,
                problem_id=problem_id,
                action='viewed',
                time_spent_seconds=time_spent_seconds,
                session_id=session_id,
                device_type=device_type,
                interaction_metadata=metadata or {},
                timestamp=datetime.now()
            )
            
            self.db.add(interaction)
            self.db.commit()
            
            logger.debug(f"Tracked problem view: {user_id} -> {problem_id}")
            
        except Exception as e:
            logger.error(f"Error tracking problem view: {str(e)}")
            self.db.rollback()
    
    def track_problem_attempt(
        self,
        user_id: str,
        problem_id: str,
        success: bool,
        time_spent_seconds: int,
        approach_used: Optional[str] = None,
        difficulty_perceived: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Track when a user attempts to solve a problem
        
        Args:
            user_id: Unique user identifier
            problem_id: Problem that was attempted
            success: Whether the attempt was successful
            time_spent_seconds: Time spent on the attempt
            approach_used: Algorithm/approach used
            difficulty_perceived: User's perceived difficulty
            session_id: User session identifier
            metadata: Additional context data
        """
        try:
            action = 'solved' if success else 'attempted'
            
            # Prepare metadata
            attempt_metadata = metadata or {}
            attempt_metadata.update({
                'approach_used': approach_used,
                'difficulty_perceived': difficulty_perceived,
                'success': success
            })
            
            interaction = UserInteraction(
                user_id=user_id,
                problem_id=problem_id,
                action=action,
                success=success,
                time_spent_seconds=time_spent_seconds,
                session_id=session_id,
                interaction_metadata=attempt_metadata,
                timestamp=datetime.now()
            )
            
            self.db.add(interaction)
            self.db.commit()
            
            logger.info(f"Tracked problem attempt: {user_id} {action} {problem_id}")
            
        except Exception as e:
            logger.error(f"Error tracking problem attempt: {str(e)}")
            self.db.rollback()
    
    def track_solution_view(
        self,
        user_id: str,
        solution_id: str,
        time_spent_seconds: Optional[int] = None,
        helpful_rating: Optional[int] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Track when a user views a solution
        
        Args:
            user_id: Unique user identifier
            solution_id: Solution that was viewed
            time_spent_seconds: Time spent viewing the solution
            helpful_rating: User rating of solution helpfulness (1-5)
            session_id: User session identifier
            metadata: Additional context data
        """
        try:
            solution_metadata = metadata or {}
            if helpful_rating:
                solution_metadata['helpful_rating'] = helpful_rating
            
            interaction = UserInteraction(
                user_id=user_id,
                solution_id=solution_id,
                action='viewed_solution',
                rating=helpful_rating,
                time_spent_seconds=time_spent_seconds,
                session_id=session_id,
                interaction_metadata=solution_metadata,
                timestamp=datetime.now()
            )
            
            self.db.add(interaction)
            self.db.commit()
            
            logger.debug(f"Tracked solution view: {user_id} -> {solution_id}")
            
        except Exception as e:
            logger.error(f"Error tracking solution view: {str(e)}")
            self.db.rollback()
    
    def track_bookmark_action(
        self,
        user_id: str,
        problem_id: str,
        action: str = "bookmarked",  # bookmarked or unbookmarked
        session_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Track when a user bookmarks or unbookmarks a problem
        
        Args:
            user_id: Unique user identifier
            problem_id: Problem that was bookmarked
            action: Bookmark action (bookmarked/unbookmarked)
            session_id: User session identifier
            metadata: Additional context data
        """
        try:
            interaction = UserInteraction(
                user_id=user_id,
                problem_id=problem_id,
                action=action,
                session_id=session_id,
                interaction_metadata=metadata or {},
                timestamp=datetime.now()
            )
            
            self.db.add(interaction)
            self.db.commit()
            
            logger.debug(f"Tracked bookmark action: {user_id} {action} {problem_id}")
            
        except Exception as e:
            logger.error(f"Error tracking bookmark action: {str(e)}")
            self.db.rollback()
    
    def track_learning_path_progress(
        self,
        user_id: str,
        learning_path_id: str,
        problem_id: str,
        progress_percentage: float,
        session_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Track progress on a learning path
        
        Args:
            user_id: Unique user identifier
            learning_path_id: Learning path being followed
            problem_id: Current problem in the path
            progress_percentage: Overall progress percentage (0-100)
            session_id: User session identifier
            metadata: Additional context data
        """
        try:
            path_metadata = metadata or {}
            path_metadata.update({
                'progress_percentage': progress_percentage,
                'learning_path_id': learning_path_id
            })
            
            interaction = UserInteraction(
                user_id=user_id,
                problem_id=problem_id,
                action='learning_path_progress',
                learning_path_id=learning_path_id,
                session_id=session_id,
                interaction_metadata=path_metadata,
                timestamp=datetime.now()
            )
            
            self.db.add(interaction)
            self.db.commit()
            
            logger.debug(f"Tracked learning path progress: {user_id} -> {learning_path_id} ({progress_percentage}%)")
            
        except Exception as e:
            logger.error(f"Error tracking learning path progress: {str(e)}")
            self.db.rollback()
    
    def get_user_analytics(
        self,
        user_id: str,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Get comprehensive analytics for a user
        
        Args:
            user_id: Unique user identifier
            days_back: Number of days to look back for analytics
            
        Returns:
            Comprehensive user analytics dictionary
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            # Get all interactions for the user in the time period
            interactions = self.db.query(UserInteraction).filter(
                UserInteraction.user_id == user_id,
                UserInteraction.timestamp >= cutoff_date
            ).order_by(UserInteraction.timestamp.desc()).all()
            
            if not interactions:
                return self._get_empty_analytics(user_id)
            
            # Calculate various analytics
            analytics = {
                'user_id': user_id,
                'period_days': days_back,
                'total_interactions': len(interactions),
                'activity_summary': self._calculate_activity_summary(interactions),
                'problem_solving_stats': self._calculate_solving_stats(interactions),
                'learning_patterns': self._analyze_learning_patterns(interactions),
                'skill_progression': self._analyze_skill_progression(interactions),
                'time_analytics': self._analyze_time_patterns(interactions),
                'difficulty_preferences': self._analyze_difficulty_preferences(interactions),
                'generated_at': datetime.now().isoformat()
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error generating user analytics: {str(e)}")
            return self._get_empty_analytics(user_id)
    
    def get_recommendation_feedback(
        self,
        user_id: str,
        recommendation_session_id: str
    ) -> Dict[str, Any]:
        """
        Analyze user feedback on recommendations
        
        Args:
            user_id: Unique user identifier
            recommendation_session_id: Session ID when recommendations were given
            
        Returns:
            Feedback analysis on recommendation quality
        """
        try:
            # Get interactions following the recommendation session
            interactions = self.db.query(UserInteraction).filter(
                UserInteraction.user_id == user_id,
                UserInteraction.session_id == recommendation_session_id
            ).all()
            
            feedback = {
                'session_id': recommendation_session_id,
                'total_interactions': len(interactions),
                'problems_viewed': 0,
                'problems_attempted': 0,
                'problems_solved': 0,
                'problems_bookmarked': 0,
                'average_time_per_problem': 0,
                'recommendation_score': 0.0
            }
            
            if interactions:
                feedback.update(self._analyze_recommendation_interactions(interactions))
            
            return feedback
            
        except Exception as e:
            logger.error(f"Error analyzing recommendation feedback: {str(e)}")
            return {}
    
    def get_popular_trends(self, days_back: int = 7) -> Dict[str, Any]:
        """
        Get trending problems and patterns across all users
        
        Args:
            days_back: Number of days to analyze for trends
            
        Returns:
            Trending problems and user behavior patterns
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            interactions = self.db.query(UserInteraction).filter(
                UserInteraction.timestamp >= cutoff_date
            ).all()
            
            trends = {
                'period_days': days_back,
                'trending_problems': self._get_trending_problems(interactions),
                'popular_algorithms': self._get_popular_algorithms(interactions),
                'difficulty_distribution': self._get_difficulty_distribution(interactions),
                'peak_activity_hours': self._get_peak_activity_hours(interactions),
                'average_session_length': self._get_average_session_length(interactions),
                'generated_at': datetime.now().isoformat()
            }
            
            return trends
            
        except Exception as e:
            logger.error(f"Error generating trend analysis: {str(e)}")
            return {}
    
    # Private analytics methods
    
    def _get_empty_analytics(self, user_id: str) -> Dict[str, Any]:
        """Return empty analytics structure for users with no data"""
        return {
            'user_id': user_id,
            'total_interactions': 0,
            'message': 'No interaction data available',
            'generated_at': datetime.now().isoformat()
        }
    
    def _calculate_activity_summary(self, interactions: List[UserInteraction]) -> Dict[str, Any]:
        """Calculate basic activity summary"""
        action_counts = defaultdict(int)
        for interaction in interactions:
            action_counts[interaction.action] += 1
        
        return {
            'actions': dict(action_counts),
            'most_common_action': max(action_counts.items(), key=lambda x: x[1])[0] if action_counts else None,
            'unique_problems': len(set(i.problem_id for i in interactions if i.problem_id)),
            'unique_sessions': len(set(i.session_id for i in interactions if i.session_id))
        }
    
    def _calculate_solving_stats(self, interactions: List[UserInteraction]) -> Dict[str, Any]:
        """Calculate problem-solving statistics"""
        solve_interactions = [i for i in interactions if i.action in ['solved', 'attempted']]
        
        if not solve_interactions:
            return {'solved': 0, 'attempted': 0, 'success_rate': 0.0}
        
        solved_count = len([i for i in solve_interactions if i.action == 'solved'])
        attempted_count = len(solve_interactions)
        
        return {
            'solved': solved_count,
            'attempted': attempted_count,
            'success_rate': solved_count / attempted_count if attempted_count > 0 else 0.0,
            'average_solve_time': self._calculate_average_solve_time(solve_interactions)
        }
    
    def _analyze_learning_patterns(self, interactions: List[UserInteraction]) -> Dict[str, Any]:
        """Analyze user learning patterns"""
        # Group interactions by day
        daily_activity = defaultdict(int)
        for interaction in interactions:
            day = interaction.timestamp.date()
            daily_activity[day] += 1
        
        # Calculate learning consistency
        active_days = len(daily_activity)
        total_days = (max(daily_activity.keys()) - min(daily_activity.keys())).days + 1 if daily_activity else 1
        consistency_score = active_days / total_days if total_days > 0 else 0.0
        
        return {
            'active_days': active_days,
            'total_days_period': total_days,
            'consistency_score': consistency_score,
            'average_daily_interactions': sum(daily_activity.values()) / len(daily_activity) if daily_activity else 0
        }
    
    def _analyze_skill_progression(self, interactions: List[UserInteraction]) -> Dict[str, Any]:
        """Analyze skill progression over time"""
        skill_interactions = []
        for interaction in interactions:
            if interaction.problem and interaction.action == 'solved':
                skill_interactions.append({
                    'timestamp': interaction.timestamp,
                    'difficulty': interaction.problem.difficulty,
                    'algorithms': interaction.problem.algorithm_tags or []
                })
        
        if not skill_interactions:
            return {'progression': 'No solved problems to analyze'}
        
        # Sort by timestamp
        skill_interactions.sort(key=lambda x: x['timestamp'])
        
        # Analyze difficulty progression
        difficulties = [s['difficulty'] for s in skill_interactions]
        difficulty_trend = self._calculate_difficulty_trend(difficulties)
        
        return {
            'total_solved': len(skill_interactions),
            'difficulty_progression': difficulty_trend,
            'algorithm_coverage': list(set([alg for s in skill_interactions for alg in s['algorithms']]))
        }
    
    def _analyze_time_patterns(self, interactions: List[UserInteraction]) -> Dict[str, Any]:
        """Analyze time-based patterns"""
        if not interactions:
            return {}
        
        # Hour distribution
        hour_counts = defaultdict(int)
        for interaction in interactions:
            hour_counts[interaction.timestamp.hour] += 1
        
        # Time spent analysis
        time_spent_values = [i.time_spent_seconds for i in interactions if i.time_spent_seconds]
        
        return {
            'most_active_hours': sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'average_time_per_interaction': sum(time_spent_values) / len(time_spent_values) if time_spent_values else 0,
            'total_time_spent_hours': sum(time_spent_values) / 3600 if time_spent_values else 0
        }
    
    def _analyze_difficulty_preferences(self, interactions: List[UserInteraction]) -> Dict[str, Any]:
        """Analyze user difficulty preferences"""
        difficulty_counts = defaultdict(int)
        
        for interaction in interactions:
            if interaction.problem and interaction.action in ['viewed', 'solved', 'attempted']:
                difficulty_counts[interaction.problem.difficulty] += 1
        
        if not difficulty_counts:
            return {}
        
        total = sum(difficulty_counts.values())
        preferences = {
            difficulty: count / total 
            for difficulty, count in difficulty_counts.items()
        }
        
        return {
            'preferences': preferences,
            'most_preferred': max(preferences.items(), key=lambda x: x[1])[0] if preferences else None
        }
    
    def _calculate_average_solve_time(self, solve_interactions: List[UserInteraction]) -> float:
        """Calculate average time to solve problems"""
        solve_times = [
            i.time_spent_seconds for i in solve_interactions 
            if i.time_spent_seconds and i.action == 'solved'
        ]
        return sum(solve_times) / len(solve_times) if solve_times else 0.0
    
    def _calculate_difficulty_trend(self, difficulties: List[str]) -> str:
        """Calculate if user is progressing in difficulty"""
        if len(difficulties) < 2:
            return "insufficient_data"
        
        difficulty_values = {'Easy': 1, 'Medium': 2, 'Hard': 3}
        values = [difficulty_values.get(d, 2) for d in difficulties]
        
        # Simple trend analysis
        recent_avg = sum(values[-5:]) / min(5, len(values))
        early_avg = sum(values[:5]) / min(5, len(values))
        
        if recent_avg > early_avg + 0.3:
            return "increasing"
        elif recent_avg < early_avg - 0.3:
            return "decreasing"
        else:
            return "stable"
    
    def _analyze_recommendation_interactions(self, interactions: List[UserInteraction]) -> Dict[str, Any]:
        """Analyze interactions following recommendations"""
        feedback = {}
        
        for action in ['viewed', 'attempted', 'solved', 'bookmarked']:
            feedback[f'problems_{action}'] = len([i for i in interactions if i.action == action])
        
        # Calculate engagement score
        view_count = feedback.get('problems_viewed', 0)
        solve_count = feedback.get('problems_solved', 0)
        
        if view_count > 0:
            engagement_score = (solve_count / view_count) * 100
        else:
            engagement_score = 0.0
        
        feedback['recommendation_score'] = engagement_score
        
        return feedback
    
    def _get_trending_problems(self, interactions: List[UserInteraction]) -> List[Dict[str, Any]]:
        """Get trending problems based on recent interactions"""
        problem_scores = defaultdict(int)
        
        for interaction in interactions:
            if interaction.problem_id:
                # Weight different actions
                weights = {'viewed': 1, 'solved': 5, 'attempted': 3, 'bookmarked': 2}
                weight = weights.get(interaction.action, 1)
                problem_scores[interaction.problem_id] += weight
        
        # Get top trending problems
        sorted_problems = sorted(problem_scores.items(), key=lambda x: x[1], reverse=True)[:10]
        
        trending = []
        for problem_id, score in sorted_problems:
            problem = self.db.query(Problem).filter(Problem.id == problem_id).first()
            if problem:
                trending.append({
                    'problem_id': problem_id,
                    'title': problem.title,
                    'platform': problem.platform,
                    'difficulty': problem.difficulty,
                    'trend_score': score
                })
        
        return trending
    
    def _get_popular_algorithms(self, interactions: List[UserInteraction]) -> List[Dict[str, Any]]:
        """Get popular algorithm topics"""
        algorithm_counts = defaultdict(int)
        
        for interaction in interactions:
            if interaction.problem and interaction.problem.algorithm_tags:
                for tag in interaction.problem.algorithm_tags:
                    algorithm_counts[tag] += 1
        
        sorted_algorithms = sorted(algorithm_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return [{'algorithm': alg, 'interaction_count': count} for alg, count in sorted_algorithms]
    
    def _get_difficulty_distribution(self, interactions: List[UserInteraction]) -> Dict[str, int]:
        """Get difficulty distribution of interactions"""
        difficulty_counts = defaultdict(int)
        
        for interaction in interactions:
            if interaction.problem:
                difficulty_counts[interaction.problem.difficulty] += 1
        
        return dict(difficulty_counts)
    
    def _get_peak_activity_hours(self, interactions: List[UserInteraction]) -> List[int]:
        """Get peak activity hours"""
        hour_counts = defaultdict(int)
        
        for interaction in interactions:
            hour_counts[interaction.timestamp.hour] += 1
        
        sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        return [hour for hour, count in sorted_hours]
    
    def _get_average_session_length(self, interactions: List[UserInteraction]) -> float:
        """Calculate average session length"""
        session_times = defaultdict(list)
        
        for interaction in interactions:
            if interaction.session_id:
                session_times[interaction.session_id].append(interaction.timestamp)
        
        session_lengths = []
        for session_id, timestamps in session_times.items():
            if len(timestamps) > 1:
                timestamps.sort()
                length = (timestamps[-1] - timestamps[0]).total_seconds() / 60  # in minutes
                session_lengths.append(length)
        
        return sum(session_lengths) / len(session_lengths) if session_lengths else 0.0

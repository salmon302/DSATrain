"""
Advanced Learning Path Engine for DSATrain
Implements intelligent path generation, adaptation, and personalization
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging
import json
import uuid
from dataclasses import dataclass
from enum import Enum

from ..models.database import (
    Problem, Solution, UserInteraction, LearningPathTemplate,
    UserLearningPath, LearningMilestone, UserSkillAssessment
)

logger = logging.getLogger(__name__)


class SkillArea(Enum):
    """Core skill areas for assessment and learning paths"""
    ARRAYS = "arrays"
    STRINGS = "strings"
    HASH_TABLES = "hash_tables"
    TWO_POINTERS = "two_pointers"
    SLIDING_WINDOW = "sliding_window"
    TREES = "trees"
    GRAPHS = "graphs"
    DYNAMIC_PROGRAMMING = "dynamic_programming"
    GREEDY = "greedy"
    BINARY_SEARCH = "binary_search"
    SORTING = "sorting"
    BACKTRACKING = "backtracking"
    MATHEMATICS = "mathematics"
    BIT_MANIPULATION = "bit_manipulation"
    SYSTEM_DESIGN = "system_design"


class DifficultyLevel(Enum):
    """Problem difficulty levels"""
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


@dataclass
class UserProfile:
    """Comprehensive user profile for learning path generation"""
    user_id: str
    current_skill_levels: Dict[str, float]  # 0.0-1.0 for each skill area
    learning_goals: List[str]  # Target companies or objectives
    available_hours_per_week: int
    preferred_difficulty_curve: str  # gradual, moderate, steep
    target_completion_weeks: Optional[int] = None
    weak_areas: List[str] = None
    strong_areas: List[str] = None
    learning_style_preferences: Dict[str, Any] = None


@dataclass
class LearningObjective:
    """Specific learning objective within a path"""
    skill_area: str
    target_level: float  # 0.0-1.0
    priority: int  # 1-5, higher is more important
    prerequisite_skills: List[str]
    estimated_hours: int


class LearningPathEngine:
    """
    Advanced engine for generating and managing personalized learning paths
    """
    
    def __init__(self, db_session: Session):
        """Initialize the learning path engine"""
        self.db = db_session
        
        # Skill dependency graph - defines prerequisite relationships
        self.skill_dependencies = self._build_skill_dependency_graph()
        
        # Problem difficulty mapping for accurate progression
        self.difficulty_weights = {
            DifficultyLevel.EASY.value: 1.0,
            DifficultyLevel.MEDIUM.value: 2.5,
            DifficultyLevel.HARD.value: 4.0
        }
        
        # Learning path templates
        self.path_templates = self._load_path_templates()
    
    def generate_personalized_path(
        self,
        user_profile: UserProfile,
        template_id: Optional[str] = None
    ) -> UserLearningPath:
        """
        Generate a personalized learning path for a user
        
        Args:
            user_profile: Comprehensive user profile
            template_id: Optional template to base the path on
            
        Returns:
            Personalized UserLearningPath instance
        """
        try:
            logger.info(f"Generating personalized path for user {user_profile.user_id}")
            
            # Step 1: Analyze skill gaps and learning objectives
            learning_objectives = self._analyze_learning_objectives(user_profile)
            
            # Step 2: Select or adapt template
            if template_id:
                template = self._get_template(template_id)
            else:
                template = self._select_optimal_template(user_profile, learning_objectives)
            
            # Step 3: Generate problem sequence
            problem_sequence = self._generate_problem_sequence(
                user_profile, learning_objectives, template
            )
            
            # Step 4: Create milestones
            milestones = self._create_learning_milestones(
                problem_sequence, learning_objectives, user_profile
            )
            
            # Step 5: Estimate timeline
            timeline = self._calculate_timeline(
                problem_sequence, user_profile.available_hours_per_week
            )
            
            # Step 6: Create personalized learning path
            path_id = f"path_{user_profile.user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            user_path = UserLearningPath(
                id=path_id,
                user_id=user_profile.user_id,
                template_id=template.id if template else None,
                name=self._generate_path_name(user_profile, learning_objectives),
                description=self._generate_path_description(user_profile, learning_objectives),
                personalized_sequence=problem_sequence,
                current_position=0,
                completion_percentage=0.0,
                problems_completed=[],
                adaptation_history=[],
                performance_metrics={
                    'initial_skill_levels': user_profile.current_skill_levels,
                    'learning_objectives': [obj.__dict__ for obj in learning_objectives],
                    'difficulty_preference': user_profile.preferred_difficulty_curve,
                    'target_goal': user_profile.learning_goals[0] if user_profile.learning_goals else 'google_interview',
                    'current_level': self._infer_skill_level(user_profile.current_skill_levels),
                    'duration_weeks': user_profile.target_completion_weeks or 8
                },
                skill_progression={},
                target_completion=timeline['target_completion'],
                estimated_completion=timeline['estimated_completion'],
                status='active'
            )
            
            # Save to database
            self.db.add(user_path)
            self.db.flush()  # Get the ID
            
            # Create milestones
            for milestone_data in milestones:
                milestone_order = milestone_data.pop('order', 0)  # Remove order from milestone_data
                milestone = LearningMilestone(
                    id=f"milestone_{path_id}_{milestone_order}",
                    learning_path_id=user_path.id,
                    **milestone_data
                )
                self.db.add(milestone)
            
            self.db.commit()
            
            logger.info(f"Created personalized path {path_id} with {len(problem_sequence)} problems and {len(milestones)} milestones")
            return user_path
            
        except Exception as e:
            logger.error(f"Error generating personalized path: {str(e)}")
            self.db.rollback()
            raise
    
    def adapt_learning_path(
        self,
        path_id: str,
        performance_data: Dict[str, Any],
        force_adaptation: bool = False
    ) -> Dict[str, Any]:
        """
        Adapt an existing learning path based on user performance
        
        Args:
            path_id: ID of the learning path to adapt
            performance_data: Recent performance metrics
            force_adaptation: Force adaptation even if not recommended
            
        Returns:
            Adaptation summary and changes made
        """
        try:
            path = self.db.query(UserLearningPath).filter(UserLearningPath.id == path_id).first()
            if not path:
                raise ValueError(f"Learning path {path_id} not found")
            
            # Analyze performance and determine if adaptation is needed
            adaptation_analysis = self._analyze_adaptation_need(path, performance_data)
            
            if not adaptation_analysis['needs_adaptation'] and not force_adaptation:
                return {
                    'adapted': False,
                    'reason': 'No adaptation needed',
                    'analysis': adaptation_analysis
                }
            
            # Perform adaptation
            adaptations = []
            
            # Difficulty adjustment
            if adaptation_analysis['difficulty_adjustment']:
                difficulty_changes = self._adapt_difficulty_progression(path, performance_data)
                adaptations.extend(difficulty_changes)
            
            # Problem sequence modification
            if adaptation_analysis['sequence_modification']:
                sequence_changes = self._adapt_problem_sequence(path, performance_data)
                adaptations.extend(sequence_changes)
            
            # Timeline adjustment
            if adaptation_analysis['timeline_adjustment']:
                timeline_changes = self._adapt_timeline(path, performance_data)
                adaptations.extend(timeline_changes)
            
            # Update path with adaptations
            self._apply_adaptations(path, adaptations)
            
            # Record adaptation history
            adaptation_record = {
                'timestamp': datetime.now().isoformat(),
                'trigger': adaptation_analysis['trigger'],
                'changes': adaptations,
                'performance_snapshot': performance_data
            }
            
            if not path.adaptation_history:
                path.adaptation_history = []
            path.adaptation_history.append(adaptation_record)
            
            self.db.commit()
            
            logger.info(f"Adapted learning path {path_id}: {len(adaptations)} changes made")
            
            return {
                'adapted': True,
                'changes': adaptations,
                'analysis': adaptation_analysis,
                'adaptation_record': adaptation_record
            }
            
        except Exception as e:
            logger.error(f"Error adapting learning path: {str(e)}")
            self.db.rollback()
            raise
    
    def get_next_problems(
        self,
        path_id: str,
        count: int = 5,
        include_context: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get the next problems in a learning path with learning context
        
        Args:
            path_id: ID of the learning path
            count: Number of problems to return
            include_context: Whether to include learning context and hints
            
        Returns:
            List of problems with learning context
        """
        try:
            path = self.db.query(UserLearningPath).filter(UserLearningPath.id == path_id).first()
            if not path:
                raise ValueError(f"Learning path {path_id} not found")
            
            current_pos = path.current_position
            sequence = path.personalized_sequence
            
            if current_pos >= len(sequence):
                return []  # Path completed
            
            # Get next problem IDs
            next_problem_ids = sequence[current_pos:current_pos + count]
            
            # Fetch problems with details
            problems = []
            for i, problem_id in enumerate(next_problem_ids):
                problem = self.db.query(Problem).filter(Problem.id == problem_id).first()
                if not problem:
                    logger.warning(f"Problem {problem_id} not found in database")
                    continue
                
                problem_data = problem.to_dict()
                
                if include_context:
                    # Add learning context
                    learning_context = self._generate_learning_context(
                        problem, path, current_pos + i
                    )
                    problem_data.update(learning_context)
                
                problems.append(problem_data)
            
            return problems
            
        except Exception as e:
            logger.error(f"Error getting next problems: {str(e)}")
            return []
    
    def assess_user_skills(
        self,
        user_id: str,
        assessment_problems: Optional[List[str]] = None,
        assessment_type: str = "comprehensive"
    ) -> Dict[str, float]:
        """
        Assess user's current skill levels across different areas
        
        Args:
            user_id: User to assess
            assessment_problems: Specific problems to use for assessment
            assessment_type: Type of assessment (comprehensive, quick, focused)
            
        Returns:
            Dictionary of skill area -> proficiency level (0.0-1.0)
        """
        try:
            # Get user's interaction history
            interactions = self.db.query(UserInteraction).filter(
                UserInteraction.user_id == user_id
            ).order_by(UserInteraction.timestamp.desc()).all()
            
            if not interactions:
                # Return default beginner levels
                return {skill.value: 0.3 for skill in SkillArea}
            
            # Analyze performance by skill area
            skill_assessments = {}
            
            for skill in SkillArea:
                skill_level = self._assess_skill_area(skill.value, interactions)
                skill_assessments[skill.value] = skill_level
            
            # Save assessment to database
            for skill_area, level in skill_assessments.items():
                assessment = UserSkillAssessment(
                    user_id=user_id,
                    skill_area=skill_area,
                    skill_level=level,
                    assessment_type=assessment_type,
                    problem_ids=[i.problem_id for i in interactions[:50]],  # Recent problems
                    performance_data={
                        'total_problems_solved': len([i for i in interactions if i.action == 'solved']),
                        'recent_success_rate': self._calculate_recent_success_rate(interactions),
                        'average_solve_time': self._calculate_average_solve_time(interactions)
                    }
                )
                self.db.add(assessment)
            
            self.db.commit()
            return skill_assessments
            
        except Exception as e:
            logger.error(f"Error assessing user skills: {str(e)}")
            return {skill.value: 0.5 for skill in SkillArea}
    
    def update_path_progress(
        self,
        path_id: str,
        problem_id: str,
        success: bool,
        time_spent_seconds: int,
        additional_metrics: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Update learning path progress when a user completes a problem
        
        Args:
            path_id: Learning path ID
            problem_id: Problem that was completed
            success: Whether the problem was solved successfully
            time_spent_seconds: Time spent on the problem
            additional_metrics: Additional performance metrics
            
        Returns:
            Updated progress information
        """
        try:
            path = self.db.query(UserLearningPath).filter(UserLearningPath.id == path_id).first()
            if not path:
                raise ValueError(f"Learning path {path_id} not found")
            
            # Update completed problems
            if success and problem_id not in path.problems_completed:
                path.problems_completed.append(problem_id)
            
            # Update current position if this was the next problem
            sequence = path.personalized_sequence
            if path.current_position < len(sequence) and sequence[path.current_position] == problem_id:
                if success:
                    path.current_position += 1
            
            # Update completion percentage
            path.completion_percentage = (len(path.problems_completed) / len(sequence)) * 100
            
            # Update performance metrics
            if not path.performance_metrics:
                path.performance_metrics = {}
            
            if 'problem_performance' not in path.performance_metrics:
                path.performance_metrics['problem_performance'] = {}
            
            path.performance_metrics['problem_performance'][problem_id] = {
                'success': success,
                'time_spent_seconds': time_spent_seconds,
                'timestamp': datetime.now().isoformat(),
                'additional_metrics': additional_metrics or {}
            }
            
            # Check for milestone completion
            milestone_updates = self._check_milestone_completion(path, problem_id, success)
            
            # Update estimated completion based on current pace
            if path.current_position > 0:
                avg_time_per_problem = self._calculate_average_time_per_problem(path)
                remaining_problems = len(sequence) - path.current_position
                estimated_hours_remaining = (remaining_problems * avg_time_per_problem) / 3600
                
                path.estimated_completion = datetime.now() + timedelta(
                    hours=estimated_hours_remaining
                )
            
            self.db.commit()
            
            return {
                'current_position': path.current_position,
                'completion_percentage': path.completion_percentage,
                'problems_completed': len(path.problems_completed),
                'total_problems': len(sequence),
                'milestone_updates': milestone_updates,
                'estimated_completion': path.estimated_completion.isoformat() if path.estimated_completion else None
            }
            
        except Exception as e:
            logger.error(f"Error updating path progress: {str(e)}")
            self.db.rollback()
            raise
    
    # Private helper methods
    
    def _build_skill_dependency_graph(self) -> Dict[str, List[str]]:
        """Build a graph of skill prerequisites"""
        return {
            SkillArea.ARRAYS.value: [],
            SkillArea.STRINGS.value: [SkillArea.ARRAYS.value],
            SkillArea.HASH_TABLES.value: [SkillArea.ARRAYS.value],
            SkillArea.TWO_POINTERS.value: [SkillArea.ARRAYS.value],
            SkillArea.SLIDING_WINDOW.value: [SkillArea.TWO_POINTERS.value],
            SkillArea.TREES.value: [SkillArea.ARRAYS.value],
            SkillArea.GRAPHS.value: [SkillArea.TREES.value],
            SkillArea.DYNAMIC_PROGRAMMING.value: [SkillArea.ARRAYS.value, SkillArea.STRINGS.value],
            SkillArea.GREEDY.value: [SkillArea.ARRAYS.value],
            SkillArea.BINARY_SEARCH.value: [SkillArea.ARRAYS.value],
            SkillArea.SORTING.value: [SkillArea.ARRAYS.value],
            SkillArea.BACKTRACKING.value: [SkillArea.ARRAYS.value, SkillArea.TREES.value],
            SkillArea.MATHEMATICS.value: [],
            SkillArea.BIT_MANIPULATION.value: [SkillArea.MATHEMATICS.value],
            SkillArea.SYSTEM_DESIGN.value: [SkillArea.ARRAYS.value, SkillArea.HASH_TABLES.value]
        }
    
    def _load_path_templates(self) -> List[LearningPathTemplate]:
        """Load available learning path templates"""
        return self.db.query(LearningPathTemplate).filter(
            LearningPathTemplate.status == 'active'
        ).all()
    
    def _skill_level_to_numeric(self, level: str) -> float:
        """Convert string skill level to numeric value"""
        level_map = {
            'beginner': 0.3,
            'intermediate': 0.6,
            'advanced': 0.9
        }
        return level_map.get(level.lower(), 0.3)
    
    def _analyze_learning_objectives(self, user_profile: UserProfile) -> List[LearningObjective]:
        """Analyze user profile and determine learning objectives"""
        objectives = []
        
        # Identify skill gaps
        for skill_area, current_level in user_profile.current_skill_levels.items():
            # Convert string level to numeric
            current_numeric = self._skill_level_to_numeric(current_level) if isinstance(current_level, str) else current_level
            
            if skill_area in [area.lower() for area in user_profile.weak_areas or []]:
                # High priority for weak areas
                target_level = min(1.0, current_numeric + 0.5)
                priority = 5
            elif skill_area in [area.lower() for area in user_profile.strong_areas or []]:
                # Lower priority for strong areas
                target_level = min(1.0, current_numeric + 0.2)
                priority = 2
            else:
                # Medium priority for others
                target_level = min(1.0, current_numeric + 0.3)
                priority = 3
            
            prerequisites = self.skill_dependencies.get(skill_area, [])
            estimated_hours = int((target_level - current_numeric) * 20)  # Rough estimate
            
            objectives.append(LearningObjective(
                skill_area=skill_area,
                target_level=target_level,
                priority=priority,
                prerequisite_skills=prerequisites,
                estimated_hours=estimated_hours
            ))
        
        # Sort by priority
        objectives.sort(key=lambda x: x.priority, reverse=True)
        return objectives
    
    def _generate_problem_sequence(
        self,
        user_profile: UserProfile,
        learning_objectives: List[LearningObjective],
        template: Optional[LearningPathTemplate]
    ) -> List[str]:
        """Generate the optimal sequence of problems for the learning path"""
        
        # Calculate total available hours
        total_weeks = user_profile.target_completion_weeks or 8
        total_hours = total_weeks * user_profile.available_hours_per_week
        
        # Allocate problems based on objectives and hours
        problem_sequence = []
        hours_allocated = 0
        
        for objective in learning_objectives:
            if hours_allocated >= total_hours:
                break
            
            # Find problems for this skill area
            current_skill_level = user_profile.current_skill_levels.get(objective.skill_area, 0.3)
            current_skill_numeric = self._skill_level_to_numeric(current_skill_level) if isinstance(current_skill_level, str) else current_skill_level
            
            skill_problems = self._find_problems_for_skill(
                objective.skill_area,
                current_skill_numeric,
                objective.target_level
            )
            
            # Filter and sort problems
            filtered_problems = self._filter_and_sort_problems(
                skill_problems, user_profile, objective
            )
            
            # Add problems within time budget
            objective_hours = min(objective.estimated_hours, total_hours - hours_allocated)
            problems_to_add = self._select_problems_for_hours(filtered_problems, objective_hours)
            
            problem_sequence.extend([p.id for p in problems_to_add])
            hours_allocated += objective_hours
        
        # Ensure variety and proper difficulty progression
        problem_sequence = self._optimize_sequence_order(problem_sequence, user_profile)
        
        return problem_sequence
    
    def _find_problems_for_skill(
        self,
        skill_area: str,
        current_level: float,
        target_level: float
    ) -> List[Problem]:
        """Find problems suitable for developing a specific skill"""
        
        # Map skill levels to difficulties
        if current_level < 0.4:
            start_difficulty = DifficultyLevel.EASY.value
        elif current_level < 0.7:
            start_difficulty = DifficultyLevel.MEDIUM.value
        else:
            start_difficulty = DifficultyLevel.HARD.value
        
        if target_level < 0.5:
            end_difficulty = DifficultyLevel.EASY.value
        elif target_level < 0.8:
            end_difficulty = DifficultyLevel.MEDIUM.value
        else:
            end_difficulty = DifficultyLevel.HARD.value
        
        # Query problems with this skill tag (using text search for SQLite compatibility)
        from sqlalchemy import cast, String
        query = self.db.query(Problem).filter(
            cast(Problem.algorithm_tags, String).contains(f'"{skill_area}"')
        )
        
        query = query.filter(
            Problem.quality_score >= 60.0  # Lowered quality threshold for better coverage
        )
        
        # Include appropriate difficulties
        difficulties = [start_difficulty]
        if start_difficulty != end_difficulty:
            if start_difficulty == DifficultyLevel.EASY.value:
                difficulties.append(DifficultyLevel.MEDIUM.value)
                if end_difficulty == DifficultyLevel.HARD.value:
                    difficulties.append(DifficultyLevel.HARD.value)
            elif start_difficulty == DifficultyLevel.MEDIUM.value and end_difficulty == DifficultyLevel.HARD.value:
                difficulties.append(DifficultyLevel.HARD.value)
        
        query = query.filter(Problem.difficulty.in_(difficulties))
        
        return query.order_by(
            Problem.google_interview_relevance.desc(),
            Problem.quality_score.desc()
        ).all()
    
    def _create_learning_milestones(
        self,
        problem_sequence: List[str],
        learning_objectives: List[LearningObjective],
        user_profile: UserProfile
    ) -> List[Dict[str, Any]]:
        """Create learning milestones for the path"""
        milestones = []
        
        # Create milestones for each major learning objective
        for i, objective in enumerate(learning_objectives[:5]):  # Limit to 5 major milestones
            milestone_position = int((i + 1) * len(problem_sequence) / len(learning_objectives))
            
            milestone = {
                'order': i + 1,
                'name': f"{objective.skill_area.replace('_', ' ').title()} Mastery",
                'description': f"Achieve {objective.target_level:.1%} proficiency in {objective.skill_area}",
                'milestone_type': 'concept_mastery',
                'problem_ids': problem_sequence[max(0, milestone_position-5):milestone_position],
                'completion_criteria': {
                    'min_success_rate': 0.8,
                    'min_problems_completed': 3,
                    'target_skill_level': objective.target_level
                },
                'target_completion_date': (
                    datetime.now() + timedelta(
                        weeks=int((i + 1) * user_profile.target_completion_weeks / len(learning_objectives))
                    )
                )
            }
            milestones.append(milestone)
        
        return milestones
    
    def _calculate_timeline(
        self,
        problem_sequence: List[str],
        hours_per_week: int
    ) -> Dict[str, datetime]:
        """Calculate timeline for path completion"""
        
        # Estimate time per problem based on difficulty
        total_hours = 0
        for problem_id in problem_sequence:
            problem = self.db.query(Problem).filter(Problem.id == problem_id).first()
            if problem:
                hours = self.difficulty_weights.get(problem.difficulty, 2.0)
                total_hours += hours
        
        # Calculate completion timeline
        weeks_needed = max(1, int(total_hours / hours_per_week))
        
        return {
            'target_completion': datetime.now() + timedelta(weeks=weeks_needed),
            'estimated_completion': datetime.now() + timedelta(weeks=weeks_needed + 1)  # Buffer
        }
    
    def _generate_path_name(
        self,
        user_profile: UserProfile,
        learning_objectives: List[LearningObjective]
    ) -> str:
        """Generate a descriptive name for the learning path"""
        
        if 'google' in [goal.lower() for goal in user_profile.learning_goals]:
            return f"Google Interview Preparation - {user_profile.target_completion_weeks or 8} Weeks"
        elif 'competitive' in [goal.lower() for goal in user_profile.learning_goals]:
            return "Competitive Programming Mastery Path"
        else:
            top_skills = [obj.skill_area.replace('_', ' ').title() 
                         for obj in learning_objectives[:3]]
            return f"Personalized Path: {', '.join(top_skills)}"
    
    def _generate_path_description(
        self,
        user_profile: UserProfile,
        learning_objectives: List[LearningObjective]
    ) -> str:
        """Generate a detailed description for the learning path"""
        
        description_parts = [
            f"Personalized learning path designed for {user_profile.available_hours_per_week} hours/week study schedule.",
            f"Focuses on {len(learning_objectives)} key skill areas with adaptive difficulty progression.",
            f"Target completion: {user_profile.target_completion_weeks or 8} weeks."
        ]
        
        if user_profile.weak_areas:
            description_parts.append(f"Special emphasis on strengthening: {', '.join(user_profile.weak_areas)}.")
        
        return " ".join(description_parts)
    
    # Additional helper methods would continue here...
    # (Due to length constraints, I'll create these in subsequent files)
    
    def _get_template(self, template_id: str) -> Optional[LearningPathTemplate]:
        """Get a specific learning path template"""
        return self.db.query(LearningPathTemplate).filter(
            LearningPathTemplate.id == template_id
        ).first()
    
    def _select_optimal_template(
        self,
        user_profile: UserProfile,
        learning_objectives: List[LearningObjective]
    ) -> Optional[LearningPathTemplate]:
        """Select the best template for a user profile"""
        # For now, return None to use custom generation
        # In future, implement template matching logic
        return None
    
    def _analyze_adaptation_need(
        self,
        path: UserLearningPath,
        performance_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze if and how a learning path should be adapted"""
        # Simplified implementation - return no adaptation needed
        return {
            'needs_adaptation': False,
            'difficulty_adjustment': False,
            'sequence_modification': False,
            'timeline_adjustment': False,
            'trigger': None
        }
    
    def _assess_skill_area(self, skill_area: str, interactions: List[UserInteraction]) -> float:
        """Assess proficiency in a specific skill area"""
        # Simple implementation - analyze success rate in skill area
        skill_interactions = [
            i for i in interactions 
            if i.problem and i.problem.algorithm_tags and skill_area in i.problem.algorithm_tags
        ]
        
        if not skill_interactions:
            return 0.3  # Default beginner level
        
        solved_count = len([i for i in skill_interactions if i.action == 'solved'])
        total_count = len(skill_interactions)
        
        success_rate = solved_count / total_count if total_count > 0 else 0
        
        # Convert success rate to skill level (0.0-1.0)
        return min(1.0, max(0.1, success_rate * 1.2))
    
    def _calculate_recent_success_rate(self, interactions: List[UserInteraction]) -> float:
        """Calculate success rate from recent interactions"""
        recent_solves = [i for i in interactions[:20] if i.action in ['solved', 'attempted']]
        if not recent_solves:
            return 0.5
        
        success_count = len([i for i in recent_solves if i.action == 'solved'])
        return success_count / len(recent_solves)
    
    def _calculate_average_solve_time(self, interactions: List[UserInteraction]) -> float:
        """Calculate average time to solve problems"""
        solve_times = [
            i.time_spent_seconds for i in interactions[:20] 
            if i.action == 'solved' and i.time_spent_seconds
        ]
        
        if not solve_times:
            return 3600.0  # Default 1 hour
        
        return sum(solve_times) / len(solve_times)
    
    def _generate_learning_context(
        self,
        problem: Problem,
        path: UserLearningPath,
        position: int
    ) -> Dict[str, Any]:
        """Generate learning context for a problem"""
        return {
            'learning_context': {
                'position_in_path': position + 1,
                'total_problems': len(path.personalized_sequence),
                'focus_areas': problem.algorithm_tags[:3] if problem.algorithm_tags else [],
                'difficulty_reasoning': f"Selected for your current skill level progression",
                'learning_objectives': f"This problem will help you practice {', '.join(problem.algorithm_tags[:2]) if problem.algorithm_tags else 'problem solving'}",
                'estimated_time_minutes': self.difficulty_weights.get(problem.difficulty, 2.0) * 60
            }
        }
    
    def _filter_and_sort_problems(
        self,
        problems: List[Problem],
        user_profile: UserProfile,
        objective: LearningObjective
    ) -> List[Problem]:
        """Filter and sort problems for optimal learning"""
        # Remove any problems the user has already solved
        # Sort by learning value and difficulty progression
        return sorted(problems, key=lambda p: (
            p.google_interview_relevance or 0,
            p.quality_score or 0
        ), reverse=True)
    
    def _select_problems_for_hours(
        self,
        problems: List[Problem],
        target_hours: int
    ) -> List[Problem]:
        """Select problems that fit within the target hours"""
        selected = []
        total_hours = 0
        
        for problem in problems:
            problem_hours = self.difficulty_weights.get(problem.difficulty, 2.0)
            if total_hours + problem_hours <= target_hours:
                selected.append(problem)
                total_hours += problem_hours
            
            if len(selected) >= 20:  # Max problems per skill area
                break
        
        return selected
    
    def _optimize_sequence_order(
        self,
        problem_ids: List[str],
        user_profile: UserProfile
    ) -> List[str]:
        """Optimize the order of problems for better learning progression"""
        # For now, return as-is
        # In future, implement intelligent reordering
        return problem_ids
    
    def _check_milestone_completion(
        self,
        path: UserLearningPath,
        problem_id: str,
        success: bool
    ) -> List[Dict[str, Any]]:
        """Check if any milestones were completed"""
        # Simplified implementation
        return []
    
    def _calculate_average_time_per_problem(self, path: UserLearningPath) -> float:
        """Calculate average time spent per problem"""
        if not path.performance_metrics or 'problem_performance' not in path.performance_metrics:
            return 3600.0  # Default 1 hour
        
        performances = path.performance_metrics['problem_performance'].values()
        times = [p['time_spent_seconds'] for p in performances if 'time_spent_seconds' in p]
        
        if not times:
            return 3600.0
        
        return sum(times) / len(times)
    
    def _infer_skill_level(self, skill_levels: Dict[str, float]) -> str:
        """Infer overall skill level from individual skill ratings"""
        if not skill_levels:
            return 'intermediate'
        
        # Convert string skill levels to numeric
        numeric_levels = []
        for level in skill_levels.values():
            if isinstance(level, str):
                numeric_levels.append(self._skill_level_to_numeric(level))
            else:
                numeric_levels.append(level)
        
        avg_skill = sum(numeric_levels) / len(numeric_levels)
        
        if avg_skill < 0.3:
            return 'beginner'
        elif avg_skill < 0.7:
            return 'intermediate'
        else:
            return 'advanced'

    # Placeholder methods for adaptation (to be implemented)
    def _adapt_difficulty_progression(self, path, performance_data):
        return []
    
    def _adapt_problem_sequence(self, path, performance_data):
        return []
    
    def _adapt_timeline(self, path, performance_data):
        return []
    
    def _apply_adaptations(self, path, adaptations):
        pass

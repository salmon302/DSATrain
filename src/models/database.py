"""
Phase 4 Database Models
Enhanced database schema for scalable problem and solution storage
"""

from sqlalchemy import create_engine, Column, String, Integer, Float, Text, JSON, DateTime, ForeignKey, Boolean, Index, PrimaryKeyConstraint
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List, Dict, Any
import json
import os

Base = declarative_base()

class Problem(Base):
    """Enhanced Problem model for Phase 4 scalability"""
    __tablename__ = 'problems'
    
    # Primary identification
    id = Column(String(50), primary_key=True)
    platform = Column(String(20), nullable=False, index=True)
    platform_id = Column(String(50), nullable=False)  # Original platform problem ID
    title = Column(String(300), nullable=False)
    
    # Classification
    difficulty = Column(String(20), nullable=False, index=True)
    category = Column(String(50), index=True)
    
    # Content
    description = Column(Text)
    constraints = Column(JSON)
    examples = Column(JSON)
    hints = Column(JSON)
    
    # Metadata
    algorithm_tags = Column(JSON, nullable=False)  # List of algorithm types
    data_structures = Column(JSON)  # List of data structures used
    complexity_class = Column(String(50))  # Time complexity class
    
    # Metrics
    google_interview_relevance = Column(Float, default=0.0, index=True)
    difficulty_rating = Column(Float, default=0.0)
    quality_score = Column(Float, default=0.0, index=True)
    popularity_score = Column(Float, default=0.0)

    # Redesign extensions
    pattern_tags = Column(JSON)  # list of strings
    skill_areas = Column(JSON)   # list of strings
    granular_difficulty = Column(Integer)  # 1–5
    interview_frequency = Column(Float)  # float proxy
    company_tags = Column(JSON)  # list of strings
    source_dataset = Column(String(100))
    canonical_solutions = Column(JSON)  # structured canonical solutions
    visual_aids = Column(JSON)
    verbal_explanations = Column(JSON)
    prerequisite_assessment = Column(JSON)
    elaborative_prompts = Column(JSON)
    working_memory_load = Column(Integer)  # 1–10
    
    # Skill Tree Enhancements
    sub_difficulty_level = Column(Integer, default=1)  # 1-5 within difficulty category
    conceptual_difficulty = Column(Integer, default=50)  # 0-100 conceptual complexity
    implementation_complexity = Column(Integer, default=50)  # 0-100 implementation difficulty
    prerequisite_skills = Column(JSON, default=lambda: [])  # Required skills
    skill_tree_position = Column(JSON, default=lambda: {})  # Position metadata for visualization
    
    # Analytics
    acceptance_rate = Column(Float)
    frequency_score = Column(Float)
    companies = Column(JSON)  # Companies that ask this problem
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    collected_at = Column(DateTime, default=func.now())
    
    # Relationships
    solutions = relationship("Solution", back_populates="problem", cascade="all, delete-orphan")
    user_interactions = relationship("UserInteraction", back_populates="problem")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_platform_difficulty', 'platform', 'difficulty'),
        Index('idx_quality_relevance', 'quality_score', 'google_interview_relevance'),
        Index('idx_tags_gin', 'algorithm_tags', postgresql_using='gin'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'platform': self.platform,
            'platform_id': self.platform_id,
            'title': self.title,
            'difficulty': self.difficulty,
            'category': self.category,
            # Content fields used by the Practice UI
            'description': self.description,
            'constraints': self.constraints,
            'examples': self.examples,
            'hints': self.hints,
            'algorithm_tags': self.algorithm_tags,
            'data_structures': self.data_structures,
            'pattern_tags': self.pattern_tags,
            'skill_areas': self.skill_areas,
            'granular_difficulty': self.granular_difficulty,
            'google_interview_relevance': self.google_interview_relevance,
            'difficulty_rating': self.difficulty_rating,
            'quality_score': self.quality_score,
            'popularity_score': self.popularity_score,
            'acceptance_rate': self.acceptance_rate,
            'companies': self.companies,
            'company_tags': self.company_tags,
            'interview_frequency': self.interview_frequency,
            'source_dataset': self.source_dataset,
            'solution_count': len(self.solutions) if self.solutions else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Solution(Base):
    """Enhanced Solution model for Phase 4 quality analysis"""
    __tablename__ = 'solutions'
    
    # Primary identification
    id = Column(String(50), primary_key=True)
    problem_id = Column(String(50), ForeignKey('problems.id'), nullable=False, index=True)
    
    # Code content
    code = Column(Text, nullable=False)
    language = Column(String(20), nullable=False, default='python')
    approach_type = Column(String(50), nullable=False, index=True)
    
    # Algorithm classification
    algorithm_tags = Column(JSON, nullable=False)
    data_structures_used = Column(JSON)
    pattern_type = Column(String(50))
    
    # Complexity analysis
    time_complexity = Column(String(50))
    space_complexity = Column(String(50))
    complexity_class = Column(String(20), index=True)  # optimal, suboptimal, etc.
    
    # Quality metrics
    overall_quality_score = Column(Float, nullable=False, index=True)
    readability_score = Column(Float)
    documentation_score = Column(Float)
    efficiency_score = Column(Float)
    maintainability_score = Column(Float)
    style_score = Column(Float)
    
    # Performance data
    runtime_ms = Column(Integer)
    memory_usage_mb = Column(Float)
    performance_percentile = Column(Float)
    
    # Educational content
    explanation = Column(Text)
    step_by_step = Column(JSON)  # List of explanation steps
    key_insights = Column(JSON)  # List of key learning points
    common_mistakes = Column(JSON)  # Common pitfalls to avoid
    
    # Context and metadata
    google_interview_relevance = Column(Float, default=0.0)
    competitive_programming_relevance = Column(Float, default=0.0)
    educational_value = Column(Float, default=0.0)
    implementation_difficulty = Column(Integer, default=1)  # 1-10 scale
    conceptual_difficulty = Column(Integer, default=1)  # 1-10 scale
    
    # Source and validation
    source_type = Column(String(20), default='generated')  # generated, scraped, manual
    validation_status = Column(String(20), default='pending')  # pending, validated, rejected
    author = Column(String(100))
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    problem = relationship("Problem", back_populates="solutions")
    user_interactions = relationship("UserInteraction", back_populates="solution")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_problem_quality', 'problem_id', 'overall_quality_score'),
        Index('idx_approach_quality', 'approach_type', 'overall_quality_score'),
        Index('idx_complexity_performance', 'complexity_class', 'performance_percentile'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'problem_id': self.problem_id,
            'language': self.language,
            'approach_type': self.approach_type,
            'algorithm_tags': self.algorithm_tags,
            'data_structures_used': self.data_structures_used,
            'time_complexity': self.time_complexity,
            'space_complexity': self.space_complexity,
            'overall_quality_score': self.overall_quality_score,
            'readability_score': self.readability_score,
            'documentation_score': self.documentation_score,
            'efficiency_score': self.efficiency_score,
            'runtime_ms': self.runtime_ms,
            'memory_usage_mb': self.memory_usage_mb,
            'performance_percentile': self.performance_percentile,
            'google_interview_relevance': self.google_interview_relevance,
            'competitive_programming_relevance': self.competitive_programming_relevance,
            'educational_value': self.educational_value,
            'implementation_difficulty': self.implementation_difficulty,
            'conceptual_difficulty': self.conceptual_difficulty,
            'explanation': self.explanation,
            'step_by_step': self.step_by_step,
            'key_insights': self.key_insights,
            'validation_status': self.validation_status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class UserInteraction(Base):
    """Track user interactions for ML recommendations"""
    __tablename__ = 'user_interactions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), nullable=False, index=True)
    problem_id = Column(String(50), ForeignKey('problems.id'), index=True)
    solution_id = Column(String(50), ForeignKey('solutions.id'), index=True)
    
    # Interaction types
    action = Column(String(20), nullable=False, index=True)  # viewed, solved, bookmarked, rated
    rating = Column(Integer)  # 1-5 rating if applicable
    time_spent_seconds = Column(Integer)
    success = Column(Boolean)  # For solve attempts
    
    # Context
    session_id = Column(String(100))
    device_type = Column(String(20))
    learning_path_id = Column(String(50))
    
    # Context data
    interaction_metadata = Column(JSON)  # Additional context data
    
    # Timestamps
    timestamp = Column(DateTime, default=func.now(), index=True)
    
    # Relationships
    problem = relationship("Problem", back_populates="user_interactions")
    solution = relationship("Solution", back_populates="user_interactions")
    
    # Indexes
    __table_args__ = (
        Index('idx_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_user_action', 'user_id', 'action'),
    )


class LearningPath(Base):
    """Structured learning paths for users"""
    __tablename__ = 'learning_paths'
    
    id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(50), index=True)  # interview_prep, competitive, algorithms
    difficulty_level = Column(String(20), index=True)  # beginner, intermediate, advanced
    
    # Path configuration
    problem_sequence = Column(JSON, nullable=False)  # Ordered list of problem IDs
    prerequisites = Column(JSON)  # Required skills/knowledge
    estimated_time_hours = Column(Integer)
    
    # Metadata
    created_by = Column(String(50))
    tags = Column(JSON)
    popularity_score = Column(Float, default=0.0)
    completion_rate = Column(Float, default=0.0)
    
    # Status
    status = Column(String(20), default='active')  # active, archived, draft
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'difficulty_level': self.difficulty_level,
            'problem_sequence': self.problem_sequence,
            'prerequisites': self.prerequisites,
            'estimated_time_hours': self.estimated_time_hours,
            'tags': self.tags,
            'popularity_score': self.popularity_score,
            'completion_rate': self.completion_rate,
            'status': self.status,
            'problem_count': len(self.problem_sequence) if self.problem_sequence else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class LearningPathTemplate(Base):
    """Template learning paths for different goals and skill levels"""
    __tablename__ = 'learning_path_templates'
    
    id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(50), index=True)  # interview_prep, skill_mastery, foundations
    target_skill_level = Column(String(20), index=True)  # beginner, intermediate, advanced
    estimated_duration_weeks = Column(Integer)
    
    # Learning configuration
    prerequisite_skills = Column(JSON)  # Required skills before starting
    learning_objectives = Column(JSON)  # Skills to be gained
    problem_sequence_template = Column(JSON)  # Template for problem selection rules
    adaptation_rules = Column(JSON)  # Rules for path adaptation
    
    # Difficulty progression
    difficulty_curve = Column(JSON)  # How difficulty should progress over time
    concept_order = Column(JSON)  # Order of concept introduction
    
    # Metadata
    created_by = Column(String(50))
    tags = Column(JSON)
    popularity_score = Column(Float, default=0.0)
    success_rate = Column(Float, default=0.0)  # How often users complete this template
    
    # Status
    status = Column(String(20), default='active')  # active, archived, draft
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'target_skill_level': self.target_skill_level,
            'estimated_duration_weeks': self.estimated_duration_weeks,
            'prerequisite_skills': self.prerequisite_skills,
            'learning_objectives': self.learning_objectives,
            'tags': self.tags,
            'popularity_score': self.popularity_score,
            'success_rate': self.success_rate,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class UserLearningPath(Base):
    """Personalized learning paths for individual users"""
    __tablename__ = 'user_learning_paths'
    
    id = Column(String(50), primary_key=True)
    user_id = Column(String(50), nullable=False, index=True)
    template_id = Column(String(50), ForeignKey('learning_path_templates.id'), index=True)
    
    # Path configuration
    name = Column(String(200), nullable=False)
    description = Column(Text)
    personalized_sequence = Column(JSON, nullable=False)  # Actual problem sequence for this user
    
    # Progress tracking
    current_position = Column(Integer, default=0)
    completion_percentage = Column(Float, default=0.0)
    problems_completed = Column(JSON, default=list)  # List of completed problem IDs
    
    # Adaptation and performance
    adaptation_history = Column(JSON, default=list)  # History of path modifications
    performance_metrics = Column(JSON, default=dict)  # User's performance data
    skill_progression = Column(JSON, default=dict)  # Skill levels over time
    
    # Timeline
    started_at = Column(DateTime, default=func.now())
    target_completion = Column(DateTime)
    estimated_completion = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Status
    status = Column(String(20), default='active')  # active, paused, completed, abandoned
    
    # Relationships
    template = relationship("LearningPathTemplate")
    milestones = relationship("LearningMilestone", back_populates="learning_path", cascade="all, delete-orphan")
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_user_status', 'user_id', 'status'),
        Index('idx_user_progress', 'user_id', 'completion_percentage'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        # Calculate problem distribution by difficulty
        easy_count = medium_count = hard_count = 0
        if self.personalized_sequence:
            # Count problems by difficulty - we'll need to query the database for this
            # For now, use approximate distribution
            total_problems = len(self.personalized_sequence)
            easy_count = int(total_problems * 0.4)  # 40% easy
            medium_count = int(total_problems * 0.4)  # 40% medium  
            hard_count = total_problems - easy_count - medium_count  # remainder hard
        
        # Calculate estimated completion time
        total_hours = (len(self.personalized_sequence) if self.personalized_sequence else 0) * 1.5  # 1.5 hours per problem average
        
        # Get duration from performance metrics or use default
        duration_weeks = 8
        if self.performance_metrics:
            duration_weeks = self.performance_metrics.get('duration_weeks', 8)
        
        hours_per_week = total_hours / max(duration_weeks, 1)  # Avoid division by zero
        
        # Extract goal and level from performance metrics if available
        target_goal = 'google_interview'  # default
        current_level = 'intermediate'  # default
        
        if self.performance_metrics:
            target_goal = self.performance_metrics.get('target_goal', target_goal)
            current_level = self.performance_metrics.get('current_level', current_level)
        
        # Generate weekly plan structure
        weekly_plan = []
        if self.personalized_sequence:
            problems_per_week = max(1, len(self.personalized_sequence) // duration_weeks)
            for week in range(duration_weeks):
                start_idx = week * problems_per_week
                end_idx = min(start_idx + problems_per_week, len(self.personalized_sequence))
                week_problems = self.personalized_sequence[start_idx:end_idx]
                
                weekly_plan.append({
                    'week': week + 1,
                    'problems': week_problems,  # Problem IDs - will be enriched in API layer
                    'focus_areas': ['algorithms', 'data_structures'],  # Could be extracted from problem tags
                    'estimated_hours': len(week_problems) * 1.5
                })
        
        return {
            'id': self.id,
            'user_id': self.user_id,
            'template_id': self.template_id,
            'name': self.name,
            'description': self.description,
            'target_goal': target_goal,
            'current_level': current_level,
            'duration_weeks': duration_weeks,
            'total_problems': len(self.personalized_sequence) if self.personalized_sequence else 0,
            'weekly_plan': weekly_plan,
            'estimated_completion_time': {
                'total_hours': int(total_hours),
                'hours_per_week': max(1, int(hours_per_week)),  # Ensure at least 1 hour per week
                'easy_problems': easy_count,
                'medium_problems': medium_count,
                'hard_problems': hard_count
            },
            'personalized_sequence': self.personalized_sequence,
            'current_position': self.current_position,
            'completion_percentage': self.completion_percentage,
            'problems_completed': self.problems_completed,
            'performance_metrics': self.performance_metrics,
            'skill_progression': self.skill_progression,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'target_completion': self.target_completion.isoformat() if self.target_completion else None,
            'estimated_completion': self.estimated_completion.isoformat() if self.estimated_completion else None,
            'status': self.status,
            'problem_count': len(self.personalized_sequence) if self.personalized_sequence else 0,
            'milestone_count': len(self.milestones) if self.milestones else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class LearningMilestone(Base):
    """Milestones within learning paths for tracking major achievements"""
    __tablename__ = 'learning_milestones'
    
    id = Column(String(50), primary_key=True)
    learning_path_id = Column(String(50), ForeignKey('user_learning_paths.id'), nullable=False, index=True)
    
    # Milestone definition
    name = Column(String(200), nullable=False)
    description = Column(Text)
    milestone_type = Column(String(50), nullable=False, index=True)  # concept_mastery, skill_check, review, assessment
    
    # Requirements
    problem_ids = Column(JSON)  # Problems that must be completed for this milestone
    completion_criteria = Column(JSON)  # Specific criteria (accuracy, time, etc.)
    prerequisite_milestones = Column(JSON)  # Previous milestones that must be completed
    
    # Assessment and results
    assessment_problems = Column(JSON)  # Problems used to assess milestone completion
    assessment_results = Column(JSON)  # Results of milestone assessment
    skill_mastery_levels = Column(JSON)  # Measured skill levels at milestone
    
    # Progress
    is_completed = Column(Boolean, default=False)
    completion_score = Column(Float)  # 0-100 score for milestone completion
    attempts = Column(Integer, default=0)
    
    # Timeline
    target_completion_date = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Relationships
    learning_path = relationship("UserLearningPath", back_populates="milestones")
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_path_milestone', 'learning_path_id', 'milestone_type'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'learning_path_id': self.learning_path_id,
            'name': self.name,
            'description': self.description,
            'milestone_type': self.milestone_type,
            'problem_ids': self.problem_ids,
            'completion_criteria': self.completion_criteria,
            'assessment_results': self.assessment_results,
            'skill_mastery_levels': self.skill_mastery_levels,
            'is_completed': self.is_completed,
            'completion_score': self.completion_score,
            'attempts': self.attempts,
            'target_completion_date': self.target_completion_date.isoformat() if self.target_completion_date else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class UserSkillAssessment(Base):
    """Track user skill levels over time for adaptive learning"""
    __tablename__ = 'user_skill_assessments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), nullable=False, index=True)
    
    # Skill measurements
    skill_area = Column(String(50), nullable=False, index=True)  # arrays, graphs, dp, etc.
    skill_level = Column(Float, nullable=False)  # 0.0-1.0 proficiency
    confidence_score = Column(Float)  # How confident we are in this assessment
    
    # Assessment context
    assessment_type = Column(String(30), nullable=False)  # problem_solve, milestone, manual
    problem_ids = Column(JSON)  # Problems used for this assessment
    performance_data = Column(JSON)  # Detailed performance metrics
    
    # Metadata
    learning_path_id = Column(String(50), ForeignKey('user_learning_paths.id'), index=True)
    
    # Timestamps
    assessed_at = Column(DateTime, default=func.now(), index=True)
    
    __table_args__ = (
        Index('idx_user_skill_time', 'user_id', 'skill_area', 'assessed_at'),
    )


class SystemMetrics(Base):
    """Track system performance and quality metrics"""
    __tablename__ = 'system_metrics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    metric_name = Column(String(100), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    metric_category = Column(String(50), index=True)  # quality, performance, usage
    
    # Context
    platform = Column(String(20))
    time_period = Column(String(20))  # daily, weekly, monthly
    metrics_metadata = Column(JSON)
    
    # Timestamps
    recorded_at = Column(DateTime, default=func.now(), index=True)
    
    __table_args__ = (
        Index('idx_metric_time', 'metric_name', 'recorded_at'),
    )


class ProblemCluster(Base):
    """Clusters of similar problems for skill tree visualization"""
    __tablename__ = 'problem_clusters'
    
    id = Column(String(50), primary_key=True)
    cluster_name = Column(String(200), nullable=False)
    primary_skill_area = Column(String(50), nullable=False, index=True)
    difficulty_level = Column(String(20), nullable=False, index=True)
    
    # Problem grouping
    representative_problems = Column(JSON, nullable=False)  # 3-5 key problems
    all_problems = Column(JSON, nullable=False)  # All problems in cluster
    similarity_threshold = Column(Float, default=0.7)
    cluster_size = Column(Integer, default=0)
    
    # Quality metrics
    avg_quality_score = Column(Float, default=0.0)
    avg_google_relevance = Column(Float, default=0.0)
    algorithm_tags = Column(JSON, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_clusters_skill_difficulty', 'primary_skill_area', 'difficulty_level'),
    )


class UserProblemConfidence(Base):
    """Track user confidence levels for individual problems"""
    __tablename__ = 'user_problem_confidence'
    
    user_id = Column(String(50), nullable=False)
    problem_id = Column(String(50), ForeignKey('problems.id'), nullable=False)
    confidence_level = Column(Integer, default=0)  # 0-5 scale
    
    # Performance tracking
    last_attempted = Column(DateTime)
    solve_time_seconds = Column(Integer)
    hints_used = Column(Integer, default=0)
    attempts_count = Column(Integer, default=0)
    
    # Learning progression
    first_solve_date = Column(DateTime)
    last_review_date = Column(DateTime)
    confidence_decay_factor = Column(Float, default=1.0)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'problem_id'),
        Index('idx_confidence_user_level', 'user_id', 'confidence_level'),
    )
    
    # Relationships
    problem = relationship("Problem", backref="user_confidences")


class UserSkillMastery(Base):
    """Track user mastery levels for skill areas"""
    __tablename__ = 'user_skill_mastery'
    
    user_id = Column(String(50), nullable=False)
    skill_area = Column(String(50), nullable=False)
    mastery_level = Column(Float, default=0.0)  # 0-100 scale
    
    # Progress metrics
    problems_attempted = Column(Integer, default=0)
    problems_solved = Column(Integer, default=0)
    avg_confidence = Column(Float, default=0.0)
    last_activity = Column(DateTime)
    
    # Trend analysis
    mastery_trend = Column(String(20), default='stable')  # improving/stable/declining
    weak_patterns = Column(JSON, default=lambda: [])
    strong_patterns = Column(JSON, default=lambda: [])
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'skill_area'),
        Index('idx_mastery_user_skill', 'user_id', 'skill_area'),
    )


class UserSkillTreePreferences(Base):
    """User preferences for skill tree visualization"""
    __tablename__ = 'user_skill_tree_preferences'
    
    user_id = Column(String(50), primary_key=True)
    
    # Display preferences
    preferred_view_mode = Column(String(20), default='columns')  # columns/grid/tree
    show_confidence_overlay = Column(Boolean, default=True)
    auto_expand_clusters = Column(Boolean, default=False)
    highlight_prerequisites = Column(Boolean, default=True)
    
    # Customization
    visible_skill_areas = Column(JSON, default=lambda: [])
    bookmarked_problems = Column(JSON, default=lambda: [])
    custom_problem_groups = Column(JSON, default=lambda: [])
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


# ================= Single-User Redesign: SRS & Cognitive =================

class ReviewCard(Base):
    __tablename__ = 'review_cards'

    id = Column(Integer, primary_key=True, autoincrement=True)
    problem_id = Column(String(50), ForeignKey('problems.id'), nullable=False, index=True)
    next_review_at = Column(DateTime, index=True)
    interval_days = Column(Integer, default=1)
    ease = Column(Float, default=2.5)  # SM-2 style ease factor
    reps = Column(Integer, default=0)
    lapses = Column(Integer, default=0)
    last_outcome = Column(String(20))  # again, hard, good, easy
    deck = Column(String(50), default='problems')

    problem = relationship('Problem')


class ReviewHistory(Base):
    __tablename__ = 'review_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    problem_id = Column(String(50), ForeignKey('problems.id'), nullable=False, index=True)
    outcome = Column(String(20), nullable=False)
    time_spent = Column(Integer)
    notes = Column(Text)
    timestamp = Column(DateTime, default=func.now(), index=True)

    problem = relationship('Problem')


class ProblemAttempt(Base):
    __tablename__ = 'problem_attempts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    problem_id = Column(String(50), ForeignKey('problems.id'), nullable=False, index=True)
    code = Column(Text)
    language = Column(String(30))
    status = Column(String(20))  # solved/attempted/failed
    time_spent = Column(Integer)
    test_results = Column(JSON)
    mistakes = Column(JSON)
    reflection = Column(Text)
    created_at = Column(DateTime, default=func.now(), index=True)

    problem = relationship('Problem')


class UserCognitiveProfile(Base):
    __tablename__ = 'user_cognitive_profile'

    user_id = Column(String(50), primary_key=True, default='default_user')
    working_memory_capacity = Column(Integer)
    learning_style_preference = Column(String(20))  # visual/verbal/balanced
    visual_vs_verbal = Column(Float)  # 0..1
    processing_speed = Column(String(20))  # slow/average/fast
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class ElaborativeSession(Base):
    __tablename__ = 'elaborative_sessions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    problem_id = Column(String(50), ForeignKey('problems.id'), nullable=False, index=True)
    why_questions = Column(JSON)
    how_questions = Column(JSON)
    responses = Column(JSON)
    timestamp = Column(DateTime, default=func.now(), index=True)

    problem = relationship('Problem')


class RetrievalPractice(Base):
    __tablename__ = 'retrieval_practice'

    id = Column(Integer, primary_key=True, autoincrement=True)
    problem_id = Column(String(50), ForeignKey('problems.id'), nullable=False, index=True)
    retrieval_type = Column(String(50))  # micro, concept_map, explanation
    success_rate = Column(Float)
    retrieval_strength = Column(Float)
    timestamp = Column(DateTime, default=func.now(), index=True)

    problem = relationship('Problem')


class PracticeGateSession(Base):
    """Persist gated practice sessions (dry-run → pseudocode → code) per user/problem."""
    __tablename__ = 'practice_gate_sessions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(String(50), default='default_user', index=True)
    problem_id = Column(String(50), ForeignKey('problems.id'), nullable=False, index=True)
    # Store gates as a JSON mapping: {"dry_run": bool, "pseudocode": bool, "code": bool}
    gates = Column(JSON, default=lambda: {"dry_run": False, "pseudocode": False, "code": False})
    unlocked = Column(Boolean, default=False)
    started_at = Column(DateTime, default=func.now(), index=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), index=True)

    # Relationships
    problem = relationship('Problem')

# Database configuration
class DatabaseConfig:
    """Database configuration and connection management"""
    
    def __init__(self, database_url: str = None):
        # Precedence: explicit arg > env var DSATRAIN_DATABASE_URL > env var DATABASE_URL > default sqlite file
        if database_url is None:
            database_url = (
                os.getenv("DSATRAIN_DATABASE_URL")
                or os.getenv("DATABASE_URL")
                or "sqlite:///./dsatrain_phase4.db"
            )
        
        self.engine = create_engine(
            database_url,
            echo=False,  # Set to True for SQL debugging
            pool_pre_ping=True
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

        # Auto-create tables for ephemeral/in-memory DBs or when explicitly requested
        auto_create = os.getenv("DSATRAIN_AUTO_CREATE_TABLES") == "1" or database_url.startswith("sqlite:///:memory:")
        if auto_create:
            try:
                Base.metadata.create_all(bind=self.engine)
            except Exception:
                # Non-fatal: allow application to start even if create fails
                pass
    
    def create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(bind=self.engine)
        print("✅ Database tables created successfully")
    
    def drop_tables(self):
        """Drop all tables (use with caution!)"""
        Base.metadata.drop_all(bind=self.engine)
        print("⚠️ All database tables dropped")
    
    def get_session(self):
        """Get database session"""
        return self.SessionLocal()


# Database utility functions
def get_database_stats(db_session) -> Dict[str, int]:
    """Get current database statistics"""
    stats = {
        'problems': db_session.query(Problem).count(),
        'solutions': db_session.query(Solution).count(),
        'user_interactions': db_session.query(UserInteraction).count(),
        'learning_paths': db_session.query(LearningPath).count(),
        'learning_path_templates': db_session.query(LearningPathTemplate).count(),
        'user_learning_paths': db_session.query(UserLearningPath).count(),
        'learning_milestones': db_session.query(LearningMilestone).count(),
        'user_skill_assessments': db_session.query(UserSkillAssessment).count(),
        'system_metrics': db_session.query(SystemMetrics).count(),
        # Skill Tree Tables
        'problem_clusters': db_session.query(ProblemCluster).count(),
        'user_problem_confidence': db_session.query(UserProblemConfidence).count(),
        'user_skill_mastery': db_session.query(UserSkillMastery).count(),
    'user_skill_tree_preferences': db_session.query(UserSkillTreePreferences).count(),
    # Redesign SRS/Cognitive Tables
    'review_cards': db_session.query(ReviewCard).count(),
    'review_history': db_session.query(ReviewHistory).count(),
    'problem_attempts': db_session.query(ProblemAttempt).count(),
    'user_cognitive_profile': db_session.query(UserCognitiveProfile).count(),
    'elaborative_sessions': db_session.query(ElaborativeSession).count(),
    'retrieval_practice': db_session.query(RetrievalPractice).count(),
    'practice_gate_sessions': db_session.query(PracticeGateSession).count(),
    }
    return stats


def get_quality_metrics(db_session) -> Dict[str, float]:
    """Get overall quality metrics"""
    from sqlalchemy import func
    
    problem_quality = db_session.query(func.avg(Problem.quality_score)).scalar() or 0.0
    solution_quality = db_session.query(func.avg(Solution.overall_quality_score)).scalar() or 0.0
    
    return {
        'average_problem_quality': round(problem_quality, 2),
        'average_solution_quality': round(solution_quality, 2),
        'total_problems': db_session.query(Problem).count(),
        'total_solutions': db_session.query(Solution).count(),
        'high_quality_solutions': db_session.query(Solution).filter(Solution.overall_quality_score >= 95.0).count()
    }


if __name__ == "__main__":
    # Initialize database for development
    db_config = DatabaseConfig()
    db_config.create_tables()
    
    # Test database connection
    session = db_config.get_session()
    stats = get_database_stats(session)
    print(f"📊 Database initialized with {stats}")
    session.close()

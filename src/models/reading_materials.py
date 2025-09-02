"""
Reading Materials Database Models
Extends DSATrain with comprehensive educational content system
"""

from sqlalchemy import Column, String, Integer, Float, Text, JSON, DateTime, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Dict, List, Any, Optional
from src.models.database import Base


class ReadingMaterial(Base):
    """Comprehensive reading materials for algorithmic concepts and skills"""
    __tablename__ = 'reading_materials'
    
    # Primary identification
    id = Column(String(50), primary_key=True)
    title = Column(String(200), nullable=False)
    subtitle = Column(String(300))
    author = Column(String(100), default='DSATrain Team')
    
    # Content classification
    content_type = Column(String(30), nullable=False, index=True)  # guide, reference, tutorial, case_study, interactive
    difficulty_level = Column(String(20), nullable=False, index=True)  # beginner, intermediate, advanced
    estimated_read_time = Column(Integer, nullable=False)  # in minutes
    
    # Content organization
    concept_ids = Column(JSON, default=list)  # Related concepts from our 52-node graph
    competency_ids = Column(JSON, default=list)  # Related behavioral competencies
    prerequisite_materials = Column(JSON, default=list)  # Required reading order
    follow_up_materials = Column(JSON, default=list)  # Suggested next reading
    
    # Content targeting
    target_personas = Column(JSON, default=list)  # foundation_builder, pattern_recognizer, etc.
    learning_objectives = Column(JSON, default=list)  # What users should gain
    skill_level_requirements = Column(JSON, default=dict)  # Minimum skill levels needed
    
    # Content structure
    content_markdown = Column(Text, nullable=False)
    content_sections = Column(JSON, default=list)  # Table of contents
    interactive_elements = Column(JSON, default=list)  # Embedded visualizations, quizzes
    external_resources = Column(JSON, default=list)  # Links to additional materials
    
    # Metadata
    tags = Column(JSON, default=list)  # Searchable tags
    keywords = Column(JSON, default=list)  # SEO and search keywords
    summary = Column(Text)  # Brief description
    thumbnail_url = Column(String(200))  # Preview image
    
    # Quality metrics
    user_ratings = Column(Float, default=0.0, index=True)
    total_ratings = Column(Integer, default=0)
    completion_rate = Column(Float, default=0.0)
    effectiveness_score = Column(Float, default=0.0)  # Based on post-reading performance
    
    # Usage analytics
    view_count = Column(Integer, default=0)
    completion_count = Column(Integer, default=0)
    bookmark_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    
    # Content management
    status = Column(String(20), default='draft')  # draft, review, published, archived
    version = Column(String(20), default='1.0')
    last_reviewed = Column(DateTime)
    review_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    published_at = Column(DateTime)
    
    # Relationships
    reading_progress = relationship("UserReadingProgress", back_populates="material", cascade="all, delete-orphan")
    material_analytics = relationship("MaterialAnalytics", back_populates="material", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_content_difficulty', 'content_type', 'difficulty_level'),
        Index('idx_rating_completion', 'user_ratings', 'completion_rate'),
        Index('idx_status_published', 'status', 'published_at'),
    )
    
    def to_dict(self, include_content: bool = False) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        result = {
            'id': self.id,
            'title': self.title,
            'subtitle': self.subtitle,
            'author': self.author,
            'content_type': self.content_type,
            'difficulty_level': self.difficulty_level,
            'estimated_read_time': self.estimated_read_time,
            'concept_ids': self.concept_ids,
            'competency_ids': self.competency_ids,
            'target_personas': self.target_personas,
            'learning_objectives': self.learning_objectives,
            'tags': self.tags,
            'summary': self.summary,
            'thumbnail_url': self.thumbnail_url,
            'user_ratings': self.user_ratings,
            'total_ratings': self.total_ratings,
            'completion_rate': self.completion_rate,
            'effectiveness_score': self.effectiveness_score,
            'view_count': self.view_count,
            'status': self.status,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_content:
            result.update({
                'content_markdown': self.content_markdown,
                'content_sections': self.content_sections,
                'interactive_elements': self.interactive_elements,
                'external_resources': self.external_resources,
                'prerequisite_materials': self.prerequisite_materials,
                'follow_up_materials': self.follow_up_materials
            })
        
        return result


class UserReadingProgress(Base):
    """Track individual user progress through reading materials"""
    __tablename__ = 'user_reading_progress'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), nullable=False, index=True)
    material_id = Column(String(50), ForeignKey('reading_materials.id'), nullable=False)
    
    # Progress tracking
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)
    last_accessed = Column(DateTime, default=func.now())
    reading_time_seconds = Column(Integer, default=0)
    progress_percentage = Column(Float, default=0.0)  # 0.0 to 100.0
    
    # Engagement metrics
    sections_read = Column(JSON, default=list)  # Which sections were completed
    sections_skipped = Column(JSON, default=list)  # Which sections were skipped
    bookmarked_sections = Column(JSON, default=list)  # User bookmarks
    highlighted_text = Column(JSON, default=list)  # User highlights
    notes = Column(Text)  # User notes and comments
    
    # Interaction data
    scroll_depth = Column(Float, default=0.0)  # How far user scrolled
    interaction_events = Column(JSON, default=list)  # Clicks, hovers, etc.
    device_type = Column(String(20))  # desktop, tablet, mobile
    referrer_source = Column(String(50))  # How user arrived at material
    
    # Assessment results
    comprehension_score = Column(Float)  # Quiz/assessment score if applicable
    quiz_attempts = Column(Integer, default=0)
    quiz_results = Column(JSON, default=list)  # Detailed quiz performance
    
    # Post-reading performance
    problems_attempted_after = Column(JSON, default=list)  # Problems tried after reading
    performance_improvement = Column(Float)  # Measured improvement in related problems
    concept_mastery_change = Column(JSON, default=dict)  # Before/after concept understanding
    
    # Feedback
    user_rating = Column(Integer)  # 1-5 rating
    difficulty_rating = Column(Integer)  # 1-5 how difficult was this material
    usefulness_rating = Column(Integer)  # 1-5 how useful was this material
    feedback_text = Column(Text)  # Detailed feedback
    would_recommend = Column(Boolean)
    
    # Context
    learning_path_id = Column(String(50))  # If part of a learning path
    session_id = Column(String(100))  # User session when reading
    recommendation_context = Column(JSON)  # Why this was recommended
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    material = relationship("ReadingMaterial", back_populates="reading_progress")
    
    # Indexes
    __table_args__ = (
        Index('idx_user_material', 'user_id', 'material_id'),
    # Note: SQLite has global index namespace; use a unique name to avoid collisions
    Index('idx_user_reading_progress_pct', 'user_id', 'progress_percentage'),
        Index('idx_completion_time', 'completed_at'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'material_id': self.material_id,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None,
            'reading_time_seconds': self.reading_time_seconds,
            'progress_percentage': self.progress_percentage,
            'sections_read': self.sections_read,
            'bookmarked_sections': self.bookmarked_sections,
            'notes': self.notes,
            'comprehension_score': self.comprehension_score,
            'user_rating': self.user_rating,
            'difficulty_rating': self.difficulty_rating,
            'usefulness_rating': self.usefulness_rating,
            'would_recommend': self.would_recommend,
            'learning_path_id': self.learning_path_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class MaterialRecommendation(Base):
    """Track recommended reading materials for users"""
    __tablename__ = 'material_recommendations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), nullable=False, index=True)
    material_id = Column(String(50), ForeignKey('reading_materials.id'), nullable=False)
    
    # Recommendation context
    recommendation_type = Column(String(30), nullable=False)  # pre_problem, post_problem, milestone, gap_filling
    recommendation_reason = Column(Text)  # Human-readable explanation
    recommendation_score = Column(Float, default=0.0)  # Confidence score
    
    # Context that triggered recommendation
    trigger_problem_id = Column(String(50))  # Problem that triggered this recommendation
    trigger_concept_ids = Column(JSON, default=list)  # Concepts that triggered this
    trigger_competency_ids = Column(JSON, default=list)  # Competencies that triggered this
    user_skill_gaps = Column(JSON, default=list)  # Identified knowledge gaps
    
    # Recommendation metadata
    priority_level = Column(Integer, default=5)  # 1-10 priority
    urgency = Column(String(20), default='normal')  # low, normal, high
    personalization_factors = Column(JSON, default=dict)  # Why this specific recommendation
    
    # User response
    was_viewed = Column(Boolean, default=False)
    was_completed = Column(Boolean, default=False)
    user_dismissed = Column(Boolean, default=False)
    dismissal_reason = Column(String(100))
    
    # Effectiveness tracking
    click_through_time = Column(DateTime)  # When user clicked on recommendation
    completion_time = Column(DateTime)  # When user completed material
    post_recommendation_performance = Column(JSON)  # How user performed after reading
    
    # Timestamps
    recommended_at = Column(DateTime, default=func.now(), index=True)
    expires_at = Column(DateTime)  # When this recommendation becomes stale
    
    # Relationships
    material = relationship("ReadingMaterial")
    
    # Indexes
    __table_args__ = (
        Index('idx_user_recommendations', 'user_id', 'recommended_at'),
        Index('idx_recommendation_type', 'recommendation_type', 'priority_level'),
    )


class MaterialAnalytics(Base):
    """Aggregate analytics for reading materials"""
    __tablename__ = 'material_analytics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    material_id = Column(String(50), ForeignKey('reading_materials.id'), nullable=False)
    
    # Time period for analytics
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    period_type = Column(String(20), nullable=False)  # daily, weekly, monthly
    
    # Usage metrics
    unique_viewers = Column(Integer, default=0)
    total_views = Column(Integer, default=0)
    completion_count = Column(Integer, default=0)
    average_reading_time = Column(Float, default=0.0)
    bounce_rate = Column(Float, default=0.0)  # Percentage who left quickly
    
    # Engagement metrics
    average_scroll_depth = Column(Float, default=0.0)
    sections_completion_rate = Column(JSON, default=dict)  # Per-section completion
    bookmark_rate = Column(Float, default=0.0)
    share_rate = Column(Float, default=0.0)
    
    # Quality metrics
    average_rating = Column(Float, default=0.0)
    rating_distribution = Column(JSON, default=dict)  # Distribution of 1-5 ratings
    average_difficulty_rating = Column(Float, default=0.0)
    average_usefulness_rating = Column(Float, default=0.0)
    recommendation_rate = Column(Float, default=0.0)  # % who would recommend
    
    # Learning effectiveness
    average_comprehension_score = Column(Float, default=0.0)
    concept_mastery_improvement = Column(JSON, default=dict)  # Per-concept improvement
    problem_solving_improvement = Column(Float, default=0.0)  # Post-reading performance
    
    # User segmentation
    beginner_completion_rate = Column(Float, default=0.0)
    intermediate_completion_rate = Column(Float, default=0.0)
    advanced_completion_rate = Column(Float, default=0.0)
    persona_engagement = Column(JSON, default=dict)  # Engagement by user persona
    
    # Device and access patterns
    device_breakdown = Column(JSON, default=dict)  # desktop, tablet, mobile usage
    access_time_patterns = Column(JSON, default=dict)  # When users typically read
    referrer_breakdown = Column(JSON, default=dict)  # How users find the material
    
    # Timestamps
    calculated_at = Column(DateTime, default=func.now())
    
    # Relationships
    material = relationship("ReadingMaterial", back_populates="material_analytics")
    
    # Indexes
    __table_args__ = (
        Index('idx_material_period', 'material_id', 'period_type', 'period_start'),
    )


class ContentCollection(Base):
    """Organize reading materials into curated collections"""
    __tablename__ = 'content_collections'
    
    id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Collection metadata
    collection_type = Column(String(30), nullable=False)  # learning_path, topic_guide, interview_prep
    difficulty_level = Column(String(20))  # beginner, intermediate, advanced, mixed
    estimated_time_hours = Column(Integer)  # Total time to complete collection
    
    # Content organization
    material_ids = Column(JSON, nullable=False)  # Ordered list of materials
    material_order = Column(JSON, default=dict)  # Specific ordering and grouping
    prerequisites = Column(JSON, default=list)  # Required knowledge/materials
    
    # Targeting
    target_personas = Column(JSON, default=list)
    learning_objectives = Column(JSON, default=list)
    skill_outcomes = Column(JSON, default=list)
    
    # Quality metrics
    completion_rate = Column(Float, default=0.0)
    user_ratings = Column(Float, default=0.0)
    effectiveness_score = Column(Float, default=0.0)
    
    # Metadata
    tags = Column(JSON, default=list)
    author = Column(String(100))
    status = Column(String(20), default='active')
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'collection_type': self.collection_type,
            'difficulty_level': self.difficulty_level,
            'estimated_time_hours': self.estimated_time_hours,
            'material_ids': self.material_ids,
            'target_personas': self.target_personas,
            'learning_objectives': self.learning_objectives,
            'skill_outcomes': self.skill_outcomes,
            'completion_rate': self.completion_rate,
            'user_ratings': self.user_ratings,
            'material_count': len(self.material_ids) if self.material_ids else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# Reading material utility functions
def get_recommended_materials(
    db_session,
    user_id: str,
    context: Dict[str, Any],
    limit: int = 5
) -> List[Dict[str, Any]]:
    """Get personalized reading material recommendations for a user"""
    # Implementation would analyze user's current skill level, learning path,
    # recent problems, and knowledge gaps to recommend relevant materials
    pass


def track_reading_progress(
    db_session,
    user_id: str,
    material_id: str,
    progress_data: Dict[str, Any]
) -> bool:
    """Update user's reading progress for a material"""
    # Implementation would update or create reading progress record
    pass


def get_material_effectiveness(
    db_session,
    material_id: str,
    time_period: str = 'last_30_days'
) -> Dict[str, float]:
    """Calculate effectiveness metrics for a reading material"""
    # Implementation would analyze user performance after reading material
    pass


def search_materials(
    db_session,
    query: str,
    filters: Dict[str, Any] = None,
    user_context: Dict[str, Any] = None
) -> List[Dict[str, Any]]:
    """Search reading materials with personalized ranking"""
    # Implementation would provide intelligent search with personalization
    pass

"""Reading Materials System

Revision ID: 006_reading_materials_system
Revises: 005_ai_features_integration
Create Date: 2025-01-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '006_reading_materials_system'
down_revision = '005_ai_features_integration'
branch_labels = None
depends_on = None


def upgrade():
    """Add reading materials system tables"""
    
    # Create reading_materials table
    op.create_table('reading_materials',
        sa.Column('id', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('subtitle', sa.String(length=300), nullable=True),
        sa.Column('author', sa.String(length=100), nullable=True),
        
        # Content classification
        sa.Column('content_type', sa.String(length=30), nullable=False),
        sa.Column('difficulty_level', sa.String(length=20), nullable=False),
        sa.Column('estimated_read_time', sa.Integer(), nullable=False),
        
        # Content organization
        sa.Column('concept_ids', sa.JSON(), nullable=True),
        sa.Column('competency_ids', sa.JSON(), nullable=True),
        sa.Column('prerequisite_materials', sa.JSON(), nullable=True),
        sa.Column('follow_up_materials', sa.JSON(), nullable=True),
        
        # Content targeting
        sa.Column('target_personas', sa.JSON(), nullable=True),
        sa.Column('learning_objectives', sa.JSON(), nullable=True),
        sa.Column('skill_level_requirements', sa.JSON(), nullable=True),
        
        # Content structure
        sa.Column('content_markdown', sa.Text(), nullable=False),
        sa.Column('content_sections', sa.JSON(), nullable=True),
        sa.Column('interactive_elements', sa.JSON(), nullable=True),
        sa.Column('external_resources', sa.JSON(), nullable=True),
        
        # Metadata
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('keywords', sa.JSON(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('thumbnail_url', sa.String(length=200), nullable=True),
        
        # Quality metrics
        sa.Column('user_ratings', sa.Float(), nullable=True),
        sa.Column('total_ratings', sa.Integer(), nullable=True),
        sa.Column('completion_rate', sa.Float(), nullable=True),
        sa.Column('effectiveness_score', sa.Float(), nullable=True),
        
        # Usage analytics
        sa.Column('view_count', sa.Integer(), nullable=True),
        sa.Column('completion_count', sa.Integer(), nullable=True),
        sa.Column('bookmark_count', sa.Integer(), nullable=True),
        sa.Column('share_count', sa.Integer(), nullable=True),
        
        # Content management
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('version', sa.String(length=20), nullable=True),
        sa.Column('last_reviewed', sa.DateTime(), nullable=True),
        sa.Column('review_notes', sa.Text(), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        
        sa.PrimaryKeyConstraint('id')
    )
    
    # Indexes for reading_materials
    op.create_index('idx_content_difficulty', 'reading_materials', ['content_type', 'difficulty_level'])
    op.create_index('idx_rating_completion', 'reading_materials', ['user_ratings', 'completion_rate'])
    op.create_index('idx_status_published', 'reading_materials', ['status', 'published_at'])
    
    # Create user_reading_progress table
    op.create_table('user_reading_progress',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.String(length=50), nullable=False),
        sa.Column('material_id', sa.String(length=50), nullable=False),
        
        # Progress tracking
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('last_accessed', sa.DateTime(), nullable=True),
        sa.Column('reading_time_seconds', sa.Integer(), nullable=True),
        sa.Column('progress_percentage', sa.Float(), nullable=True),
        
        # Engagement metrics
        sa.Column('sections_read', sa.JSON(), nullable=True),
        sa.Column('sections_skipped', sa.JSON(), nullable=True),
        sa.Column('bookmarked_sections', sa.JSON(), nullable=True),
        sa.Column('highlighted_text', sa.JSON(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        
        # Interaction data
        sa.Column('scroll_depth', sa.Float(), nullable=True),
        sa.Column('interaction_events', sa.JSON(), nullable=True),
        sa.Column('device_type', sa.String(length=20), nullable=True),
        sa.Column('referrer_source', sa.String(length=50), nullable=True),
        
        # Assessment results
        sa.Column('comprehension_score', sa.Float(), nullable=True),
        sa.Column('quiz_attempts', sa.Integer(), nullable=True),
        sa.Column('quiz_results', sa.JSON(), nullable=True),
        
        # Post-reading performance
        sa.Column('problems_attempted_after', sa.JSON(), nullable=True),
        sa.Column('performance_improvement', sa.Float(), nullable=True),
        sa.Column('concept_mastery_change', sa.JSON(), nullable=True),
        
        # Feedback
        sa.Column('user_rating', sa.Integer(), nullable=True),
        sa.Column('difficulty_rating', sa.Integer(), nullable=True),
        sa.Column('usefulness_rating', sa.Integer(), nullable=True),
        sa.Column('feedback_text', sa.Text(), nullable=True),
        sa.Column('would_recommend', sa.Boolean(), nullable=True),
        
        # Context
        sa.Column('learning_path_id', sa.String(length=50), nullable=True),
        sa.Column('session_id', sa.String(length=100), nullable=True),
        sa.Column('recommendation_context', sa.JSON(), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        
        sa.ForeignKeyConstraint(['material_id'], ['reading_materials.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Indexes for user_reading_progress
    op.create_index('idx_reading_user_material', 'user_reading_progress', ['user_id', 'material_id'])
    op.create_index('idx_reading_user_progress', 'user_reading_progress', ['user_id', 'progress_percentage'])
    op.create_index('idx_reading_completion_time', 'user_reading_progress', ['completed_at'])
    
    # Create material_recommendations table
    op.create_table('material_recommendations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.String(length=50), nullable=False),
        sa.Column('material_id', sa.String(length=50), nullable=False),
        
        # Recommendation context
        sa.Column('recommendation_type', sa.String(length=30), nullable=False),
        sa.Column('recommendation_reason', sa.Text(), nullable=True),
        sa.Column('recommendation_score', sa.Float(), nullable=True),
        
        # Context that triggered recommendation
        sa.Column('trigger_problem_id', sa.String(length=50), nullable=True),
        sa.Column('trigger_concept_ids', sa.JSON(), nullable=True),
        sa.Column('trigger_competency_ids', sa.JSON(), nullable=True),
        sa.Column('user_skill_gaps', sa.JSON(), nullable=True),
        
        # Recommendation metadata
        sa.Column('priority_level', sa.Integer(), nullable=True),
        sa.Column('urgency', sa.String(length=20), nullable=True),
        sa.Column('personalization_factors', sa.JSON(), nullable=True),
        
        # User response
        sa.Column('was_viewed', sa.Boolean(), nullable=True),
        sa.Column('was_completed', sa.Boolean(), nullable=True),
        sa.Column('user_dismissed', sa.Boolean(), nullable=True),
        sa.Column('dismissal_reason', sa.String(length=100), nullable=True),
        
        # Effectiveness tracking
        sa.Column('click_through_time', sa.DateTime(), nullable=True),
        sa.Column('completion_time', sa.DateTime(), nullable=True),
        sa.Column('post_recommendation_performance', sa.JSON(), nullable=True),
        
        # Timestamps
        sa.Column('recommended_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        
        sa.ForeignKeyConstraint(['material_id'], ['reading_materials.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Indexes for material_recommendations
    op.create_index('idx_user_recommendations', 'material_recommendations', ['user_id', 'recommended_at'])
    op.create_index('idx_recommendation_type', 'material_recommendations', ['recommendation_type', 'priority_level'])
    
    # Create material_analytics table
    op.create_table('material_analytics',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('material_id', sa.String(length=50), nullable=False),
        
        # Time period for analytics
        sa.Column('period_start', sa.DateTime(), nullable=False),
        sa.Column('period_end', sa.DateTime(), nullable=False),
        sa.Column('period_type', sa.String(length=20), nullable=False),
        
        # Usage metrics
        sa.Column('unique_viewers', sa.Integer(), nullable=True),
        sa.Column('total_views', sa.Integer(), nullable=True),
        sa.Column('completion_count', sa.Integer(), nullable=True),
        sa.Column('average_reading_time', sa.Float(), nullable=True),
        sa.Column('bounce_rate', sa.Float(), nullable=True),
        
        # Engagement metrics
        sa.Column('average_scroll_depth', sa.Float(), nullable=True),
        sa.Column('sections_completion_rate', sa.JSON(), nullable=True),
        sa.Column('bookmark_rate', sa.Float(), nullable=True),
        sa.Column('share_rate', sa.Float(), nullable=True),
        
        # Quality metrics
        sa.Column('average_rating', sa.Float(), nullable=True),
        sa.Column('rating_distribution', sa.JSON(), nullable=True),
        sa.Column('average_difficulty_rating', sa.Float(), nullable=True),
        sa.Column('average_usefulness_rating', sa.Float(), nullable=True),
        sa.Column('recommendation_rate', sa.Float(), nullable=True),
        
        # Learning effectiveness
        sa.Column('average_comprehension_score', sa.Float(), nullable=True),
        sa.Column('concept_mastery_improvement', sa.JSON(), nullable=True),
        sa.Column('problem_solving_improvement', sa.Float(), nullable=True),
        
        # User segmentation
        sa.Column('beginner_completion_rate', sa.Float(), nullable=True),
        sa.Column('intermediate_completion_rate', sa.Float(), nullable=True),
        sa.Column('advanced_completion_rate', sa.Float(), nullable=True),
        sa.Column('persona_engagement', sa.JSON(), nullable=True),
        
        # Device and access patterns
        sa.Column('device_breakdown', sa.JSON(), nullable=True),
        sa.Column('access_time_patterns', sa.JSON(), nullable=True),
        sa.Column('referrer_breakdown', sa.JSON(), nullable=True),
        
        # Timestamps
        sa.Column('calculated_at', sa.DateTime(), nullable=True),
        
        sa.ForeignKeyConstraint(['material_id'], ['reading_materials.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Indexes for material_analytics
    op.create_index('idx_material_period', 'material_analytics', ['material_id', 'period_type', 'period_start'])
    
    # Create content_collections table
    op.create_table('content_collections',
        sa.Column('id', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        
        # Collection metadata
        sa.Column('collection_type', sa.String(length=30), nullable=False),
        sa.Column('difficulty_level', sa.String(length=20), nullable=True),
        sa.Column('estimated_time_hours', sa.Integer(), nullable=True),
        
        # Content organization
        sa.Column('material_ids', sa.JSON(), nullable=False),
        sa.Column('material_order', sa.JSON(), nullable=True),
        sa.Column('prerequisites', sa.JSON(), nullable=True),
        
        # Targeting
        sa.Column('target_personas', sa.JSON(), nullable=True),
        sa.Column('learning_objectives', sa.JSON(), nullable=True),
        sa.Column('skill_outcomes', sa.JSON(), nullable=True),
        
        # Quality metrics
        sa.Column('completion_rate', sa.Float(), nullable=True),
        sa.Column('user_ratings', sa.Float(), nullable=True),
        sa.Column('effectiveness_score', sa.Float(), nullable=True),
        
        # Metadata
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('author', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    """Remove reading materials system tables"""
    
    # Drop all reading materials tables
    op.drop_table('content_collections')
    op.drop_table('material_analytics')
    op.drop_table('material_recommendations')
    op.drop_table('user_reading_progress')
    op.drop_table('reading_materials')

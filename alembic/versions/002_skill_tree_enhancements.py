"""Skill Tree Enhancements - Phase 1

Revision ID: 002_skill_tree
Revises: 001_learning_paths
Create Date: 2025-07-31 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite
import json

# revision identifiers, used by Alembic.
revision = '002_skill_tree'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade():
    """Add skill tree enhancements to existing tables"""
    
    # Enhance Problems table with granular difficulty
    op.add_column('problems', sa.Column('sub_difficulty_level', sa.Integer, default=1))
    op.add_column('problems', sa.Column('conceptual_difficulty', sa.Integer, default=50))
    op.add_column('problems', sa.Column('implementation_complexity', sa.Integer, default=50))
    op.add_column('problems', sa.Column('prerequisite_skills', sa.JSON, default=lambda: []))
    op.add_column('problems', sa.Column('skill_tree_position', sa.JSON, default=lambda: {}))
    
    # Create problem clusters table for similarity grouping
    op.create_table('problem_clusters',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('cluster_name', sa.String(200), nullable=False),
        sa.Column('primary_skill_area', sa.String(50), nullable=False, index=True),
        sa.Column('difficulty_level', sa.String(20), nullable=False, index=True),
        sa.Column('representative_problems', sa.JSON, nullable=False),
        sa.Column('all_problems', sa.JSON, nullable=False),
        sa.Column('similarity_threshold', sa.Float, default=0.7),
        sa.Column('cluster_size', sa.Integer, default=0),
        sa.Column('avg_quality_score', sa.Float, default=0.0),
        sa.Column('avg_google_relevance', sa.Float, default=0.0),
        sa.Column('algorithm_tags', sa.JSON, nullable=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create user problem confidence tracking
    op.create_table('user_problem_confidence',
        sa.Column('user_id', sa.String(50), nullable=False),
        sa.Column('problem_id', sa.String(50), sa.ForeignKey('problems.id'), nullable=False),
        sa.Column('confidence_level', sa.Integer, default=0),  # 0-5 scale
        sa.Column('last_attempted', sa.DateTime),
        sa.Column('solve_time_seconds', sa.Integer),
        sa.Column('hints_used', sa.Integer, default=0),
        sa.Column('attempts_count', sa.Integer, default=0),
        sa.Column('first_solve_date', sa.DateTime),
        sa.Column('last_review_date', sa.DateTime),
        sa.Column('confidence_decay_factor', sa.Float, default=1.0),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('user_id', 'problem_id')
    )
    
    # Create skill area mastery tracking
    op.create_table('user_skill_mastery',
        sa.Column('user_id', sa.String(50), nullable=False),
        sa.Column('skill_area', sa.String(50), nullable=False),
        sa.Column('mastery_level', sa.Float, default=0.0),  # 0-100 scale
        sa.Column('problems_attempted', sa.Integer, default=0),
        sa.Column('problems_solved', sa.Integer, default=0),
        sa.Column('avg_confidence', sa.Float, default=0.0),
        sa.Column('last_activity', sa.DateTime),
        sa.Column('mastery_trend', sa.String(20), default='stable'),  # improving/stable/declining
        sa.Column('weak_patterns', sa.JSON, default=lambda: []),
        sa.Column('strong_patterns', sa.JSON, default=lambda: []),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('user_id', 'skill_area')
    )
    
    # Create skill tree navigation preferences
    op.create_table('user_skill_tree_preferences',
        sa.Column('user_id', sa.String(50), primary_key=True),
        sa.Column('preferred_view_mode', sa.String(20), default='columns'),  # columns/grid/tree
        sa.Column('show_confidence_overlay', sa.Boolean, default=True),
        sa.Column('auto_expand_clusters', sa.Boolean, default=False),
        sa.Column('highlight_prerequisites', sa.Boolean, default=True),
        sa.Column('visible_skill_areas', sa.JSON, default=lambda: []),
        sa.Column('bookmarked_problems', sa.JSON, default=lambda: []),
        sa.Column('custom_problem_groups', sa.JSON, default=lambda: []),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Add indexes for performance
    op.create_index('idx_problems_sub_difficulty', 'problems', ['difficulty', 'sub_difficulty_level'])
    op.create_index('idx_problems_skill_position', 'problems', ['platform', 'difficulty', 'sub_difficulty_level'])
    op.create_index('idx_clusters_skill_difficulty', 'problem_clusters', ['primary_skill_area', 'difficulty_level'])
    op.create_index('idx_confidence_user_level', 'user_problem_confidence', ['user_id', 'confidence_level'])
    op.create_index('idx_mastery_user_skill', 'user_skill_mastery', ['user_id', 'skill_area'])


def downgrade():
    """Remove skill tree enhancements"""
    
    # Drop new tables
    op.drop_table('user_skill_tree_preferences')
    op.drop_table('user_skill_mastery')
    op.drop_table('user_problem_confidence')
    op.drop_table('problem_clusters')
    
    # Remove columns from problems table
    op.drop_column('problems', 'skill_tree_position')
    op.drop_column('problems', 'prerequisite_skills')
    op.drop_column('problems', 'implementation_complexity')
    op.drop_column('problems', 'conceptual_difficulty')
    op.drop_column('problems', 'sub_difficulty_level')

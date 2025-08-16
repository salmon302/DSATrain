"""AI Features Integration

Revision ID: 005_ai_features_integration
Revises: 004_gated_practice_sessions
Create Date: 2025-08-14 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '005_ai_features_integration'
down_revision = '004_gated_practice'
branch_labels = None
depends_on = None


def upgrade():
    """Add AI features tables to support the data framework integration"""
    
    # Create problem_embeddings table
    op.create_table('problem_embeddings',
        sa.Column('problem_id', sa.String(length=50), nullable=False),
        sa.Column('title_embedding', sa.JSON(), nullable=False),
        sa.Column('description_embedding', sa.JSON(), nullable=False),
        sa.Column('combined_embedding', sa.JSON(), nullable=False),
        sa.Column('embedding_model', sa.String(length=50), nullable=True),
        sa.Column('embedding_dimension', sa.Integer(), nullable=True),
        sa.Column('embedding_quality_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['problem_id'], ['problems.id'], ),
        sa.PrimaryKeyConstraint('problem_id')
    )
    op.create_index('idx_embedding_quality', 'problem_embeddings', ['embedding_quality_score'], unique=False)

    # Create problem_difficulty_vectors table
    op.create_table('problem_difficulty_vectors',
        sa.Column('problem_id', sa.String(length=50), nullable=False),
        sa.Column('algorithmic_complexity', sa.Float(), nullable=False),
        sa.Column('implementation_difficulty', sa.Float(), nullable=False),
        sa.Column('mathematical_content', sa.Float(), nullable=False),
        sa.Column('data_structure_usage', sa.Float(), nullable=False),
        sa.Column('optimization_required', sa.Float(), nullable=False),
        sa.Column('overall_difficulty', sa.Float(), nullable=False),
        sa.Column('difficulty_confidence', sa.Float(), nullable=True),
        sa.Column('vector_version', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['problem_id'], ['problems.id'], ),
        sa.PrimaryKeyConstraint('problem_id')
    )
    op.create_index('idx_overall_difficulty', 'problem_difficulty_vectors', ['overall_difficulty'], unique=False)
    op.create_index('idx_algo_complexity', 'problem_difficulty_vectors', ['algorithmic_complexity'], unique=False)

    # Create concept_nodes table
    op.create_table('concept_nodes',
        sa.Column('id', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('difficulty_level', sa.Integer(), nullable=True),
        sa.Column('problem_count', sa.Integer(), nullable=True),
        sa.Column('graph_version', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_concept_difficulty', 'concept_nodes', ['difficulty_level'], unique=False)

    # Create concept_prerequisites table
    op.create_table('concept_prerequisites',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('concept_id', sa.String(length=50), nullable=False),
        sa.Column('prerequisite_id', sa.String(length=50), nullable=False),
        sa.Column('importance', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['concept_id'], ['concept_nodes.id'], ),
        sa.ForeignKeyConstraint(['prerequisite_id'], ['concept_nodes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_concept_prereq', 'concept_prerequisites', ['concept_id', 'prerequisite_id'], unique=False)

    # Create problem_concept_mapping table
    op.create_table('problem_concept_mapping',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('problem_id', sa.String(length=50), nullable=False),
        sa.Column('concept_id', sa.String(length=50), nullable=False),
        sa.Column('relevance_score', sa.Float(), nullable=True),
        sa.Column('is_primary_concept', sa.Boolean(), nullable=True),
        sa.Column('mapping_source', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['concept_id'], ['concept_nodes.id'], ),
        sa.ForeignKeyConstraint(['problem_id'], ['problems.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_problem_concept', 'problem_concept_mapping', ['problem_id', 'concept_id'], unique=False)
    op.create_index('idx_primary_concepts', 'problem_concept_mapping', ['problem_id', 'is_primary_concept'], unique=False)

    # Create google_interview_features table
    op.create_table('google_interview_features',
        sa.Column('problem_id', sa.String(length=50), nullable=False),
        sa.Column('base_google_relevance', sa.Float(), nullable=False),
        sa.Column('frequency_score', sa.Float(), nullable=False),
        sa.Column('difficulty_appropriateness', sa.Float(), nullable=False),
        sa.Column('concept_coverage', sa.Float(), nullable=False),
        sa.Column('implementation_complexity', sa.Float(), nullable=False),
        sa.Column('final_interview_probability', sa.Float(), nullable=False),
        sa.Column('feature_weights', sa.JSON(), nullable=False),
        sa.Column('features_version', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['problem_id'], ['problems.id'], ),
        sa.PrimaryKeyConstraint('problem_id')
    )
    op.create_index('idx_interview_probability', 'google_interview_features', ['final_interview_probability'], unique=False)
    op.create_index('idx_google_relevance', 'google_interview_features', ['base_google_relevance'], unique=False)

    # Create problem_quality_scores table
    op.create_table('problem_quality_scores',
        sa.Column('problem_id', sa.String(length=50), nullable=False),
        sa.Column('completeness_score', sa.Float(), nullable=False),
        sa.Column('clarity_score', sa.Float(), nullable=False),
        sa.Column('specificity_score', sa.Float(), nullable=False),
        sa.Column('educational_value_score', sa.Float(), nullable=False),
        sa.Column('content_quality_overall', sa.Float(), nullable=False),
        sa.Column('topic_relevance', sa.Float(), nullable=False),
        sa.Column('difficulty_appropriateness', sa.Float(), nullable=False),
        sa.Column('frequency_score', sa.Float(), nullable=False),
        sa.Column('company_alignment', sa.Float(), nullable=False),
        sa.Column('google_relevance_overall', sa.Float(), nullable=False),
        sa.Column('overall_quality_score', sa.Float(), nullable=False),
        sa.Column('recommendation', sa.String(length=30), nullable=False),
        sa.Column('scoring_model_version', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['problem_id'], ['problems.id'], ),
        sa.PrimaryKeyConstraint('problem_id')
    )
    op.create_index('idx_overall_quality', 'problem_quality_scores', ['overall_quality_score'], unique=False)
    op.create_index('idx_recommendation', 'problem_quality_scores', ['recommendation'], unique=False)
    op.create_index('idx_google_relevance_overall', 'problem_quality_scores', ['google_relevance_overall'], unique=False)

    # Create behavioral_competencies table
    op.create_table('behavioral_competencies',
        sa.Column('id', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('parent_competency_id', sa.String(length=50), nullable=True),
        sa.Column('competency_level', sa.Integer(), nullable=True),
        sa.Column('assessment_criteria', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['parent_competency_id'], ['behavioral_competencies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_competency_level', 'behavioral_competencies', ['competency_level'], unique=False)

    # Create behavioral_questions table
    op.create_table('behavioral_questions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('competency_id', sa.String(length=50), nullable=False),
        sa.Column('question_type', sa.String(length=30), nullable=True),
        sa.Column('difficulty_level', sa.String(length=20), nullable=True),
        sa.Column('source_document', sa.String(length=100), nullable=True),
        sa.Column('source_type', sa.String(length=30), nullable=True),
        sa.Column('expected_response_time', sa.Integer(), nullable=True),
        sa.Column('follow_up_questions', sa.JSON(), nullable=True),
        sa.Column('evaluation_criteria', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['competency_id'], ['behavioral_competencies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_competency_difficulty', 'behavioral_questions', ['competency_id', 'difficulty_level'], unique=False)

    # Create conversation_templates table
    op.create_table('conversation_templates',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('competency_id', sa.String(length=50), nullable=False),
        sa.Column('template_name', sa.String(length=100), nullable=False),
        sa.Column('opening_questions', sa.JSON(), nullable=False),
        sa.Column('follow_up_prompts', sa.JSON(), nullable=False),
        sa.Column('probing_questions', sa.JSON(), nullable=False),
        sa.Column('evaluation_criteria', sa.JSON(), nullable=False),
        sa.Column('template_type', sa.String(length=30), nullable=True),
        sa.Column('estimated_duration', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['competency_id'], ['behavioral_competencies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_competency_template', 'conversation_templates', ['competency_id', 'template_type'], unique=False)

    # Create data_pipeline_status table
    op.create_table('data_pipeline_status',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('pipeline_component', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('total_records', sa.Integer(), nullable=True),
        sa.Column('processed_records', sa.Integer(), nullable=True),
        sa.Column('failed_records', sa.Integer(), nullable=True),
        sa.Column('quality_score', sa.Float(), nullable=True),
        sa.Column('status_message', sa.Text(), nullable=True),
        sa.Column('error_details', sa.JSON(), nullable=True),
        sa.Column('pipeline_version', sa.String(length=20), nullable=True),
        sa.Column('execution_time_seconds', sa.Float(), nullable=True),
        sa.Column('last_updated', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_pipeline_status', 'data_pipeline_status', ['pipeline_component', 'status'], unique=False)
    op.create_index('idx_pipeline_updated', 'data_pipeline_status', ['last_updated'], unique=False)


def downgrade():
    """Remove AI features tables"""
    
    # Drop all AI features tables
    op.drop_table('data_pipeline_status')
    op.drop_table('conversation_templates')
    op.drop_table('behavioral_questions')
    op.drop_table('behavioral_competencies')
    op.drop_table('problem_quality_scores')
    op.drop_table('google_interview_features')
    op.drop_table('problem_concept_mapping')
    op.drop_table('concept_prerequisites')
    op.drop_table('concept_nodes')
    op.drop_table('problem_difficulty_vectors')
    op.drop_table('problem_embeddings')

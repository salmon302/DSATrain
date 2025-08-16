"""Single-User Redesign Core: Problem extensions + SRS tables

Revision ID: 003_single_user_redesign
Revises: 002_skill_tree
Create Date: 2025-08-14 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003_single_user_redesign'
down_revision = '002_skill_tree'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Problem table extensions
    with op.batch_alter_table('problems') as batch_op:
        batch_op.add_column(sa.Column('pattern_tags', sa.JSON))
        batch_op.add_column(sa.Column('skill_areas', sa.JSON))
        batch_op.add_column(sa.Column('granular_difficulty', sa.Integer))
        batch_op.add_column(sa.Column('interview_frequency', sa.Float))
        batch_op.add_column(sa.Column('company_tags', sa.JSON))
        batch_op.add_column(sa.Column('source_dataset', sa.String(length=100)))
        batch_op.add_column(sa.Column('canonical_solutions', sa.JSON))
        batch_op.add_column(sa.Column('visual_aids', sa.JSON))
        batch_op.add_column(sa.Column('verbal_explanations', sa.JSON))
        batch_op.add_column(sa.Column('prerequisite_assessment', sa.JSON))
        batch_op.add_column(sa.Column('elaborative_prompts', sa.JSON))
        batch_op.add_column(sa.Column('working_memory_load', sa.Integer))

    # Review/SRS tables
    op.create_table(
        'review_cards',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('problem_id', sa.String(50), sa.ForeignKey('problems.id'), nullable=False, index=True),
        sa.Column('next_review_at', sa.DateTime, index=True),
        sa.Column('interval_days', sa.Integer, server_default='1'),
        sa.Column('ease', sa.Float, server_default='2.5'),
        sa.Column('reps', sa.Integer, server_default='0'),
        sa.Column('lapses', sa.Integer, server_default='0'),
        sa.Column('last_outcome', sa.String(20)),
        sa.Column('deck', sa.String(50), server_default='problems'),
    )

    op.create_table(
        'review_history',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('problem_id', sa.String(50), sa.ForeignKey('problems.id'), nullable=False, index=True),
        sa.Column('outcome', sa.String(20), nullable=False),
        sa.Column('time_spent', sa.Integer),
        sa.Column('notes', sa.Text),
        sa.Column('timestamp', sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        'problem_attempts',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('problem_id', sa.String(50), sa.ForeignKey('problems.id'), nullable=False, index=True),
        sa.Column('code', sa.Text),
        sa.Column('language', sa.String(30)),
        sa.Column('status', sa.String(20)),
        sa.Column('time_spent', sa.Integer),
        sa.Column('test_results', sa.JSON),
        sa.Column('mistakes', sa.JSON),
        sa.Column('reflection', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        'user_cognitive_profile',
        sa.Column('user_id', sa.String(50), primary_key=True),
        sa.Column('working_memory_capacity', sa.Integer),
        sa.Column('learning_style_preference', sa.String(20)),
        sa.Column('visual_vs_verbal', sa.Float),
        sa.Column('processing_speed', sa.String(20)),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        'elaborative_sessions',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('problem_id', sa.String(50), sa.ForeignKey('problems.id'), nullable=False, index=True),
        sa.Column('why_questions', sa.JSON),
        sa.Column('how_questions', sa.JSON),
        sa.Column('responses', sa.JSON),
        sa.Column('timestamp', sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        'retrieval_practice',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('problem_id', sa.String(50), sa.ForeignKey('problems.id'), nullable=False, index=True),
        sa.Column('retrieval_type', sa.String(50)),
        sa.Column('success_rate', sa.Float),
        sa.Column('retrieval_strength', sa.Float),
        sa.Column('timestamp', sa.DateTime, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('retrieval_practice')
    op.drop_table('elaborative_sessions')
    op.drop_table('user_cognitive_profile')
    op.drop_table('problem_attempts')
    op.drop_table('review_history')
    op.drop_table('review_cards')

    with op.batch_alter_table('problems') as batch_op:
        batch_op.drop_column('working_memory_load')
        batch_op.drop_column('elaborative_prompts')
        batch_op.drop_column('prerequisite_assessment')
        batch_op.drop_column('verbal_explanations')
        batch_op.drop_column('visual_aids')
        batch_op.drop_column('canonical_solutions')
        batch_op.drop_column('source_dataset')
        batch_op.drop_column('company_tags')
        batch_op.drop_column('interview_frequency')
        batch_op.drop_column('granular_difficulty')
        batch_op.drop_column('skill_areas')
        batch_op.drop_column('pattern_tags')

"""Gated practice sessions table

Revision ID: 004_gated_practice
Revises: 003_single_user_redesign
Create Date: 2025-08-14 00:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '004_gated_practice'
down_revision = '003_single_user_redesign'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'practice_gate_sessions',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('session_id', sa.String(100), nullable=False),
        sa.Column('user_id', sa.String(50), server_default='default_user', nullable=True),
        sa.Column('problem_id', sa.String(50), sa.ForeignKey('problems.id'), nullable=False),
        sa.Column('gates', sa.JSON, server_default=sa.text("'{""dry_run"": false, ""pseudocode"": false, ""code"": false}'")),
        sa.Column('unlocked', sa.Boolean, server_default=sa.text('0')),
        sa.Column('started_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )
    # Indexes and constraints
    op.create_index('ix_practice_gate_sessions_session_id', 'practice_gate_sessions', ['session_id'], unique=True)
    op.create_index('ix_practice_gate_sessions_user_id', 'practice_gate_sessions', ['user_id'])
    op.create_index('ix_practice_gate_sessions_problem_id', 'practice_gate_sessions', ['problem_id'])
    op.create_index('ix_practice_gate_sessions_started_at', 'practice_gate_sessions', ['started_at'])
    op.create_index('ix_practice_gate_sessions_updated_at', 'practice_gate_sessions', ['updated_at'])


def downgrade() -> None:
    op.drop_index('ix_practice_gate_sessions_updated_at', table_name='practice_gate_sessions')
    op.drop_index('ix_practice_gate_sessions_started_at', table_name='practice_gate_sessions')
    op.drop_index('ix_practice_gate_sessions_problem_id', table_name='practice_gate_sessions')
    op.drop_index('ix_practice_gate_sessions_user_id', table_name='practice_gate_sessions')
    op.drop_index('ix_practice_gate_sessions_session_id', table_name='practice_gate_sessions')
    op.drop_table('practice_gate_sessions')

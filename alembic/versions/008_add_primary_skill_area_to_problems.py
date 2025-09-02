"""
add primary_skill_area to problems

Revision ID: 008_add_primary_skill_area
Revises: 007_reading_progress_index_rename
Create Date: 2025-08-18
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '008_add_primary_skill_area'
down_revision = '007_reading_progress_index_rename'
branch_labels = None
depends_on = None


def upgrade():
    # Add new column with index; nullable to allow backfill in-place
    with op.batch_alter_table('problems') as batch_op:
        batch_op.add_column(sa.Column('primary_skill_area', sa.String(length=50), nullable=True))
        batch_op.create_index('idx_primary_skill_area', ['primary_skill_area'])


def downgrade():
    with op.batch_alter_table('problems') as batch_op:
        batch_op.drop_index('idx_primary_skill_area')
        batch_op.drop_column('primary_skill_area')

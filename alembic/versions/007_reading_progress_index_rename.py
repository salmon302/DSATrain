"""
Rename index for user_reading_progress to avoid SQLite global index collision.

Revision ID: 007_reading_progress_index_rename
Revises: 006_reading_materials_system
Create Date: 2025-08-15
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '007_reading_progress_index_rename'
down_revision = '006_reading_materials_system'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    dialect_name = bind.dialect.name

    old_index = 'idx_user_progress'
    new_index = 'idx_user_reading_progress_pct'
    table = 'user_reading_progress'

    # Drop old index if it exists
    try:
        if dialect_name == 'sqlite':
            # SQLite requires raw SQL for DROP INDEX IF EXISTS
            op.execute(f"DROP INDEX IF EXISTS {old_index}")
        else:
            op.drop_index(old_index, table_name=table)
    except Exception:
        # Index might not exist; continue
        pass

    # Create new index (guard in case it already exists)
    try:
        op.create_index(new_index, table, ['user_id', 'progress_percentage'])
    except Exception:
        pass


def downgrade():
    # Best-effort rollback: drop the new index and recreate the old one
    new_index = 'idx_user_reading_progress_pct'
    old_index = 'idx_user_progress'
    table = 'user_reading_progress'

    try:
        op.drop_index(new_index, table_name=table)
    except Exception:
        pass

    try:
        op.create_index(old_index, table, ['user_id', 'progress_percentage'])
    except Exception:
        pass

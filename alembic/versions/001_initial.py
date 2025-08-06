"""Initial database schema

Revision ID: 001_initial
Revises: 
Create Date: 2025-07-31 09:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Create initial tables - tables already exist, so this is just a placeholder"""
    pass


def downgrade():
    """Remove initial tables"""
    pass

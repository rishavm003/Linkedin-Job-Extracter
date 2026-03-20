"""Add fulltext search column

Revision ID: 002_add_fulltext_search
Revises: 001_initial_jobs_table
Create Date: 2026-03-20

"""
from typing import Sequence, Union

# type: ignore  # Alembic migration file - imports only available in migration context
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002_add_fulltext_search'
down_revision: str = '001_initial_jobs_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add tsvector search_vector column and GIN index."""
    op.execute("""
        ALTER TABLE jobs 
        ADD COLUMN search_vector tsvector
        GENERATED ALWAYS AS (
            setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
            setweight(to_tsvector('english', coalesce(company, '')), 'B') ||
            setweight(to_tsvector('english', coalesce(description_clean, '')), 'C')
        ) STORED;
    """)
    
    op.execute("CREATE INDEX ix_jobs_search_vector ON jobs USING GIN (search_vector);")


def downgrade() -> None:
    """Drop search_vector column and index."""
    op.execute("DROP INDEX IF EXISTS ix_jobs_search_vector;")
    op.execute("ALTER TABLE jobs DROP COLUMN IF EXISTS search_vector;")

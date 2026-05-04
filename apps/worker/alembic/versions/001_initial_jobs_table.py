"""Initial jobs table migration

Revision ID: 001_initial_jobs_table
Revises: 
Create Date: 2026-03-20

"""
from typing import Sequence, Union

# type: ignore  # Alembic migration file - imports only available in migration context
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial_jobs_table'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create jobs table with all columns and indexes."""
    op.create_table(
        'jobs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('fingerprint', sa.String(64), unique=True, nullable=False, index=True),
        
        # Core fields
        sa.Column('title', sa.String(300), nullable=False),
        sa.Column('company', sa.String(200), nullable=False),
        sa.Column('location', sa.String(200)),
        sa.Column('is_remote', sa.Boolean, default=False),
        sa.Column('country', sa.String(100)),
        sa.Column('city', sa.String(100)),
        
        # Portal info
        sa.Column('source_portal', sa.String(50), nullable=False, index=True),
        sa.Column('portal_display_name', sa.String(100)),
        sa.Column('apply_url', sa.Text, nullable=False),
        
        # Categorisation
        sa.Column('job_type', sa.String(50), default='Full-time'),
        sa.Column('seniority', sa.String(50), default='Entry Level', index=True),
        sa.Column('domain', sa.String(100), index=True),
        
        # NLP-extracted (stored as JSON arrays)
        sa.Column('skills', postgresql.JSON, default=list),
        sa.Column('qualifications', postgresql.JSON, default=list),
        sa.Column('soft_skills', postgresql.JSON, default=list),
        
        # Salary
        sa.Column('salary_min', sa.Float, nullable=True),
        sa.Column('salary_max', sa.Float, nullable=True),
        sa.Column('salary_currency', sa.String(10), nullable=True),
        sa.Column('salary_period', sa.String(20), nullable=True),
        sa.Column('salary_disclosed', sa.Boolean, default=False),
        sa.Column('salary_raw', sa.String(200), nullable=True),
        
        # Dates
        sa.Column('posted_at', sa.DateTime, nullable=True),
        sa.Column('scraped_at', sa.DateTime, default=sa.func.now()),
        sa.Column('processed_at', sa.DateTime, default=sa.func.now()),
        
        # Description
        sa.Column('description_clean', sa.Text),
        sa.Column('description_summary', sa.Text),
        
        # Fresher flags
        sa.Column('is_fresher_friendly', sa.Boolean, default=False, index=True),
        sa.Column('requires_experience', sa.String(100), nullable=True),
        
        # Soft-delete + active flag
        sa.Column('is_active', sa.Boolean, default=True, index=True),
    )
    
    # Create composite indexes
    op.create_index('ix_jobs_domain_seniority', 'jobs', ['domain', 'seniority'])
    op.create_index('ix_jobs_portal_active', 'jobs', ['source_portal', 'is_active'])
    op.create_index('ix_jobs_fresher_remote', 'jobs', ['is_fresher_friendly', 'is_remote'])


def downgrade() -> None:
    """Drop jobs table and all indexes."""
    op.drop_index('ix_jobs_fresher_remote', table_name='jobs')
    op.drop_index('ix_jobs_portal_active', table_name='jobs')
    op.drop_index('ix_jobs_domain_seniority', table_name='jobs')
    op.drop_table('jobs')

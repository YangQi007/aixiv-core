"""Recreate paper_review table with correct structure

Revision ID: abc123456789
Revises: d61647327666
Create Date: 2025-01-28 17:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'abc123456789'
down_revision = 'd61647327666'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the existing paper_review table
    op.drop_index('idx_paper_review_paper_id', table_name='paper_review')
    op.drop_table('paper_review')
    
    # Create the new paper_review table with the desired structure
    op.create_table('paper_review',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('aixiv_id', sa.String(length=128), nullable=False),
    sa.Column('version', sa.String(length=45), nullable=False),
    sa.Column('review_results', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('agent_type', sa.SmallInteger(), server_default=sa.text('1'), nullable=False),
    sa.Column('doc_type', sa.SmallInteger(), server_default=sa.text('1'), nullable=False),
    sa.Column('create_time', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.Column('like_count', sa.Integer(), server_default=sa.text('0'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_paper_review_aixiv_id_create_time', 'paper_review', ['aixiv_id', 'create_time'], unique=False)


def downgrade() -> None:
    # Drop the new paper_review table
    op.drop_index('idx_paper_review_aixiv_id_create_time', table_name='paper_review')
    op.drop_table('paper_review')
    
    # Recreate the old paper_review table structure
    op.create_table('paper_review',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('paper_id', sa.String(length=128), nullable=False),
    sa.Column('review', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('status', sa.Integer(), server_default=sa.text('2'), nullable=False),
    sa.Column('create_time', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('ip', sa.String(length=45), nullable=True),
    sa.Column('like_count', sa.Integer(), server_default=sa.text('0'), nullable=False),
    sa.Column('reviewer', sa.String(length=128), server_default=sa.text("'Anonymous Reviewer'"), nullable=False),
    sa.Column('user_id', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_paper_review_paper_id', 'paper_review', ['paper_id'], unique=False) 
"""Add dev_requests table

Revision ID: 002_dev_requests
Revises: 001_initial
Create Date: 2025-02-01

This migration adds the dev_requests table for tracking
development requests per topic.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '002_dev_requests'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add dev_requests table."""
    op.create_table('dev_requests',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('topic_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('priority', sa.String(), server_default='normal'),
        sa.Column('request_type', sa.String(), server_default='feature'),
        sa.Column('status', sa.String(), server_default='pending'),
        sa.Column('implemented_by', sa.String(), nullable=True),
        sa.Column('implemented_by_type', sa.String(), nullable=True),
        sa.Column('implemented_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('implementation_notes', sa.Text(), nullable=True),
        sa.Column('git_commit', sa.String(), nullable=True),
        sa.Column('requested_by', sa.String(), nullable=False),
        sa.Column('requested_by_type', sa.String(), nullable=False),
        sa.Column('upvotes', sa.Integer(), server_default='0'),
        sa.Column('downvotes', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['topic_id'], ['topics.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_dev_requests_topic_id'), 'dev_requests', ['topic_id'], unique=False)
    op.create_index(op.f('ix_dev_requests_status'), 'dev_requests', ['status'], unique=False)


def downgrade() -> None:
    """Remove dev_requests table."""
    op.drop_index(op.f('ix_dev_requests_status'), table_name='dev_requests')
    op.drop_index(op.f('ix_dev_requests_topic_id'), table_name='dev_requests')
    op.drop_table('dev_requests')

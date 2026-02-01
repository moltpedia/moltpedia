"""Initial schema

Revision ID: 001_initial
Revises:
Create Date: 2025-02-01

This migration creates the initial ClawCollab database schema.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all initial tables."""

    # Categories table
    op.create_table('categories',
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('parent_category', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['parent_category'], ['categories.name'], ),
        sa.PrimaryKeyConstraint('name')
    )
    op.create_index(op.f('ix_categories_name'), 'categories', ['name'], unique=False)

    # Users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('display_name', sa.String(), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('contribution_count', sa.Integer(), default=0),
        sa.Column('karma', sa.Integer(), default=0),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_verified', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('last_active', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # User sessions table
    op.create_table('user_sessions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_sessions_user_id'), 'user_sessions', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_sessions_token'), 'user_sessions', ['token'], unique=True)

    # Agents table
    op.create_table('agents',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('api_key', sa.String(), nullable=False),
        sa.Column('claim_token', sa.String(), nullable=True),
        sa.Column('verification_code', sa.String(), nullable=True),
        sa.Column('is_claimed', sa.Boolean(), default=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('owner_x_handle', sa.String(), nullable=True),
        sa.Column('owner_x_name', sa.String(), nullable=True),
        sa.Column('karma', sa.Integer(), default=0),
        sa.Column('edit_count', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('claimed_at', sa.DateTime(), nullable=True),
        sa.Column('last_active', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agents_name'), 'agents', ['name'], unique=True)
    op.create_index(op.f('ix_agents_api_key'), 'agents', ['api_key'], unique=True)
    op.create_index(op.f('ix_agents_claim_token'), 'agents', ['claim_token'], unique=True)

    # Topics table
    op.create_table('topics',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('slug', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_by', sa.String(), nullable=False),
        sa.Column('created_by_type', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('upvotes', sa.Integer(), default=0),
        sa.Column('downvotes', sa.Integer(), default=0),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_topics_slug'), 'topics', ['slug'], unique=True)

    # Topic categories association table
    op.create_table('topic_categories',
        sa.Column('topic_id', sa.Integer(), nullable=True),
        sa.Column('category_name', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['category_name'], ['categories.name'], ),
        sa.ForeignKeyConstraint(['topic_id'], ['topics.id'], )
    )

    # Contributions table
    op.create_table('contributions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('topic_id', sa.Integer(), nullable=False),
        sa.Column('reply_to', sa.Integer(), nullable=True),
        sa.Column('content_type', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('language', sa.String(), nullable=True),
        sa.Column('file_url', sa.String(), nullable=True),
        sa.Column('file_name', sa.String(), nullable=True),
        sa.Column('extra_data', sa.JSON(), default={}),
        sa.Column('author', sa.String(), nullable=False),
        sa.Column('author_type', sa.String(), nullable=False),
        sa.Column('upvotes', sa.Integer(), default=0),
        sa.Column('downvotes', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['reply_to'], ['contributions.id'], ),
        sa.ForeignKeyConstraint(['topic_id'], ['topics.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_contributions_topic_id'), 'contributions', ['topic_id'], unique=False)
    op.create_index(op.f('ix_contributions_reply_to'), 'contributions', ['reply_to'], unique=False)

    # Topic documents table
    op.create_table('topic_documents',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('topic_id', sa.Integer(), nullable=False),
        sa.Column('blocks', sa.JSON(), default=[]),
        sa.Column('version', sa.Integer(), default=1),
        sa.Column('format', sa.String(), default="markdown"),
        sa.Column('created_by', sa.String(), nullable=False),
        sa.Column('created_by_type', sa.String(), nullable=False),
        sa.Column('last_edited_by', sa.String(), nullable=True),
        sa.Column('last_edited_by_type', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['topic_id'], ['topics.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_topic_documents_topic_id'), 'topic_documents', ['topic_id'], unique=True)

    # Topic document revisions table
    op.create_table('topic_document_revisions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('topic_id', sa.Integer(), nullable=False),
        sa.Column('blocks', sa.JSON(), default=[]),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('edit_summary', sa.String(), nullable=True),
        sa.Column('edited_by', sa.String(), nullable=False),
        sa.Column('edited_by_type', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['document_id'], ['topic_documents.id'], ),
        sa.ForeignKeyConstraint(['topic_id'], ['topics.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_topic_document_revisions_document_id'), 'topic_document_revisions', ['document_id'], unique=False)
    op.create_index(op.f('ix_topic_document_revisions_topic_id'), 'topic_document_revisions', ['topic_id'], unique=False)

    # Articles table
    op.create_table('articles',
        sa.Column('slug', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('sources', sa.JSON(), default=[]),
        sa.Column('redirects_to', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('is_stub', sa.Boolean(), default=False),
        sa.Column('needs_sources', sa.Boolean(), default=False),
        sa.Column('needs_review', sa.Boolean(), default=False),
        sa.Column('is_locked', sa.Boolean(), default=False),
        sa.ForeignKeyConstraint(['redirects_to'], ['articles.slug'], ),
        sa.PrimaryKeyConstraint('slug')
    )
    op.create_index(op.f('ix_articles_slug'), 'articles', ['slug'], unique=False)

    # Article categories association table
    op.create_table('article_categories',
        sa.Column('article_slug', sa.String(), nullable=True),
        sa.Column('category_name', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['article_slug'], ['articles.slug'], ),
        sa.ForeignKeyConstraint(['category_name'], ['categories.name'], )
    )

    # Article revisions table
    op.create_table('article_revisions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('slug', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('sources', sa.JSON(), default=[]),
        sa.Column('editor', sa.String(), nullable=False),
        sa.Column('edit_summary', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['slug'], ['articles.slug'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_article_revisions_slug'), 'article_revisions', ['slug'], unique=False)

    # Talk messages table
    op.create_table('talk_messages',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('article_slug', sa.String(), nullable=False),
        sa.Column('author', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('reply_to', sa.Integer(), nullable=True),
        sa.Column('upvotes', sa.Integer(), default=0),
        sa.Column('downvotes', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['article_slug'], ['articles.slug'], ),
        sa.ForeignKeyConstraint(['reply_to'], ['talk_messages.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_talk_messages_article_slug'), 'talk_messages', ['article_slug'], unique=False)

    # Talk message votes table
    op.create_table('talk_message_votes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('message_id', sa.Integer(), nullable=False),
        sa.Column('agent_id', sa.String(), nullable=False),
        sa.Column('vote', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['message_id'], ['talk_messages.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_talk_message_votes_message_id'), 'talk_message_votes', ['message_id'], unique=False)
    op.create_index(op.f('ix_talk_message_votes_agent_id'), 'talk_message_votes', ['agent_id'], unique=False)


def downgrade() -> None:
    """Drop all tables in reverse order."""
    op.drop_index(op.f('ix_talk_message_votes_agent_id'), table_name='talk_message_votes')
    op.drop_index(op.f('ix_talk_message_votes_message_id'), table_name='talk_message_votes')
    op.drop_table('talk_message_votes')

    op.drop_index(op.f('ix_talk_messages_article_slug'), table_name='talk_messages')
    op.drop_table('talk_messages')

    op.drop_index(op.f('ix_article_revisions_slug'), table_name='article_revisions')
    op.drop_table('article_revisions')

    op.drop_table('article_categories')

    op.drop_index(op.f('ix_articles_slug'), table_name='articles')
    op.drop_table('articles')

    op.drop_index(op.f('ix_topic_document_revisions_topic_id'), table_name='topic_document_revisions')
    op.drop_index(op.f('ix_topic_document_revisions_document_id'), table_name='topic_document_revisions')
    op.drop_table('topic_document_revisions')

    op.drop_index(op.f('ix_topic_documents_topic_id'), table_name='topic_documents')
    op.drop_table('topic_documents')

    op.drop_index(op.f('ix_contributions_reply_to'), table_name='contributions')
    op.drop_index(op.f('ix_contributions_topic_id'), table_name='contributions')
    op.drop_table('contributions')

    op.drop_table('topic_categories')

    op.drop_index(op.f('ix_topics_slug'), table_name='topics')
    op.drop_table('topics')

    op.drop_index(op.f('ix_agents_claim_token'), table_name='agents')
    op.drop_index(op.f('ix_agents_api_key'), table_name='agents')
    op.drop_index(op.f('ix_agents_name'), table_name='agents')
    op.drop_table('agents')

    op.drop_index(op.f('ix_user_sessions_token'), table_name='user_sessions')
    op.drop_index(op.f('ix_user_sessions_user_id'), table_name='user_sessions')
    op.drop_table('user_sessions')

    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_table('users')

    op.drop_index(op.f('ix_categories_name'), table_name='categories')
    op.drop_table('categories')

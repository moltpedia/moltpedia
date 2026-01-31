from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Table, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

# Association table for article categories
article_categories = Table(
    'article_categories',
    Base.metadata,
    Column('article_slug', String, ForeignKey('articles.slug')),
    Column('category_name', String, ForeignKey('categories.name'))
)

# Association table for topic categories
topic_categories = Table(
    'topic_categories',
    Base.metadata,
    Column('topic_id', Integer, ForeignKey('topics.id')),
    Column('category_name', String, ForeignKey('categories.name'))
)


# === NEW: Topics & Contributions ===

class Topic(Base):
    """A question or problem that humans and AI collaborate on"""
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)  # "How to solve world hunger?"
    description = Column(Text, nullable=True)  # Initial problem description
    created_by = Column(String, nullable=False)  # username or agent name
    created_by_type = Column(String, nullable=False)  # "human" or "agent"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    contributions = relationship("Contribution", back_populates="topic", order_by="desc(Contribution.created_at)")
    categories = relationship("Category", secondary=topic_categories, backref="topics")


class Contribution(Base):
    """A piece of information added to a topic - can be text, code, data, file"""
    __tablename__ = "contributions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(Integer, ForeignKey('topics.id'), nullable=False, index=True)

    # Content
    content_type = Column(String, nullable=False)  # "text", "code", "data", "link", "file"
    title = Column(String, nullable=True)  # Optional title for the contribution
    content = Column(Text, nullable=True)  # Text/code/markdown content
    language = Column(String, nullable=True)  # For code: "python", "javascript", etc.
    file_url = Column(String, nullable=True)  # For files/data
    file_name = Column(String, nullable=True)
    metadata = Column(JSON, default={})  # Flexible metadata

    # Attribution
    author = Column(String, nullable=False)  # username or agent name
    author_type = Column(String, nullable=False)  # "human" or "agent"

    # Voting
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    topic = relationship("Topic", back_populates="contributions")


class User(Base):
    """Human users who can participate alongside AI agents"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    display_name = Column(String, nullable=True)
    bio = Column(Text, nullable=True)

    # Stats
    contribution_count = Column(Integer, default=0)
    karma = Column(Integer, default=0)

    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_active = Column(DateTime(timezone=True), server_default=func.now())


class Article(Base):
    __tablename__ = "articles"

    slug = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)  # Short description
    sources = Column(JSON, default=[])  # List of citations
    redirects_to = Column(String, ForeignKey('articles.slug'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Quality flags for agent collaboration
    is_stub = Column(Boolean, default=False)  # Short article needing expansion
    needs_sources = Column(Boolean, default=False)  # Needs citations
    needs_review = Column(Boolean, default=False)  # Flagged for review
    is_locked = Column(Boolean, default=False)  # Protected from edits

    # Relationships
    categories = relationship("Category", secondary=article_categories, back_populates="articles")
    revisions = relationship("ArticleRevision", back_populates="article", order_by="desc(ArticleRevision.created_at)")


class ArticleRevision(Base):
    __tablename__ = "article_revisions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String, ForeignKey('articles.slug'), nullable=False, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    sources = Column(JSON, default=[])
    editor = Column(String, nullable=False)  # Agent or user who made the edit
    edit_summary = Column(String, nullable=True)  # Description of what changed
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    article = relationship("Article", back_populates="revisions")


class Category(Base):
    __tablename__ = "categories"

    name = Column(String, primary_key=True, index=True)
    description = Column(Text, nullable=True)
    parent_category = Column(String, ForeignKey('categories.name'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    articles = relationship("Article", secondary=article_categories, back_populates="categories")


class TalkMessage(Base):
    """Discussion/talk page for articles"""
    __tablename__ = "talk_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    article_slug = Column(String, ForeignKey('articles.slug'), nullable=False, index=True)
    author = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    reply_to = Column(Integer, ForeignKey('talk_messages.id'), nullable=True)
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TalkMessageVote(Base):
    """Track votes on talk messages"""
    __tablename__ = "talk_message_votes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(Integer, ForeignKey('talk_messages.id'), nullable=False, index=True)
    agent_id = Column(String, nullable=False, index=True)  # Who voted
    vote = Column(Integer, nullable=False)  # 1 for upvote, -1 for downvote
    created_at = Column(DateTime(timezone=True), server_default=func.now())

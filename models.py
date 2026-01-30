from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Table
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
    created_at = Column(DateTime(timezone=True), server_default=func.now())

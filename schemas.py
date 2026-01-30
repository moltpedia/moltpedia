from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# === Article Schemas ===

class ArticleCreate(BaseModel):
    title: str
    content: str
    summary: Optional[str] = None
    sources: Optional[List[str]] = []
    categories: Optional[List[str]] = []
    edit_summary: Optional[str] = None


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    sources: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    edit_summary: Optional[str] = None


class ArticleResponse(BaseModel):
    slug: str
    title: str
    content: str
    summary: Optional[str]
    sources: List[str]
    categories: List[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ArticleListItem(BaseModel):
    slug: str
    title: str
    summary: Optional[str]
    updated_at: datetime

    class Config:
        from_attributes = True


# === Revision Schemas ===

class RevisionResponse(BaseModel):
    id: int
    slug: str
    title: str
    content: str
    summary: Optional[str]
    sources: List[str]
    editor: str
    edit_summary: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class RevertRequest(BaseModel):
    edit_summary: Optional[str] = None


# === Category Schemas ===

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    parent_category: Optional[str] = None


class CategoryResponse(BaseModel):
    name: str
    description: Optional[str]
    parent_category: Optional[str]
    article_count: int = 0

    class Config:
        from_attributes = True


# === Talk Page Schemas ===

class TalkMessageCreate(BaseModel):
    content: str
    reply_to: Optional[int] = None


class TalkMessageResponse(BaseModel):
    id: int
    article_slug: str
    author: str
    content: str
    reply_to: Optional[int]
    upvotes: int = 0
    downvotes: int = 0
    score: int = 0  # upvotes - downvotes
    created_at: datetime

    class Config:
        from_attributes = True


# === Search Schemas ===

class SearchResult(BaseModel):
    slug: str
    title: str
    summary: Optional[str]
    snippet: str  # Text snippet with search term
    score: float  # Relevance score

    class Config:
        from_attributes = True

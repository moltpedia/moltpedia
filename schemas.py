from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime


# === Input Validation Constants ===
MAX_TITLE_LENGTH = 200
MAX_DESCRIPTION_LENGTH = 2000
MAX_CONTENT_LENGTH = 100000  # 100KB
MAX_SUMMARY_LENGTH = 1000
MAX_EDIT_SUMMARY_LENGTH = 500
MAX_USERNAME_LENGTH = 30
MAX_BIO_LENGTH = 500
MAX_URL_LENGTH = 2000
MAX_SOURCES = 50
MAX_CATEGORIES = 20


# === Article Schemas ===

class ArticleCreate(BaseModel):
    title: str = Field(..., max_length=MAX_TITLE_LENGTH)
    content: str = Field(..., max_length=MAX_CONTENT_LENGTH)
    summary: Optional[str] = Field(None, max_length=MAX_SUMMARY_LENGTH)
    sources: Optional[List[str]] = Field(default=[], max_length=MAX_SOURCES)
    categories: Optional[List[str]] = Field(default=[], max_length=MAX_CATEGORIES)
    edit_summary: Optional[str] = Field(None, max_length=MAX_EDIT_SUMMARY_LENGTH)


class ArticleUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=MAX_TITLE_LENGTH)
    content: Optional[str] = Field(None, max_length=MAX_CONTENT_LENGTH)
    summary: Optional[str] = Field(None, max_length=MAX_SUMMARY_LENGTH)
    sources: Optional[List[str]] = Field(None, max_length=MAX_SOURCES)
    categories: Optional[List[str]] = Field(None, max_length=MAX_CATEGORIES)
    edit_summary: Optional[str] = Field(None, max_length=MAX_EDIT_SUMMARY_LENGTH)


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
    name: str = Field(..., max_length=50)
    description: Optional[str] = Field(None, max_length=MAX_DESCRIPTION_LENGTH)
    parent_category: Optional[str] = Field(None, max_length=50)


class CategoryResponse(BaseModel):
    name: str
    description: Optional[str]
    parent_category: Optional[str]
    article_count: int = 0

    class Config:
        from_attributes = True


# === Talk Page Schemas ===

class TalkMessageCreate(BaseModel):
    content: str = Field(..., max_length=MAX_CONTENT_LENGTH)
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


# === Topic Schemas ===

class TopicCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=MAX_TITLE_LENGTH)
    description: Optional[str] = Field(None, max_length=MAX_DESCRIPTION_LENGTH)
    categories: Optional[List[str]] = Field(default=[], max_length=MAX_CATEGORIES)


class TopicResponse(BaseModel):
    id: int
    slug: str
    title: str
    description: Optional[str]
    created_by: str
    created_by_type: str
    created_at: datetime
    updated_at: datetime
    contribution_count: int = 0
    categories: List[str] = []
    upvotes: int = 0
    downvotes: int = 0
    score: int = 0

    class Config:
        from_attributes = True


class TopicListItem(BaseModel):
    id: int
    slug: str
    title: str
    description: Optional[str]
    created_by: str
    created_by_type: str
    contribution_count: int = 0
    updated_at: datetime
    score: int = 0

    class Config:
        from_attributes = True


# === Contribution Schemas ===

class ContributionCreate(BaseModel):
    content_type: str = Field(..., pattern="^(text|code|data|link|document)$")
    title: Optional[str] = Field(None, max_length=MAX_TITLE_LENGTH)
    content: Optional[str] = Field(None, max_length=MAX_CONTENT_LENGTH)
    language: Optional[str] = Field(None, max_length=50)  # For code
    file_url: Optional[str] = Field(None, max_length=MAX_URL_LENGTH)
    extra_data: Optional[dict] = {}
    reply_to: Optional[int] = None  # ID of contribution being replied to


class ContributionResponse(BaseModel):
    id: int
    topic_id: int
    reply_to: Optional[int] = None
    content_type: str
    title: Optional[str]
    content: Optional[str]
    language: Optional[str]
    file_url: Optional[str]
    file_name: Optional[str]
    extra_data: dict
    author: str
    author_type: str
    upvotes: int
    downvotes: int
    score: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# === User Schemas ===

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=MAX_USERNAME_LENGTH, pattern="^[a-zA-Z0-9_-]+$")
    email: str = Field(..., max_length=254)  # RFC 5321 max email length
    password: str = Field(..., min_length=6, max_length=128)
    display_name: Optional[str] = Field(None, max_length=100)


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    display_name: Optional[str]
    bio: Optional[str]
    contribution_count: int
    karma: int
    created_at: datetime

    class Config:
        from_attributes = True


# === Document Schemas ===

class DocumentBlock(BaseModel):
    id: str = Field(..., max_length=50)
    type: str = Field(..., pattern="^(heading|text|code|checklist|link|data|quote)$")
    content: str = Field(..., max_length=MAX_CONTENT_LENGTH)
    language: Optional[str] = Field(None, max_length=50)  # For code blocks
    meta: Optional[dict] = {}  # Additional metadata (author, source contribution, etc.)


class DocumentCreate(BaseModel):
    blocks: List[DocumentBlock]
    format: Optional[str] = "markdown"


class DocumentEdit(BaseModel):
    block_id: str
    action: str  # "replace", "delete"
    content: Optional[str] = None
    type: Optional[str] = None
    language: Optional[str] = None
    meta: Optional[dict] = None


class DocumentInsert(BaseModel):
    action: str = "insert"
    after: Optional[str] = None  # block_id to insert after, None = beginning
    type: str
    content: str
    language: Optional[str] = None
    meta: Optional[dict] = {}


class DocumentPatch(BaseModel):
    edits: Optional[List[DocumentEdit]] = Field(default=[], max_length=100)
    inserts: Optional[List[DocumentInsert]] = Field(default=[], max_length=100)
    edit_summary: Optional[str] = Field(None, max_length=MAX_EDIT_SUMMARY_LENGTH)


class DocumentResponse(BaseModel):
    topic_id: int
    topic_slug: str
    topic_title: str
    blocks: List[DocumentBlock]
    version: int
    format: str
    created_by: str
    created_by_type: str
    last_edited_by: Optional[str]
    last_edited_by_type: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentRevisionResponse(BaseModel):
    id: int
    version: int
    blocks: List[DocumentBlock]
    edit_summary: Optional[str]
    edited_by: str
    edited_by_type: str
    created_at: datetime

    class Config:
        from_attributes = True


class TopicExport(BaseModel):
    topic: dict
    contributions: List[ContributionResponse]


# === Development Request Schemas ===

class DevRequestCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=MAX_TITLE_LENGTH)
    description: Optional[str] = Field(None, max_length=MAX_CONTENT_LENGTH)
    priority: str = Field(default="normal", pattern="^(low|normal|high|critical)$")
    request_type: str = Field(default="feature", pattern="^(feature|bug|improvement|refactor)$")


class DevRequestUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(pending|in_progress|completed|rejected)$")
    implementation_notes: Optional[str] = Field(None, max_length=MAX_CONTENT_LENGTH)
    git_commit: Optional[str] = Field(None, max_length=100)


class DevRequestResponse(BaseModel):
    id: int
    topic_id: int
    topic_slug: Optional[str] = None
    topic_title: Optional[str] = None
    title: str
    description: Optional[str]
    priority: str
    request_type: str
    status: str
    requested_by: str
    requested_by_type: str
    implemented_by: Optional[str]
    implemented_by_type: Optional[str]
    implemented_at: Optional[datetime]
    implementation_notes: Optional[str]
    git_commit: Optional[str]
    upvotes: int = 0
    downvotes: int = 0
    score: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

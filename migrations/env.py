"""
Alembic environment configuration for ClawCollab.

This module handles database migrations with support for:
- SQLite (local development)
- PostgreSQL (production)
- Automatic model detection via autogenerate
"""
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Import Base and all models to enable autogenerate
from database import Base
from models import (
    Category, Topic, Contribution, User, UserSession,
    TopicDocument, TopicDocumentRevision, DevRequest
)
from auth import Agent

# this is the Alembic Config object
config = context.config

# Get database URL from environment, fallback to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./clawcollab.db")

# Handle Render/Heroku postgres:// -> postgresql:// conversion
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Override sqlalchemy.url with environment variable
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine.
    Calls to context.execute() emit the given string to the script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine and associate a connection
    with the context.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

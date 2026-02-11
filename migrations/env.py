"""
Alembic Environment Configuration
===================================
Configures Alembic to work with Flask-SQLAlchemy and all Evident models.

All model modules must be imported here so that Alembic's autogenerate
can detect schema changes. Import order does not matter — SQLAlchemy
resolves relationships at metadata reflection time.
"""

import logging
from logging.config import fileConfig

from alembic import context
from flask import current_app

# Alembic Config object — provides access to alembic.ini values
config = context.config

# Set up Python logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

logger = logging.getLogger("alembic.env")


def get_engine():
    """Retrieve the SQLAlchemy engine from the Flask app."""
    try:
        return current_app.extensions["migrate"].db.engine
    except (TypeError, AttributeError):
        return current_app.extensions["migrate"].db.engine


def get_engine_url():
    """Return the database URL as a string (for offline migration)."""
    try:
        return get_engine().url.render_as_string(hide_password=False).replace("%", "%%")
    except AttributeError:
        return str(get_engine().url).replace("%", "%%")


# Target metadata — all models registered on db.Model.metadata
target_metadata = current_app.extensions["migrate"].db.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode — emits SQL to stdout
    without a live database connection.
    """
    url = get_engine_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode — connects to the database
    and applies DDL statements directly.
    """

    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, "autogenerate", False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info("No changes detected — skipping autogenerate revision.")

    connectable = get_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            process_revision_directives=process_revision_directives,
            render_as_batch=True,  # Required for SQLite ALTER TABLE support
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

import os, sys

import logging
from logging.config import fileConfig

from flask import current_app
from alembic import context
from sqlalchemy import engine_from_config, pool

# add the parent of the project folder so WritingAssistantBackend/ is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

print("Alembic is loading INI from:", config.config_file_name)

# Interpret the alembic .ini for logging.
fileConfig(context.config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
from WritingAssistantBackend.app import app
from WritingAssistantBackend.app import db
import WritingAssistantBackend.dbModel  # ensure the models are registered

# Tell alembic what the DB URL is from the Flask config file
context.config.set_main_option(
    'sqlalchemy.url',
    app.config['SQLALCHEMY_DATABASE_URI']
)
target_metadata = db.metadata
# right after you set target_metadata
print(">>> TARGET METADATA TABLES:", list(target_metadata.tables.keys()))


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = context.config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        render_as_batch=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        context.config.get_section(context.config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

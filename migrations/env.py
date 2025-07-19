from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

from src.config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER
from src.app.models import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

section = config.config_ini_section
config.set_section_option(section, "DB_USER", DB_USER)
config.set_section_option(section, "DB_NAME", DB_NAME)
config.set_section_option(section, "DB_PASS", DB_PASS)
config.set_section_option(section, "DB_PORT", DB_PORT)
config.set_section_option(section, "DB_HOST", DB_HOST)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

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


def do_run_migrations(connection):
    """
    Вспомогательная функция для запуска миграций.
    """
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Получаем URL из конфигурации Alembic
    # Убедитесь, что `sqlalchemy.url` в вашем alembic.ini указывает на asyncpg
    connectable = create_async_engine(config.get_main_option("sqlalchemy.url"))

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

# В самом конце файла, где решается, какой метод запускать (offline или online)
if context.is_offline_mode():
    run_migrations_offline()
else:
    # Запускаем нашу новую асинхронную функцию
    asyncio.run(run_migrations_online())

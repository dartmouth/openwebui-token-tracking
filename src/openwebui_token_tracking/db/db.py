from alembic.config import Config
from alembic import command

from sqlalchemy import create_engine

from pathlib import Path

from .credit_group import *
from .model_pricing import *
from .sponsored import *
from .token_usage import *
from .user import *


def init_db(database_url: str):
    engine = create_engine(database_url)
    return engine


def migrate_database(database_url: str):
    """Creates the tables required for token tracking in the specified database

    :param database_url: A database URL in `SQLAlchemy format
    <https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls>`_
    :type database_url: str
    """

    alembic_cfg = Config()
    alembic_cfg.set_main_option(
        "script_location", str(Path(__file__).parent.parent / "migrations/alembic")
    )
    alembic_cfg.set_main_option("sqlalchemy.url", database_url)

    command.stamp(alembic_cfg, "base")
    command.upgrade(alembic_cfg, "token_tracking@head")

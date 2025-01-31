from openwebui_token_tracking.models import ModelPricingSchema, DEFAULT_MODEL_PRICING
from alembic.config import Config
from alembic import command
from sqlalchemy.orm import declarative_base, Session
import sqlalchemy as sa

from pathlib import Path

Base = declarative_base()


class ModelPricing(Base):
    """SQLAlchemy model for the model pricing table"""

    __tablename__ = "model_pricing"
    id = sa.Column("id", sa.String(length=255), primary_key=True)
    name = sa.Column("name", sa.String(length=255))
    input_cost_credits = sa.Column("input_cost_credits", sa.Integer())
    per_input_tokens = sa.Column("per_input_tokens", sa.Integer())
    output_cost_credits = sa.Column("output_cost_credits", sa.Integer())
    per_output_tokens = sa.Column("per_output_tokens", sa.Integer())


def add_model_pricing(database_url: str, models: list[ModelPricingSchema] = None):
    """Add model pricing to the database

    :param database_url: A database URL in `SQLAlchemy format <https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls>`_
    :type database_url: str
    :param models: A list of model pricing descriptions. If None, uses :obj:`openwebui_token_tracking.models.DEFAULT_MODEL_PRICING`.
    :type models: list[ModelPricing], optional
    """
    if models is None:
        models = DEFAULT_MODEL_PRICING

    engine = sa.create_engine(database_url)
    with Session(engine) as session:
        for model in models:
            session.add(ModelPricing(**model.model_dump()))
        session.commit()


def migrate_database(database_url: str):
    """Creates the tables required for token tracking in the specified database

    :param database_url: A database URL in `SQLAlchemy format <https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls>`_
    :type database_url: str
    """

    alembic_cfg = Config()
    alembic_cfg.set_main_option(
        "script_location", str(Path(__file__).parent / "migrations/alembic")
    )
    alembic_cfg.set_main_option("sqlalchemy.url", database_url)
    command.upgrade(alembic_cfg, "head")

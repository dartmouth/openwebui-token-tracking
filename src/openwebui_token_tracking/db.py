from openwebui_token_tracking.models import ModelPricingSchema, DEFAULT_MODEL_PRICING
from alembic.config import Config
from alembic import command
from sqlalchemy.orm import declarative_base, Session, relationship
import sqlalchemy as sa

from pathlib import Path
import uuid

Base = declarative_base()


class CreditGroupUser(Base):
    """SQLAlchemy model for the credit group user table"""

    __tablename__ = "credit_group_user"
    credit_group_id = sa.Column(
        sa.UUID(as_uuid=True), sa.ForeignKey("credit_group.id"), primary_key=True
    )
    user_id = sa.Column(
        sa.String(length=255), sa.ForeignKey("user.id"), primary_key=True
    )

    credit_group = relationship("CreditGroup", back_populates="users")
    user = relationship("User", back_populates="credit_groups")


class CreditGroup(Base):
    """SQLAlchemy model for the credit group table"""

    __tablename__ = "credit_group"
    id = sa.Column(
        sa.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name = sa.Column(sa.String(length=255))
    max_credit = sa.Column(sa.Integer())

    users = relationship("CreditGroupUser", back_populates="credit_group")


class User(Base):
    """SQLAlchemy model for the user table.

    Mocks (parts of) the user table managed by Open WebUI
    and is only used for testing purposes.
    """

    __tablename__ = "user"
    id = sa.Column(sa.String(length=255), primary_key=True)
    name = sa.Column(sa.String(length=255))
    email = sa.Column(sa.String(length=255))

    credit_groups = relationship("CreditGroupUser", back_populates="user")


class ModelPricing(Base):
    """SQLAlchemy model for the model pricing table"""

    __tablename__ = "model_pricing"
    id = sa.Column(sa.String(length=255), primary_key=True)
    name = sa.Column(sa.String(length=255))
    input_cost_credits = sa.Column(sa.Integer())
    per_input_tokens = sa.Column(sa.Integer())
    output_cost_credits = sa.Column(sa.Integer())
    per_output_tokens = sa.Column(sa.Integer())


class TokenUsageLog(Base):
    """SQLAlchemy model for the token usage log table"""

    __tablename__ = "token_usage_log"
    log_date = sa.Column(
        "log_date",
        sa.DateTime(timezone=True),
        primary_key=True,
    )
    user_id = sa.Column(sa.String(length=255), primary_key=True)
    model_id = sa.Column(sa.String(length=255), primary_key=True)
    prompt_tokens = sa.Column(sa.Integer())
    response_tokens = sa.Column(sa.Integer())


def add_model_pricing(database_url: str, models: list[ModelPricingSchema] = None):
    """Add model pricing to the database

    :param database_url: A database URL in `SQLAlchemy format
    <https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls>`_
    :type database_url: str
    :param models: A list of model pricing descriptions. If None, uses
    :obj:`openwebui_token_tracking.models.DEFAULT_MODEL_PRICING`.
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

    :param database_url: A database URL in `SQLAlchemy format
    <https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls>`_
    :type database_url: str
    """

    alembic_cfg = Config()
    alembic_cfg.set_main_option(
        "script_location", str(Path(__file__).parent / "migrations/alembic")
    )
    alembic_cfg.set_main_option("sqlalchemy.url", database_url)

    command.stamp(alembic_cfg, "base")
    command.upgrade(alembic_cfg, "token_tracking@head")

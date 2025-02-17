from openwebui_token_tracking.models import ModelPricingSchema
from alembic.config import Config
from alembic import command
from sqlalchemy.orm import declarative_base, Session, relationship
import sqlalchemy as sa

from pathlib import Path
import uuid

Base = declarative_base()


class BaseSetting(Base):
    """SQLAlchemy model for the baseline settings table"""

    __tablename__ = "token_tracking_base_settings"

    setting_key = sa.Column(sa.String(length=255), primary_key=True)
    setting_value = sa.Column(sa.String(length=255))
    description = sa.Column(sa.String(length=255))


class CreditGroupUser(Base):
    """SQLAlchemy model for the credit group user table"""

    __tablename__ = "token_tracking_credit_group_user"
    credit_group_id = sa.Column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("token_tracking_credit_group.id"),
        primary_key=True,
    )
    user_id = sa.Column(
        sa.String(length=255), sa.ForeignKey("user.id"), primary_key=True
    )

    credit_group = relationship("CreditGroup", back_populates="users")
    user = relationship("User", back_populates="credit_groups")


class CreditGroup(Base):
    """SQLAlchemy model for the credit group table"""

    __tablename__ = "token_tracking_credit_group"
    id = sa.Column(
        sa.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name = sa.Column(sa.String(length=255))
    max_credit = sa.Column(sa.Integer())
    description = sa.Column(sa.String(length=255))

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

    __tablename__ = "token_tracking_model_pricing"
    provider = sa.Column(sa.String(length=255), primary_key=True)
    id = sa.Column(sa.String(length=255), primary_key=True)
    name = sa.Column(sa.String(length=255))
    input_cost_credits = sa.Column(sa.Integer())
    per_input_tokens = sa.Column(sa.Integer())
    output_cost_credits = sa.Column(sa.Integer())
    per_output_tokens = sa.Column(sa.Integer())


class TokenUsageLog(Base):
    """SQLAlchemy model for the token usage log table"""

    __tablename__ = "token_tracking_usage_log"
    log_date = sa.Column(
        "log_date",
        sa.DateTime(timezone=True),
        primary_key=True,
    )
    user_id = sa.Column(sa.String(length=255), primary_key=True)
    provider = sa.Column(sa.String(length=255), primary_key=True)
    model_id = sa.Column(sa.String(length=255), primary_key=True)
    prompt_tokens = sa.Column(sa.Integer())
    response_tokens = sa.Column(sa.Integer())


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


def init_base_settings(database_url: str, settings: list[dict[str, str]] = None):
    """Initializes the base settings table with default values

    :param database_url: A database URL in `SQLAlchemy format
    <https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls>`_
    :type database_url: str
    :param settings: A list of dictionaries of settings to use. If None, uses default settings.
    :type settings: list[dict[str, str]]
    """

    if settings is None:
        settings = [
            {
                "setting_key": "base_credit_allowance",
                "setting_value": "1000",
                "description": "Baseline credit allowance for all users.",
            }
        ]

    engine = sa.create_engine(database_url)
    with Session(engine) as session:
        for setting in settings:
            session.merge(BaseSetting(**setting))
        session.commit()


def list_model_pricing(database_url: str, provider: str = None) -> list[dict]:
    """Retrieve model pricing entries from the database, optionally filtered by provider

    :param database_url: A database URL in `SQLAlchemy format
        <https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls>`_
    :type database_url: str
    :param provider: Optional provider name to filter results
    :type provider: str, optional
    :return: List of dictionaries containing model pricing information
    :rtype: list[dict]
    """
    engine = sa.create_engine(database_url)
    with Session(engine) as session:
        query = session.query(ModelPricing)
        if provider:
            query = query.filter(ModelPricing.provider == provider)
        models = query.all()
        return [
            {
                "provider": model.provider,
                "id": model.id,
                "name": model.name,
                "input_cost_credits": model.input_cost_credits,
                "per_input_tokens": model.per_input_tokens,
                "output_cost_credits": model.output_cost_credits,
                "per_output_tokens": model.per_output_tokens,
            }
            for model in models
        ]


def get_model_pricing(
    database_url: str, model_id: str = None, provider: str = None
) -> list[dict]:
    """Retrieve specific model pricing entries from the database

    :param database_url: A database URL in `SQLAlchemy format
        <https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls>`_
    :type database_url: str
    :param model_id: Model ID to filter results
    :type model_id: str, optional
    :param provider: Provider name to filter results
    :type provider: str, optional
    :return: List of dictionaries containing model pricing information
    :rtype: list[dict]
    """
    engine = sa.create_engine(database_url)
    with Session(engine) as session:
        query = session.query(ModelPricing)

        if model_id:
            query = query.filter(ModelPricing.id == model_id)
        if provider:
            query = query.filter(ModelPricing.provider == provider)

        models = query.all()
        return [
            {
                "provider": model.provider,
                "id": model.id,
                "name": model.name,
                "input_cost_credits": model.input_cost_credits,
                "per_input_tokens": model.per_input_tokens,
                "output_cost_credits": model.output_cost_credits,
                "per_output_tokens": model.per_output_tokens,
            }
            for model in models
        ]


def add_model_pricing(database_url: str, model_pricing: list[ModelPricingSchema]):
    """Add model pricing to the database

    :param database_url: A database URL in `SQLAlchemy format
    <https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls>`_
    :type database_url: str
    :param models: A list of model pricing descriptions.
    :type models: list[ModelPricing], optional
    """

    engine = sa.create_engine(database_url)
    with Session(engine) as session:
        for model in model_pricing:
            session.add(ModelPricing(**model.model_dump()))
        session.commit()


def update_model_pricing(
    database_url: str, model_id: str, provider: str, updates: dict
) -> bool:
    """Update pricing information for a specific model

    :param database_url: A database URL in `SQLAlchemy format
        <https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls>`_
    :type database_url: str
    :param model_id: Model ID to update
    :type model_id: str
    :param provider: Provider name of the model
    :type provider: str
    :param updates: Dictionary containing the fields to update and their new values
    :type updates: dict
    :return: True if update was successful, False if model not found
    :rtype: bool
    """
    allowed_fields = {
        "name",
        "input_cost_credits",
        "per_input_tokens",
        "output_cost_credits",
        "per_output_tokens",
    }

    # Filter out any fields that aren't allowed to be updated
    filtered_updates = {k: v for k, v in updates.items() if k in allowed_fields}

    if not filtered_updates:
        return False

    engine = sa.create_engine(database_url)
    with Session(engine) as session:
        try:
            # Find the specific model
            model = (
                session.query(ModelPricing)
                .filter(ModelPricing.id == model_id, ModelPricing.provider == provider)
                .first()
            )

            if not model:
                return False
            # Update the model with the new values
            for key, value in filtered_updates.items():
                setattr(model, key, value)
            session.commit()
            return True

        except Exception as e:
            session.rollback()
            raise e


def upsert_model_pricing(
    database_url: str,
    provider: str,
    model_id: str,
    name: str,
    input_cost_credits: int,
    per_input_tokens: int,
    output_cost_credits: int,
    per_output_tokens: int,
) -> bool:
    """Create or update pricing information for a specific model

    :param database_url: A database URL in `SQLAlchemy format
        <https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls>`_
    :type database_url: str
    :param provider: Provider name of the model
    :type provider: str
    :param model_id: Model ID
    :type model_id: str
    :param name: Model name
    :type name: str
    :param input_cost_credits: Input cost in credits
    :type input_cost_credits: int
    :param per_input_tokens: Number of input tokens per credit
    :type per_input_tokens: int
    :param output_cost_credits: Output cost in credits
    :type output_cost_credits: int
    :param per_output_tokens: Number of output tokens per credit
    :type per_output_tokens: int
    :return: True if operation was successful
    :rtype: bool
    """
    engine = sa.create_engine(database_url)
    with Session(engine) as session:
        try:
            # Try to find existing record
            model = (
                session.query(ModelPricing)
                .filter(ModelPricing.id == model_id, ModelPricing.provider == provider)
                .first()
            )

            if model:
                # Update existing record
                model.name = name
                model.input_cost_credits = input_cost_credits
                model.per_input_tokens = per_input_tokens
                model.output_cost_credits = output_cost_credits
                model.per_output_tokens = per_output_tokens
            else:
                # Create new record
                model = ModelPricing(
                    provider=provider,
                    id=model_id,
                    name=name,
                    input_cost_credits=input_cost_credits,
                    per_input_tokens=per_input_tokens,
                    output_cost_credits=output_cost_credits,
                    per_output_tokens=per_output_tokens,
                )
                session.add(model)

            session.commit()
            return True

        except Exception as e:
            session.rollback()
            raise e


def delete_model_pricing(
    database_url: str, model_id: str, provider: str = None
) -> bool:
    """Delete pricing information for a specific model

    :param database_url: A database URL in `SQLAlchemy format
        <https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls>`_
    :type database_url: str
    :param model_id: Model ID to delete
    :type model_id: str
    :param provider: Provider name of the model
    :type provider: str, optional
    :return: True if deletion was successful, False if model not found
    :rtype: bool
    """
    engine = sa.create_engine(database_url)
    with Session(engine) as session:
        try:
            query = session.query(ModelPricing).filter(ModelPricing.id == model_id)
            if provider:
                query.filter(ModelPricing.provider == provider)

            result = query.delete()

            session.commit()
            # Return True if a row was deleted, False otherwise
            return result > 0

        except Exception as e:
            session.rollback()
            raise e


def find_user(
    database_url: str,
    user_id: str = None,
    name: str = None,
    email: str = None,
) -> User | None:
    """Find a user based on any combination of id, name, and email.

    :param db: SQLAlchemy database session
    :type db: Session
    :param user_id: User ID to search for
    :type user_id: Optional[str]
    :param name: User name to search for
    :type name: Optional[str]
    :param email: User email to search for
    :type email: Optional[str]
    :return: User object if found, None otherwise
    :rtype: Optional[User]

    :example:

    Find by id::

        user = find_user(db, user_id="123")

    Find by name and email::

        user = find_user(db, name="John Doe", email="john@example.com")

    Find by email only::

        user = find_user(db, email="john@example.com")
    """
    engine = sa.create_engine(database_url)

    conditions = []

    if user_id is not None:
        conditions.append(User.id == user_id)
    if name is not None:
        conditions.append(User.name == name)
    if email is not None:
        conditions.append(User.email == email)

    if not conditions:
        return None

    with Session(engine) as session:
        query = session.query(User).filter(sa.and_(*conditions))

    return query.first()

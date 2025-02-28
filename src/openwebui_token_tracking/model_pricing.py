from openwebui_token_tracking.db import init_db, ModelPricing
from openwebui_token_tracking.models import ModelPricingSchema
from sqlalchemy.orm import Session


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
    engine = init_db(database_url)
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
    engine = init_db(database_url)
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


def add_model_pricing(database_url: str, model_pricing: list[ModelPricingSchema]):
    """Add model pricing to the database

    :param database_url: A database URL in `SQLAlchemy format <https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls>`_
    :type database_url: str
    :param models: A list of model pricing descriptions.
    :type models: list[ModelPricing], optional
    """

    engine = init_db(database_url)
    with Session(engine) as session:
        for model in model_pricing:
            session.add(ModelPricing(**model.model_dump()))
        session.commit()


def update_model_pricing(
    database_url: str, model_id: str, provider: str, updates: dict
) -> bool:
    """Update pricing information for a specific model

    :param database_url: A database URL in `SQLAlchemy format <https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls>`_
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

    engine = init_db(database_url)
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
    engine = init_db(database_url)
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
    engine = init_db(database_url)
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

import os
from typing import Iterable

from sqlalchemy.orm import Session

from openwebui_token_tracking.db import (
    init_db,
    SponsoredAllowance,
    SponsoredAllowanceBaseModels,
)


def create_sponsored_allowance(
    database_url: str,
    sponsor_id: str,
    name: str,
    models: Iterable[str],
    total_credit_limit: int,
    daily_credit_limit: int,
):
    if database_url is None:
        database_url = os.environ["DATABASE_URL"]

    engine = init_db(database_url)
    with Session(engine) as session:
        sponsored_allowance = SponsoredAllowance(
            sponsor_id=sponsor_id,
            name=name,
            total_credit_limit=total_credit_limit,
            daily_credit_limit=daily_credit_limit,
        )

        # Create the base model associations
        for base_model_id in models:
            association = SponsoredAllowanceBaseModels(
                sponsored_allowance=sponsored_allowance, base_model_id=base_model_id
            )
            sponsored_allowance.base_models.append(association)

        session.add(sponsored_allowance)
        session.commit()


def delete_sponsored_allowance(
    database_url: str = None,
    allowance_id: str = None,
    name: str = None,
):
    """Delete a sponsored allowance by ID or name.

    :param database_url: The database connection URL. If None, uses the DATABASE_URL environment variable.
    :type database_url: str, optional
    :param allowance_id: The ID of the sponsored allowance to delete.
    :type allowance_id: str, optional
    :param name: The name of the sponsored allowance to delete.
    :type name: str, optional
    :raises ValueError: If neither allowance_id nor name is provided.
    :raises ValueError: If no sponsored allowance is found with the given ID or name.
    """
    if allowance_id is None and name is None:
        raise ValueError("Either allowance_id or name must be provided")

    if database_url is None:
        database_url = os.environ["DATABASE_URL"]

    engine = init_db(database_url)
    with Session(engine) as session:
        query = session.query(SponsoredAllowance)

        if allowance_id is not None:
            query = query.filter(SponsoredAllowance.id == allowance_id)
        else:
            query = query.filter(SponsoredAllowance.name == name)

        sponsored_allowance = query.first()

        if sponsored_allowance is None:
            raise ValueError(
                f"No sponsored allowance found with the given {'ID' if allowance_id else 'name'}"
            )

        session.query(SponsoredAllowanceBaseModels).filter(
            SponsoredAllowanceBaseModels.sponsored_allowance_id
            == sponsored_allowance.id
        ).delete(synchronize_session=False)

        session.delete(sponsored_allowance)
        session.commit()


def get_sponsored_allowance(
    database_url: str = None,
    name: str = None,
    id: str = None,
):
    """Get a single sponsored allowance by name or ID.

    :param database_url: The database connection URL. If None, uses the DATABASE_URL environment variable.
    :type database_url: str, optional
    :param name: The name of the allowance to retrieve.
    :type name: str, optional
    :param id: The ID of the allowance to retrieve.
    :type id: str, optional
    :return: The sponsored allowance as a dictionary.
    :rtype: dict
    :raises KeyError: If no allowance is found with the given name or ID.
    """
    if database_url is None:
        database_url = os.environ["DATABASE_URL"]

    if name is None and id is None:
        raise ValueError("Either name or id must be provided")

    engine = init_db(database_url)
    with Session(engine) as session:
        query = session.query(SponsoredAllowance)

        if name is not None:
            query = query.filter(SponsoredAllowance.name == name)
        if id is not None:
            query = query.filter(SponsoredAllowance.id == id)

        sponsored_allowance = query.first()

        if sponsored_allowance is None:
            raise KeyError(f"Could not find sponsored allowance: {id=}, {name=}")

        return {
            "id": str(sponsored_allowance.id),
            "name": sponsored_allowance.name,
            "sponsor_id": sponsored_allowance.sponsor_id,
            "total_credit_limit": sponsored_allowance.total_credit_limit,
            "daily_credit_limit": sponsored_allowance.daily_credit_limit,
            "base_models": sponsored_allowance.base_models,
        }


def get_sponsored_allowances(
    database_url: str = None,
    sponsor_id: str = None,
):
    """Get all sponsored allowances, optionally filtered by sponsor ID.

    :param database_url: The database connection URL. If None, uses the DATABASE_URL environment variable.
    :type database_url: str, optional
    :param sponsor_id: Filter allowances by sponsor ID.
    :type sponsor_id: str, optional
    :return: List of sponsored allowances, each as a dictionary.
    :rtype: list[dict]
    """
    if database_url is None:
        database_url = os.environ["DATABASE_URL"]

    engine = init_db(database_url)
    with Session(engine) as session:
        query = session.query(SponsoredAllowance)

        if sponsor_id is not None:
            query = query.filter(SponsoredAllowance.sponsor_id == sponsor_id)

        # Order by name for consistent results
        query = query.order_by(SponsoredAllowance.name)

        sponsored_allowances = query.all()

        result = []
        for allowance in sponsored_allowances:
            result.append(
                {
                    "id": str(allowance.id),
                    "name": allowance.name,
                    "sponsor_id": allowance.sponsor_id,
                    "total_credit_limit": allowance.total_credit_limit,
                    "daily_credit_limit": allowance.daily_credit_limit,
                    "base_models": allowance.base_models,
                }
            )

        return result


def update_sponsored_allowance(
    database_url: str = None,
    allowance_id: str = None,
    name: str = None,
    new_name: str = None,
    sponsor_id: str = None,
    models: Iterable[str] = None,
    total_credit_limit: int = None,
    daily_credit_limit: int = None,
):
    """Update a sponsored allowance by ID or name.

    :param database_url: The database connection URL. If None, uses the DATABASE_URL environment variable.
    :type database_url: str, optional
    :param allowance_id: The ID of the sponsored allowance to update.
    :type allowance_id: str, optional
    :param name: The name of the sponsored allowance to update.
    :type name: str, optional
    :param new_name: The new name for the sponsored allowance.
    :type new_name: str, optional
    :param sponsor_id: The new sponsor ID for the sponsored allowance.
    :type sponsor_id: str, optional
    :param models: The new list of base model IDs.
    :type models: Iterable[str], optional
    :param total_credit_limit: The new total credit limit.
    :type total_credit_limit: int, optional
    :param daily_credit_limit: The new daily credit limit.
    :type daily_credit_limit: int, optional
    :raises ValueError: If neither allowance_id nor name is provided.
    :raises ValueError: If no sponsored allowance is found with the given ID or name.
    """
    if allowance_id is None and name is None:
        raise ValueError("Either allowance_id or name must be provided")

    if database_url is None:
        database_url = os.environ["DATABASE_URL"]

    engine = init_db(database_url)
    with Session(engine) as session:
        query = session.query(SponsoredAllowance)
        if allowance_id is not None:
            query = query.filter(SponsoredAllowance.id == allowance_id)
        else:
            query = query.filter(SponsoredAllowance.name == name)

        sponsored_allowance = query.first()
        if sponsored_allowance is None:
            raise ValueError(
                f"No sponsored allowance found with the given {'ID' if allowance_id else 'name'}"
            )

        if new_name is not None:
            sponsored_allowance.name = new_name
        if sponsor_id is not None:
            sponsored_allowance.sponsor_id = sponsor_id
        if total_credit_limit is not None:
            sponsored_allowance.total_credit_limit = total_credit_limit
        if daily_credit_limit is not None:
            sponsored_allowance.daily_credit_limit = daily_credit_limit

        if models is not None:
            # Delete existing model associations
            session.query(SponsoredAllowanceBaseModels).filter(
                SponsoredAllowanceBaseModels.sponsored_allowance_id
                == sponsored_allowance.id
            ).delete(synchronize_session=False)

            # Create new model associations
            for base_model_id in models:
                association = SponsoredAllowanceBaseModels(
                    sponsored_allowance=sponsored_allowance, base_model_id=base_model_id
                )
                sponsored_allowance.base_models.append(association)

        session.commit()

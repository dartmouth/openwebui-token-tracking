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

        session.delete(sponsored_allowance)
        session.commit()


def get_sponsored_allowances(
    database_url: str = None,
    name: str = None,
    id: str = None,
    sponsor_id: str = None,
):
    """Get all sponsored allowances matching the provided filters.

    :param database_url: The database connection URL. If None, uses the DATABASE_URL environment variable.
    :type database_url: str, optional
    :param name: Filter by allowance name.
    :type name: str, optional
    :param id: Filter by allowance ID.
    :type id: str, optional
    :param sponsor_id: Filter by sponsor ID.
    :type sponsor_id: str, optional
    :return: List of matching sponsored allowances, each as a dictionary.
    :rtype: list[dict]
    """
    if database_url is None:
        database_url = os.environ["DATABASE_URL"]

    engine = init_db(database_url)
    with Session(engine) as session:
        query = session.query(SponsoredAllowance)

        if name is not None:
            query = query.filter(SponsoredAllowance.name == name)
        if id is not None:
            query = query.filter(SponsoredAllowance.id == id)
        if sponsor_id is not None:
            query = query.filter(SponsoredAllowance.sponsor_id == sponsor_id)

        sponsored_allowances = query.all()

        if not sponsored_allowances:
            return []

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

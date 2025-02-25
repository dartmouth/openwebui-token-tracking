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


def get_sponsored_allowance(
    database_url: str,
    name: str = None,
    id: str = None,
):
    if database_url is None:
        database_url = os.environ["DATABASE_URL"]

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
            "total_credit_limit": sponsored_allowance.total_credit_limit,
            "daily_credit_limit": sponsored_allowance.daily_credit_limit,
            "base_models": sponsored_allowance.base_models,
        }

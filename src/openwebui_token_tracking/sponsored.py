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

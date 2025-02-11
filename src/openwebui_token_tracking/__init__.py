from openwebui_token_tracking.tracking import TokenTracker
from openwebui_token_tracking.models import ModelPricingSchema

import argparse


# Entry points
def migrate_database():
    import openwebui_token_tracking.db

    parser = argparse.ArgumentParser(
        description=(
            "Migrate the database to include the tables required for token tracking."
        )
    )
    parser.add_argument("database_url", help="URL of the database in SQLAlchemy format")

    args = parser.parse_args()

    return openwebui_token_tracking.db.migrate_database(database_url=args.database_url)


def add_model_pricing():
    import openwebui_token_tracking.db

    parser = argparse.ArgumentParser(description=("Add model pricing to the database."))
    parser.add_argument("database_url", help="URL of the database in SQLAlchemy format")
    parser.add_argument(
        "-m",
        "--models",
        help="A JSON string describing the model pricing with the following schema: \n"
        + str(ModelPricingSchema.model_json_schema()["properties"]),
        default=None,
    )

    args = parser.parse_args()

    return openwebui_token_tracking.db.add_model_pricing(
        database_url=args.database_url, models=args.models
    )


def init_base_settings():
    import openwebui_token_tracking.db

    parser = argparse.ArgumentParser(
        description=(
            "Migrate the database to include the tables required for token tracking."
        )
    )
    parser.add_argument("database_url", help="URL of the database in SQLAlchemy format")

    args = parser.parse_args()

    return openwebui_token_tracking.db.init_base_settings(
        database_url=args.database_url
    )


__all__ = [
    "TokenTracker",
]

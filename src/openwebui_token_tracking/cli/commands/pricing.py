import click
import json
from openwebui_token_tracking import models, ModelPricingSchema
import openwebui_token_tracking.db


@click.group(name="pricing")
def pricing():
    """Manage pricing structures."""
    pass


@pricing.command(name="add")
@click.argument("database_url")
@click.option(
    "-m",
    "--model-pricing",
    default=json.dumps(
        [m.model_dump(mode="json") for m in models.DEFAULT_MODEL_PRICING]
    ),
    help="A JSON string describing the model pricing with the following schema: \n"
    + str(models.ModelPricingSchema.model_json_schema()["properties"]),
)
def add_pricing(database_url: str, model_pricing: str):
    """Add model pricing to the database at DATABASE_URL.

    DATABASE_URL is expected to be in SQLAlchemy format.

    If --mode-pricing is not provided, uses
    openwebui_token_tracking.models.DEFAULT_MODEL_PRICING.
    """
    model_pricing = json.loads(model_pricing)

    return openwebui_token_tracking.db.add_model_pricing(
        database_url=database_url,
        model_pricing=[ModelPricingSchema(**m) for m in model_pricing],
    )

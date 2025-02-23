import click
from click.testing import CliRunner

import json
import os

from .commands import database, pricing, credit_group, settings, sponsored, user
from openwebui_token_tracking.models import ModelPricingSchema
from openwebui_token_tracking.model_pricing import upsert_model_pricing


@click.group()
def cli():
    """OWUI Token Tracking CLI tool."""
    pass


# Register commands
cli.add_command(database.database)
cli.add_command(pricing.pricing)
cli.add_command(credit_group.credit_group)
cli.add_command(settings.settings)
cli.add_command(sponsored.sponsored)
cli.add_command(user.user)


@cli.command()
@click.option("--database-url", envvar="DATABASE_URL")
@click.option(
    "--json",
    "json_file",
    type=click.File("r"),
    help="Read multiple models from a JSON file",
)
def init(database_url: str, json_file: str):
    """Initialize the token tracking tool with default settings"""
    runner = CliRunner()

    click.echo("Starting initialization...")

    click.echo("Running database migration...")
    result = runner.invoke(cli, ["database", "migrate"])
    if result.exit_code != 0:
        click.echo("Database migration failed!")
        return result.exit_code

    click.echo("Adding pricing...")
    if not json_file:
        json_file = open(
            f"{os.path.dirname(os.path.realpath(__file__))}/../resources/models.json"
        )

    model_pricing_data = json.load(json_file)
    model_pricing = [ModelPricingSchema(**m) for m in model_pricing_data]

    for model in model_pricing:
        upsert_model_pricing(
            database_url=database_url,
            model_id=model.id,
            **model.model_dump(exclude=["id"]),
        )

    click.echo("Initializing settings...")
    result = runner.invoke(cli, ["settings", "init"])
    if result.exit_code != 0:
        click.echo("Settings initialization failed!")
        return result.exit_code

    click.echo("Initialization completed successfully!")


if __name__ == "__main__":
    cli()

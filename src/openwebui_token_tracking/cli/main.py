import click
from click.testing import CliRunner
from .commands import database, pricing, credit_group, settings, user
import os

@click.group()
def cli():
    """OWUI Token Tracking CLI tool."""
    pass


# Register commands
cli.add_command(database.database)
cli.add_command(pricing.pricing)
cli.add_command(credit_group.credit_group)
cli.add_command(settings.settings)
cli.add_command(user.user)


@cli.command()
def init():
    """Initialize the token tracking tool with default settings"""
    runner = CliRunner()

    click.echo("Starting initialization...")

    click.echo("Running database migration...")
    result = runner.invoke(cli, ["database", "migrate"])
    if result.exit_code != 0:
        click.echo("Database migration failed!")
        return result.exit_code

    click.echo("Adding pricing...")
    print(os.path.realpath(__file__))
    result = runner.invoke(
        cli,
        [
            "pricing",
            "upsert",
            "--json",
            f"{os.path.dirname(os.path.realpath(__file__))}/../resources/models.json",
        ],
    )
    if result.exit_code != 0:
        click.echo("Adding pricing failed!")
        return result.exit_code

    click.echo("Initializing settings...")
    result = runner.invoke(cli, ["settings", "init"])
    if result.exit_code != 0:
        click.echo("Settings initialization failed!")
        return result.exit_code

    click.echo("Initialization completed successfully!")


if __name__ == "__main__":
    cli()

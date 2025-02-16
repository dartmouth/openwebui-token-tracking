import click
from .commands import database, pricing, credit_group, settings, user


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

if __name__ == "__main__":
    cli()

import click
from .commands import database, pricing


@click.group()
def cli():
    """OWUI Token Tracking CLI tool."""
    pass


# Register commands
cli.add_command(database.database)
cli.add_command(pricing.pricing)
# cli.add_command(cmd2.command_2)

if __name__ == "__main__":
    cli()

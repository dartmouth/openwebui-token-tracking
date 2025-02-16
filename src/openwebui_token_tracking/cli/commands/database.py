import click
import openwebui_token_tracking.db


@click.group(name="database")
def database():
    """Database management commands."""
    pass


@database.command()
@click.argument("database_url", envvar="DATABASE_URL")
def migrate(database_url: str):
    """Migrate the database at DATABASE_URL to include the tables required for token tracking.
    Expects DATABASE_URL to be in SQLAlchemy format.
    """

    return openwebui_token_tracking.db.migrate_database(database_url=database_url)

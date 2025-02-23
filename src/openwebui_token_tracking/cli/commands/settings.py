import click
from openwebui_token_tracking.settings import init_base_settings


@click.group(name="settings")
def settings():
    """Settings management commands."""
    pass


@settings.command(name="init")
@click.option("--database-url", envvar="DATABASE_URL")
def init(
    database_url: str,
):
    """Initialize base settings in the database at DATABASE-URL.

    DATABASE-URL is expected to be in SQLAlchemy format.
    """

    return init_base_settings(database_url=database_url)

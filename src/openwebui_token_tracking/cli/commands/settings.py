import click
from openwebui_token_tracking.settings import init_base_settings


@click.group(name="settings")
def settings():
    """Settings management commands."""
    pass


@settings.command(name="init")
@click.option("--database-url", envvar="DATABASE_URL")
@click.option(
    "--setting",
    type=(str, str, str),
    multiple=True,
    default=[
        (
            "base_credit_allowance",
            "1000",
            "Baseline credit allowance for all users.",
        )
    ],
)
def init(
    database_url: str,
    setting: list[tuple[str, str, str]],
):
    """Initialize base settings in the database at DATABASE-URL.

    DATABASE-URL is expected to be in SQLAlchemy format.
    """

    settings_dict = [
        {
            "setting_key": s[0],
            "setting_value": s[1],
            "description": s[2],
        }
        for s in setting
    ]

    return init_base_settings(database_url=database_url, settings=settings_dict)

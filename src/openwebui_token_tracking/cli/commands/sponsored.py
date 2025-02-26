import click
import openwebui_token_tracking.sponsored as sp


@click.group(name="sponsored")
def sponsored():
    """Manage sponsored structures."""
    pass


@sponsored.command(name="create")
@click.option("--database-url", envvar="DATABASE_URL")
@click.option(
    "--sponsor-id",
    help="ID of the allowance sponsor",
    required=True,
)
@click.option(
    "--name",
    help="Human-readable name for the sponsored allowance",
    required=True,
)
@click.option(
    "--model",
    "-m",
    type=str,
    help="ID of a model for which the allowance should apply",
    multiple=True,
    required=True,
)
@click.option(
    "--total-limit",
    "-t",
    type=int,
    help="Total credit limit across all users and models",
    required=True,
)
@click.option(
    "--daily-limit",
    "-d",
    type=int,
    help="Daily credit limit for each user",
)
def create_sponsored_allowance(
    database_url: str,
    sponsor_id: str,
    name: str,
    model: list[str],
    total_limit: int,
    daily_limit: int | None,
):

    return sp.create_sponsored_allowance(
        database_url=database_url,
        sponsor_id=sponsor_id,
        name=name,
        models=model,
        total_credit_limit=total_limit,
        daily_credit_limit=daily_limit,
    )


@sponsored.command(name="delete")
@click.option("--database-url", envvar="DATABASE_URL")
@click.option("--id", help="ID of the sponsored allowance to delete")
@click.option("--name", help="Name of the sponsored allowance to delete")
def delete_sponsored(database_url: str, id: str = None, name: str = None):
    """Delete a sponsored allowance from the database.

    Either --id or --name must be provided to identify the allowance to delete.
    DATABASE-URL is expected to be in SQLAlchemy format.
    """
    if id is None and name is None:
        click.echo("Error: Either --id or --name must be provided", err=True)
        return

    try:
        sp.delete_sponsored_allowance(
            database_url=database_url, allowance_id=id, name=name
        )
        click.echo(f"Successfully deleted sponsored allowance: {id or name}")
    except ValueError as e:
        click.echo(f"Error: {str(e)}", err=True)


@sponsored.command(name="list")
@click.option("--database-url", envvar="DATABASE_URL")
def list_sponsored(database_url: str):
    """List all sponsored allowances in the database.

    DATABASE-URL is expected to be in SQLAlchemy format.
    """
    models = sp.get_sponsored_allowances(database_url=database_url)
    for model in models:
        click.echo(model)

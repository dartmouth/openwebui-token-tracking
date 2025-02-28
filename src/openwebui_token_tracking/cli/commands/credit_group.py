import click
import openwebui_token_tracking.credit_groups

import json

@click.group(name="credit-group")
def credit_group():
    """Manage credit groups."""
    pass


@credit_group.command()
@click.argument("name")
@click.argument("allowance")
@click.argument("description")
@click.argument("database-url", envvar="DATABASE_URL")
def create(name: str, allowance: int, description: str, database_url: str):
    """Create a new credit group NAME with the credit allowance ALLOWANCE in the
    database at DATABASE_URL.
    """
    try:
        result = openwebui_token_tracking.credit_groups.create_credit_group(
            credit_group_name=name,
            credit_allowance=allowance,
            description=description,
            database_url=database_url,
        )
        click.echo(f"Successfully created credit group '{name}'")
        return result
    except Exception as e:
        click.echo(f"Error creating credit group: {str(e)}", err=True)
        raise click.Abort()


@credit_group.command()
@click.argument("name")
@click.argument("database-url", envvar="DATABASE_URL")
def get(name: str, database_url: str):
    """Get details of credit group NAME from the database at DATABASE_URL."""
    try:
        result = openwebui_token_tracking.credit_groups.get_credit_group(
            credit_group_name=name, database_url=database_url
        )
        click.echo(f"Credit group '{name}' details: {result}")
        return result
    except Exception as e:
        click.echo(f"Error reading credit group: {str(e)}", err=True)
        raise click.Abort()


@credit_group.command()
@click.argument("database-url", envvar="DATABASE_URL")
def list(database_url: str):
    """List all credit groups from the database at DATABASE_URL."""
    try:
        result = openwebui_token_tracking.credit_groups.list_credit_groups(
            database_url=database_url
        )
        click.echo("Credit groups:")
        for group in result:
            click.echo(f"{group}")
        return result
    except Exception as e:
        click.echo(f"Error listing credit groups: {str(e)}", err=True)
        raise click.Abort()


@credit_group.command()
@click.argument("name")
@click.argument("allowance", type=int)
@click.argument("database-url", envvar="DATABASE_URL")
def update(name: str, allowance: int, database_url: str):
    """Update credit group NAME with new ALLOWANCE in the database at DATABASE_URL."""
    try:
        result = openwebui_token_tracking.credit_groups.update_credit_group(
            credit_group_name=name,
            credit_allowance=allowance,
            database_url=database_url,
        )
        click.echo(f"Successfully updated credit group '{name}'")
        return result
    except Exception as e:
        click.echo(f"Error updating credit group: {str(e)}", err=True)
        raise click.Abort()


@credit_group.command()
@click.argument("name")
@click.argument("database-url", envvar="DATABASE_URL")
@click.option(
    "--force",
    is_flag=True,
    help="force credit group deletion even if it has users",
)
def delete(name: str, database_url: str, force: bool = False):
    """Delete credit group NAME from the database at DATABASE_URL."""
    try:
        result = openwebui_token_tracking.credit_groups.delete_credit_group(
            credit_group_name=name,
            database_url=database_url,
            force=force,
        )
        click.echo(f"Successfully deleted credit group '{name}'")
        return result
    except Exception as e:
        click.echo(f"Error deleting credit group: {str(e)}", err=True)
        raise click.Abort()


@credit_group.command()
@click.argument("user-id")
@click.argument("credit-group")
@click.argument("database-url", envvar="DATABASE_URL")
def add_user(user_id: str, credit_group: str, database_url: str):
    """Add a user with USER-ID to the credit group CREDIT-GROUP in the
    database at DATABASE-URL.
    """

    try:
        result = openwebui_token_tracking.credit_groups.add_user(
            user_id=user_id, credit_group_name=credit_group, database_url=database_url
        )
        click.echo(
            f"Successfully added user '{user_id}' to credit group '{credit_group}'"
        )
        return result
    except Exception as e:
        click.echo(f"Error adding user to credit group: {str(e)}", err=True)
        raise click.Abort()


@credit_group.command()
@click.argument("user-id")
@click.argument("credit-group")
@click.argument("database-url", envvar="DATABASE_URL")
def remove_user(user_id: str, credit_group: str, database_url: str):
    """Remove a user with USER-ID from the credit group CREDIT-GROUP in the
    database at DATABASE_URL.
    """
    try:
        result = openwebui_token_tracking.credit_groups.remove_user(
            user_id=user_id, credit_group_name=credit_group, database_url=database_url
        )
        click.echo(
            f"Successfully removed user '{user_id}' from credit group '{credit_group}'"
        )
        return result
    except Exception as e:
        click.echo(f"Error removing user from credit group: {str(e)}", err=True)
        raise click.Abort()


@credit_group.command()
@click.argument("name")
@click.argument("database-url", envvar="DATABASE_URL")
def list_users(name: str, database_url: str):
    """List all users in credit group NAME from the database at DATABASE_URL."""
    try:
        result = openwebui_token_tracking.credit_groups.list_users(
            credit_group_name=name, database_url=database_url
        )
        click.echo(json.dumps(result))
        return result
    except KeyError as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"Error listing users in credit group: {str(e)}", err=True)
        raise click.Abort()

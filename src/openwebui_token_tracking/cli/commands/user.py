import click
import openwebui_token_tracking.user

import os
import json

@click.group(name="user")
def user():
    """User management commands."""
    pass


@user.command()
@click.option("--id", "user_id", help="User ID to search for")
@click.option("--name", help="User name to search for")
@click.option("--email", help="User email to search for")
@click.argument("database-url", envvar="DATABASE_URL")
def find(database_url: str, user_id: str | None, name: str | None, email: str | None):
    """
    Find a user in the database at DATABASE_URL using any combination of ID, name,
    and email.
    """
    try:
        result = openwebui_token_tracking.user.find_user(
            database_url=database_url,
            user_id=user_id,
            name=name,
            email=email,
        )
        if result:
            click.echo(
                json.dumps(
                    openwebui_token_tracking.user.serialize_user(result),
                )
            )
            return os.EX_OK
        else:
            click.echo("No user found matching the specified criteria")
            return os.EX_NOUSER
    except Exception as e:
        click.echo(f"Error finding user: {str(e)}", err=True)
        raise click.Abort()

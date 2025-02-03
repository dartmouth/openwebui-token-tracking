import click
import openwebui_token_tracking.credit_groups


@click.group(name="credit-group")
def credit_group():
    """Manage credit groups."""
    pass


@credit_group.command()
@click.argument("name")
@click.argument("allowance")
@click.argument("database_url")
def create(name: str, allowance: int, database_url: str):
    """Create a new credit group NAME with the credit allowance ALLOWANCE in the
    database at DATABASE_URL.
    """
    return openwebui_token_tracking.credit_groups.create_credit_group(
        credit_group_name=name, credit_allowance=allowance, database_url=database_url
    )


@credit_group.command()
@click.argument("user_id")
@click.argument("credit_group")
@click.argument("database_url")
def add_user(user_id: str, credit_group: str, database_url: str):
    """Add a user with USER_ID to the credit group CREDIT_GROUP in the
    database at DATABASE_URL.
    """

    return openwebui_token_tracking.credit_groups.add_user(
        user_id=user_id, credit_group_name=credit_group, database_url=database_url
    )

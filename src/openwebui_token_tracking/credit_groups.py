import sqlalchemy as db
from sqlalchemy.orm import Session

from openwebui_token_tracking.db import init_db
from openwebui_token_tracking.db.credit_group import CreditGroup, CreditGroupUser
from openwebui_token_tracking.db.user import User
from openwebui_token_tracking.user import serialize_user

import os


def create_credit_group(
    credit_group_name: str,
    credit_allowance: int,
    description: str,
    database_url: str = None,
):
    """Creates a credit group in the database.

    :param credit_group_name: Name of the credit group to be created.
    :type credit_group_name: str
    :param credit_allowance: Maximum credit allowance granted to members of this group.
    :type credit_allowance: int
    :param description: Description e of the credit group to be created.
    :type description: str
    :param database_url: URL of the database. If None, uses env variable ``DATABASE_URL``
    :type database_url: str, optional
    :raises KeyError: Raised if a credit group of this name already exists.
    """

    if database_url is None:
        database_url = os.environ["DATABASE_URL"]
    engine = init_db(database_url)

    with Session(engine) as session:
        # Make sure credit group of that name does not already exist
        credit_group = (
            session.query(CreditGroup).filter_by(name=credit_group_name).first()
        )
        if not credit_group:
            session.add(
                CreditGroup(
                    name=credit_group_name,
                    max_credit=credit_allowance,
                    description=description,
                )
            )
            session.commit()
        else:
            raise KeyError(
                f"A credit group of that name already exists: '{credit_group.name}'"
            )


def get_credit_group(credit_group_name: str, database_url: str = None) -> dict:
    """Retrieves a credit group from the database by its name and returns it
    as a dictionary.

    :param credit_group_name: Name of the credit group to retrieve
    :type credit_group_name: str
    :param database_url: URL of the database. If None, uses env variable
        ``DATABASE_URL``
    :type database_url: str, optional
    :return: Dictionary containing the credit group properties (id, name, max_credit,
        description)
    :rtype: dict
    :raises KeyError: Raised if the credit group of that name could not be found
    """
    if database_url is None:
        database_url = os.environ["DATABASE_URL"]

    engine = init_db(database_url)
    with Session(engine) as session:
        credit_group = (
            session.query(CreditGroup).filter_by(name=credit_group_name).first()
        )
        if not credit_group:
            raise KeyError(f"Could not find credit group: {credit_group_name}")

        return {
            "id": str(credit_group.id),  # Convert UUID to string
            "name": credit_group.name,
            "max_credit": credit_group.max_credit,
            "description": credit_group.description,
        }


def list_credit_groups(database_url: str = None) -> list[dict]:
    """Lists all credit groups in the database in a readable format.

    :param database_url: URL of the database. If None, uses env variable ``DATABASE_URL``
    :type database_url: str, optional
    :return: List of dictionaries containing formatted credit group information
    :rtype: list[dict]
    """
    if database_url is None:
        database_url = os.environ["DATABASE_URL"]
    engine = init_db(database_url)

    with Session(engine) as session:
        credit_groups = session.query(CreditGroup).all()
        formatted_groups = []
        for credit_group in credit_groups:
            # Count number of users in the group
            user_count = (
                session.query(CreditGroupUser)
                .filter_by(credit_group_id=credit_group.id)
                .count()
            )

            formatted_groups.append(
                {
                    "id": str(credit_group.id),  # Convert UUID to string
                    "name": credit_group.name,
                    "description": credit_group.description,
                    "max_credit": credit_group.max_credit,
                    "user_count": user_count,
                }
            )

        return formatted_groups


def update_credit_group(
    credit_group_name: str,
    new_credit_allowance: int = None,
    new_description: str = None,
    new_name: str = None,
    database_url: str = None,
):
    """Updates an existing credit group in the database.

    :param credit_group_name: Name of the credit group to update
    :type credit_group_name: str
    :param new_credit_allowance: New maximum credit allowance for the group
    :type new_credit_allowance: int, optional
    :param new_description: New description for the group
    :type new_description: str, optional
    :param new_name: New name for the group
    :type new_name: str, optional
    :param database_url: URL of the database. If None, uses env variable ``DATABASE_URL``
    :type database_url: str, optional
    :raises KeyError: Raised if the credit group of that name could not be found
    :raises ValueError: Raised if no updates are specified
    """
    if all(
        param is None for param in [new_credit_allowance, new_description, new_name]
    ):
        raise ValueError("At least one update parameter must be specified")

    if database_url is None:
        database_url = os.environ["DATABASE_URL"]

    engine = init_db(database_url)
    with Session(engine) as session:
        credit_group = (
            session.query(CreditGroup).filter_by(name=credit_group_name).first()
        )
        if not credit_group:
            raise KeyError(f"Could not find credit group: {credit_group_name}")

        # Update fields if new values are provided
        if new_credit_allowance is not None:
            credit_group.max_credit = new_credit_allowance
        if new_description is not None:
            credit_group.description = new_description
        if new_name is not None:
            # Check if new name already exists
            existing = session.query(CreditGroup).filter_by(name=new_name).first()
            if existing and existing.id != credit_group.id:
                raise KeyError(f"A credit group with name '{new_name}' already exists")
            credit_group.name = new_name

        session.commit()


def upsert_credit_group(
    credit_group_name: str,
    credit_allowance: int,
    description: str,
    database_url: str = None,
) -> bool:
    """Creates a new credit group or updates an existing one if it already exists.

    :param credit_group_name: Name of the credit group
    :type credit_group_name: str
    :param credit_allowance: Maximum credit allowance for the group
    :type credit_allowance: int
    :param description: Description of the credit group
    :type description: str
    :param database_url: URL of the database. If None, uses env variable ``DATABASE_URL``
    :type database_url: str, optional
    :return: True if a new group was created, False if an existing group was updated
    :rtype: bool
    """
    if database_url is None:
        database_url = os.environ["DATABASE_URL"]

    engine = init_db(database_url)
    with Session(engine) as session:
        credit_group = (
            session.query(CreditGroup).filter_by(name=credit_group_name).first()
        )

        if credit_group:
            # Update existing group
            credit_group.max_credit = credit_allowance
            credit_group.description = description
            session.commit()
            return False
        else:
            # Create new group
            session.add(
                CreditGroup(
                    name=credit_group_name,
                    max_credit=credit_allowance,
                    description=description,
                )
            )
            session.commit()
            return True


def delete_credit_group(
    credit_group_name: str, database_url: str = None, force: bool = False
):
    """Deletes a credit group from the database.

    :param credit_group_name: Name of the credit group to delete
    :type credit_group_name: str
    :param database_url: URL of the database. If None, uses env variable
        ``DATABASE_URL``
    :type database_url: str, optional
    :param force: If True, deletes group even if it has users. If False, raises error
        if group has users
    :type force: bool, optional
    :raises KeyError: Raised if the credit group of that name could not be found
    :raises ValueError: Raised if the group has users and force=False
    """
    if database_url is None:
        database_url = os.environ["DATABASE_URL"]
    engine = init_db(database_url)

    with Session(engine) as session:
        # Find the credit group
        credit_group = (
            session.query(CreditGroup).filter_by(name=credit_group_name).first()
        )
        if not credit_group:
            raise KeyError(f"Could not find credit group: {credit_group_name}")

        # Check if the group has any users
        user_count = (
            session.query(CreditGroupUser)
            .filter_by(credit_group_id=credit_group.id)
            .count()
        )

        if user_count > 0 and not force:
            raise ValueError(
                f"Credit group '{credit_group_name}' has {user_count} users. "
                "Use force=True to delete anyway."
            )

        # Delete all user associations if force=True
        if force:
            session.query(CreditGroupUser).filter_by(
                credit_group_id=credit_group.id
            ).delete()

        # Delete the credit group
        session.delete(credit_group)
        session.commit()


def add_user(user_id: str, credit_group_name: str, database_url: str = None):
    """Add the specified user to the credit group

    :param credit_group_name: Name of the credit group to add the user to
    :type credit_group_name: str
    :param user_id: ID of the user
    :type user_id: str
    :param database_url: URL of the database. If None, uses env variable
        ``DATABASE_URL``
    :type database_url: str, optional
    :raises KeyError: Raised if the credit group of that name could not be found
    """
    if database_url is None:
        database_url = os.environ["DATABASE_URL"]
    engine = init_db(database_url)

    with Session(engine) as session:
        credit_group = (
            session.query(CreditGroup).filter_by(name=credit_group_name).first()
        )
        if not credit_group:
            raise KeyError(f"Could not find credit group: {credit_group=}")

        # Add user to credit group
        user = session.query(User).filter_by(id=user_id).first()
        session.merge(CreditGroupUser(credit_group_id=credit_group.id, user_id=user.id))
        session.commit()


def remove_user(user_id: str, credit_group_name: str, database_url: str = None):
    """Removes a user from the specified credit group.

    :param user_id: ID of the user to remove
    :type user_id: str
    :param credit_group_name: Name of the credit group to remove the user from
    :type credit_group_name: str
    :param database_url: URL of the database. If None, uses env variable
        ``DATABASE_URL``
    :type database_url: str, optional
    :raises KeyError: Raised if the credit group of that name could not be found
    :raises ValueError: Raised if the user is not in the specified credit group
    """
    if database_url is None:
        database_url = os.environ["DATABASE_URL"]
    engine = init_db(database_url)

    with Session(engine) as session:
        # Find the credit group
        credit_group = (
            session.query(CreditGroup).filter_by(name=credit_group_name).first()
        )
        if not credit_group:
            raise KeyError(f"Could not find credit group: {credit_group_name}")

        # Find the user
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            raise KeyError(f"Could not find user with ID: {user_id}")

        # Find and delete the association
        association = (
            session.query(CreditGroupUser)
            .filter_by(credit_group_id=credit_group.id, user_id=user.id)
            .first()
        )

        if not association:
            raise ValueError(
                f"User {user_id} is not a member of credit group '{credit_group_name}'"
            )

        session.delete(association)
        session.commit()


def list_users(credit_group_name: str, database_url: str = None) -> list[dict]:
    """Lists all users in a specific credit group.

    :param credit_group_name: Name of the credit group to list users from
    :type credit_group_name: str
    :param database_url: URL of the database. If None, uses env variable ``DATABASE_URL``
    :type database_url: str, optional
    :return: List of dictionaries containing user information
    :rtype: list[dict]
    :raises KeyError: Raised if the credit group of that name could not be found
    """
    if database_url is None:
        database_url = os.environ["DATABASE_URL"]

    engine = init_db(database_url)
    with Session(engine) as session:
        # Find the credit group
        credit_group = (
            session.query(CreditGroup).filter_by(name=credit_group_name).first()
        )
        if not credit_group:
            raise KeyError(f"Could not find credit group: {credit_group_name}")

        # Query users in the group
        users = (
            session.query(User)
            .join(CreditGroupUser)
            .filter(CreditGroupUser.credit_group_id == credit_group.id)
            .all()
        )

        # Format user information
        user_list = []
        for user in users:
            user_list.append(
                serialize_user(user),
            )

        return user_list

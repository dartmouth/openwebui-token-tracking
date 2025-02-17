import sqlalchemy as db
from sqlalchemy.orm import Session

from openwebui_token_tracking.db import CreditGroup, CreditGroupUser, User

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
    engine = db.create_engine(database_url)

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
    """Retrieves a credit group from the database by its name and returns it as a
    dictionary.

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

    engine = db.create_engine(database_url)
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
    engine = db.create_engine(database_url)

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
    engine = db.create_engine(database_url)

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
    :param database_url: URL of the database. If None, uses env variable ``DATABASE_URL``
    :type database_url: str, optional
    :raises KeyError: Raised if the credit group of that name could not be found
    """
    if database_url is None:
        database_url = os.environ["DATABASE_URL"]
    engine = db.create_engine(database_url)

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

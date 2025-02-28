import sqlalchemy as sa
from sqlalchemy.orm import Session

from openwebui_token_tracking.db import init_db, User


def find_user(
    database_url: str,
    user_id: str = None,
    name: str = None,
    email: str = None,
) -> User | None:
    """Find a user based on any combination of id, name, and email.

    :param db: SQLAlchemy database session
    :type db: Session
    :param user_id: User ID to search for
    :type user_id: Optional[str]
    :param name: User name to search for
    :type name: Optional[str]
    :param email: User email to search for
    :type email: Optional[str]
    :return: User object if found, None otherwise
    :rtype: Optional[User]

    :example:

    Find by id::

        user = find_user(db, user_id="123")

    Find by name and email::

        user = find_user(db, name="John Doe", email="john@example.com")

    Find by email only::

        user = find_user(db, email="john@example.com")
    """
    engine = init_db(database_url)

    conditions = []

    if user_id is not None:
        conditions.append(User.id == user_id)
    if name is not None:
        conditions.append(User.name == name)
    if email is not None:
        conditions.append(User.email == email)

    if not conditions:
        return None

    with Session(engine) as session:
        query = session.query(User).filter(sa.and_(*conditions))

    return query.first()


def serialize_user(user):
    credit_groups_data = []
    for credit_group_user in user.credit_groups:
        credit_group = credit_group_user.credit_group
        credit_groups_data.append(
            {
                "id": str(credit_group.id),
                "name": credit_group.name,
                "max_credit": credit_group.max_credit,
                "description": credit_group.description,
            }
        )

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "credit_groups": credit_groups_data,
    }

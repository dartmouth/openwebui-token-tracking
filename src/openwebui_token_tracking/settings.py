from sqlalchemy.orm import Session

from openwebui_token_tracking.db import init_db, BaseSetting


def init_base_settings(database_url: str, settings: list[dict[str, str]] = None):
    """Initializes the base settings table with default values

    :param database_url: A database URL in `SQLAlchemy format
        <https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls>`_
    :type database_url: str
    :param settings: A list of dictionaries of settings to use. If None, uses default settings.
    :type settings: list[dict[str, str]]
    """

    if settings is None:
        settings = [
            {
                "setting_key": "base_credit_allowance",
                "setting_value": "1000",
                "description": "Baseline credit allowance for all users.",
            }
        ]

    engine = init_db(database_url)
    with Session(engine) as session:
        for setting in settings:
            session.merge(BaseSetting(**setting))
        session.commit()

from openwebui_token_tracking.tracking import TokenTracker


def init_base_settings():
    import openwebui_token_tracking.db
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Migrate the database to include the tables required for token tracking."
        )
    )
    parser.add_argument("database_url", help="URL of the database in SQLAlchemy format")

    args = parser.parse_args()

    return openwebui_token_tracking.db.init_base_settings(
        database_url=args.database_url
    )


__all__ = [
    "TokenTracker",
]

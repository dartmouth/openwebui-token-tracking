from openwebui_token_tracking.tracking import TokenTracker

import argparse


# Entry point
def migrate_database():
    import openwebui_token_tracking.db

    parser = argparse.ArgumentParser(
        description=(
            "Migrate the database to include the tables required for token tracking."
        )
    )
    parser.add_argument("database_url", help="URL of the database in SQLAlchemy format")

    args = parser.parse_args()

    return openwebui_token_tracking.db.migrate_database(database_url=args.database_url)


__all__ = [
    "TokenTracker",
]
